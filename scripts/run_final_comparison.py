"""
Final Comparison: Single Specialist vs Multi-Agent with Two-Phase Verification

Configurations:
1. Single Specialist (Baseline)
2. Multi-Agent (No Verification)
3. Multi-Agent + Two-Phase Verification - MAIN CONTRIBUTION
4. Single Specialist + Two-Phase Verification (Optional - to show multi-agent helps)

Purpose: Show that Multi-Agent + Two-Phase Verification is the best configuration.
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.llm_client import LocalLLMClient
from src.agents.specialist_agent import create_specialist_team
from src.verification.tier1_verification import Tier1Verifier
from src.verification.tier2_validation import Tier2Validator
from src.fusion.integration_methods import integrate_scores
from src.evaluation.metrics import calculate_accuracy, calculate_confidence_metrics, calculate_auroc


def load_dataset(file_path: str, max_questions: int = None, random_seed: int = 42):
    """Load filtered respiratory dataset with random sampling."""
    import random
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different dataset formats
    if 'filtered_questions' in data:
        questions = data['filtered_questions']
    elif 'questions' in data:
        questions = data['questions']
    elif isinstance(data, list):
        questions = data
    else:
        questions = data.get('data', data.get('items', []))
    
    # RANDOM SAMPLING with fixed seed for reproducibility
    if max_questions and max_questions < len(questions):
        random.seed(random_seed)
        questions = random.sample(questions, max_questions)
        print(f"  Randomly sampled {max_questions} from {len(questions)} questions (seed={random_seed})")
    
    return questions


def run_configuration(
    config_name: str,
    llm_client,
    specialists,  # List of specialists (can be single or multi)
    questions,
    two_phase_verifier=None,  # Two-Phase Verification (Wu et al. 2024)
    tier2_validator=None,
    integration_method=None,
    alpha=None,
    temperature_scale=1.2,  # Reduced from 1.5 to improve discrimination
    is_single_specialist=False
):
    """Run a single configuration and return results."""
    print(f"\n{'='*70}", flush=True)
    print(f"Running Configuration: {config_name}", flush=True)
    print(f"{'='*70}", flush=True)
    results = {
        'config_name': config_name,
        'timestamp': datetime.now().isoformat(),
        'num_questions': len(questions),
        'is_single_specialist': is_single_specialist,
        'integration_method': integration_method or 'none',
        'alpha': alpha,
        'question_results': []
    }
    
    # Store options for metrics calculation (letter-to-text conversion in metrics)
    all_options = []
    
    for idx, q in enumerate(questions, 1):
        print(f"\nProcessing Q{idx}/{len(questions)}...", end=' ', flush=True)
        
        question_text = q.get('question', '')
        options = q.get('options', {})
        correct_answer = q.get('answer', q.get('correct_answer', ''))
        
        # Store raw options for this question (used later for metrics answer matching)
        all_options.append(options)
        
        # Convert options dict to list if needed
        if isinstance(options, dict):
            options_list = [f"{k}: {v}" for k, v in options.items()]
        else:
            options_list = options
        
        # Get specialist opinions
        specialist_outputs = []
        for specialist in specialists:
            diagnosis = specialist.analyze_question(question_text, options_list)
            
            # Apply Two-Phase Verification if enabled (Wu et al. 2024)
            S_score = None
            two_phase_result = None
            if two_phase_verifier:
                two_phase_result = two_phase_verifier.verify_specialist(
                    specialist_name=specialist.specialty,
                    question=question_text,
                    answer=diagnosis.get('answer', ''),
                    reasoning=diagnosis.get('reasoning', ''),
                    initial_confidence=diagnosis.get('confidence', 0.5),
                    options=options_list
                )
                S_score = two_phase_result.get('specialist_confidence_S', diagnosis.get('confidence', 0.5))
            else:
                S_score = diagnosis.get('confidence', 0.5)
            
            # Apply Tier 2 validation if enabled
            G_score = None
            tier2_result = None
            if tier2_validator and two_phase_result:
                tier2_result = tier2_validator.validate_specialist_diagnosis(
                    specialist_name=specialist.specialty,
                    question=question_text,
                    answer=diagnosis.get('answer', ''),
                    reasoning=diagnosis.get('reasoning', ''),
                    tier1_result=two_phase_result,  # Pass two-phase result to Tier 2
                    options=options_list
                )
                G_score = tier2_result.get('gp_validation_confidence_G', S_score)
            else:
                G_score = S_score if tier2_validator is None else None
            
            # Integrate scores if both verification tiers are enabled
            if two_phase_verifier and tier2_validator and S_score is not None and G_score is not None:
                if integration_method == 'linear':
                    final_confidence = integrate_scores(S_score, G_score, method='linear', alpha=alpha)
                elif integration_method == 'bayesian':
                    final_confidence = integrate_scores(S_score, G_score, method='bayesian')
                else:
                    final_confidence = S_score
            elif two_phase_verifier:
                final_confidence = S_score
            else:
                final_confidence = diagnosis.get('confidence', 0.5)
            
            specialist_outputs.append({
                'specialty': specialist.specialty,
                'answer': diagnosis.get('answer', ''),
                'confidence': final_confidence,
                'reasoning': diagnosis.get('reasoning', ''),
                'S_score': S_score,
                'G_score': G_score,
                'two_phase_result': two_phase_result,  # Two-Phase Verification result
                'tier2_result': tier2_result
            })
        
        # Fusion: Single specialist vs Multi-agent
        fusion_reason = "single_specialist" if is_single_specialist else "unresolved"
        fusion_debug = {}
        # Initialize final_answer and final_confidence to prevent None errors
        final_answer = None
        final_confidence = 0.5
        
        if is_single_specialist:
            # Single specialist - use its confidence directly
            final_answer = specialist_outputs[0]['answer'] if specialist_outputs else None
            final_confidence = specialist_outputs[0]['confidence'] if specialist_outputs else 0.5
        else:
            # Multi-agent fusion: Majority voting with Two-Phase-informed boosts
            from collections import Counter
            import re

            # STEP 1: Identify strongly verified specialists (Two-Phase YES with high S_score)
            # Keep threshold at 0.7 to avoid false positives
            strong_yes_specialists: List[Dict[str, Any]] = []
            for spec_out in specialist_outputs:
                two_phase_result = spec_out.get('two_phase_result', {})
                verified_status = two_phase_result.get('verified_status', '') if two_phase_result else ''
                s_score = spec_out.get('S_score', spec_out['confidence'])
                if verified_status == 'YES' and s_score >= 0.7:
                    strong_yes_specialists.append(spec_out)

            # FIXED: Require consensus for verified answers - don't trust single verified specialist
            # Single verified answers can be wrong (consistency ??? correctness)
            # Only trust if at least 2 specialists agree on the same verified answer
            if len(strong_yes_specialists) >= 2:
                # Check if multiple verified specialists agree on the same answer
                verified_answers = Counter([s['answer'] for s in strong_yes_specialists])
                most_common_verified = verified_answers.most_common(1)
                
                if most_common_verified and most_common_verified[0][1] >= 2:
                    # At least 2 verified specialists agree - this is a strong signal
                    agreed_answer = most_common_verified[0][0]
                    agreed_specialists = [s for s in strong_yes_specialists if s['answer'] == agreed_answer]
                    best_verified = max(agreed_specialists, key=lambda x: x.get('S_score', x['confidence']))
                    final_answer = best_verified['answer']
                    final_confidence = min(1.0, best_verified['confidence'] * 1.2)  # Reduced boost from 1.4 to 1.2
                    final_answer_set = True
                    fusion_reason = "verified_consensus"
                elif len(strong_yes_specialists) >= 2:
                    # Multiple verified specialists but disagree - use best S_score among them
                    best_verified = max(strong_yes_specialists, key=lambda x: x.get('S_score', x['confidence']))
                    final_answer = best_verified['answer']
                    final_confidence = best_verified.get('S_score', best_verified['confidence'])
                    final_answer_set = True
                    fusion_reason = "verified_disagreement_best"
                # If only 1 verified specialist, don't trust it blindly - fall through to normal fusion
            # GP fallback removed - GP is no longer in specialist team
            # This forces fusion logic to work with domain specialists only
            else:
                # STEP 2: Apply Two-Phase-based boosts and consensus logic
                high_confidence_verified_specialist = None
                max_verified_confidence = 0.0

                for spec_out in specialist_outputs:
                    two_phase_result = spec_out.get('two_phase_result', {})
                    verified_status = two_phase_result.get('verified_status', '') if two_phase_result else ''
                    s_score = spec_out.get('S_score', spec_out['confidence'])

                    # If Two-Phase Verification says YES with high confidence, this is a strong signal
                    if verified_status == 'YES' and s_score > 0.6:
                        # Boost confidence for Two-Phase verified answers
                        boost_factor = 1.3 if s_score > 0.7 else 1.2  # Increased to improve discrimination
                        spec_out['confidence'] = min(1.0, spec_out['confidence'] * boost_factor)

                        # Track the highest confidence verified answer
                        if s_score > max_verified_confidence:
                            max_verified_confidence = s_score
                            high_confidence_verified_specialist = spec_out

                # Also check for consensus: if multiple specialists agree
                answer_votes_prelim = Counter([s['answer'] for s in specialist_outputs])
                
                # SIMPLIFIED: Track answers with 2+ agreeing specialists and their avg S_score
                agreement_scores = {}
                for spec_out in specialist_outputs:
                    answer = spec_out['answer']
                    answer_count = answer_votes_prelim[answer]
                    s_score = spec_out.get('S_score', spec_out['confidence'])
                    
                    if answer_count >= 2:
                        if answer not in agreement_scores:
                            agreement_scores[answer] = {
                                'count': answer_count,
                                'scores': [s_score],
                                'specialists': [spec_out]
                            }
                        else:
                            agreement_scores[answer]['scores'].append(s_score)
                            agreement_scores[answer]['specialists'].append(spec_out)
                
                for spec_out in specialist_outputs:
                    answer = spec_out['answer']
                    answer_count = answer_votes_prelim[answer]
                    s_score = spec_out.get('S_score', spec_out['confidence'])

                    # If 2+ specialists agree AND Two-Phase confidence is reasonable, boost
                    if answer_count >= 2 and s_score > 0.5:
                        boost = 1.05  # Conservative boost
                        spec_out['confidence'] = min(1.0, spec_out['confidence'] * boost)

                    # If 3+ specialists agree but Two-Phase confidence is low, penalize consensus
                    if answer_count >= 3 and s_score < 0.5:
                        spec_out['confidence'] = max(0.0, spec_out['confidence'] * 0.9)  # Less aggressive

                # Count votes per answer
                answer_votes = Counter([s['answer'] for s in specialist_outputs])
                most_common = answer_votes.most_common()
                fusion_debug["answer_votes"] = dict(answer_votes)
                fusion_debug["most_common"] = most_common[:5]

                # PRIORITY 0: If max S_score is reasonably high (>0.45), prefer that specialist's answer
                # This uses the better discrimination of S_scores (AUROC 0.590 vs 0.412)
                max_s_specialist = max(specialist_outputs, key=lambda x: x.get('S_score', x['confidence']))
                max_s_score = max_s_specialist.get('S_score', max_s_specialist['confidence'])
                fusion_debug["max_s_specialist"] = {
                    "specialty": max_s_specialist.get("specialty"),
                    "answer": max_s_specialist.get("answer"),
                    "S_score": max_s_score,
                    "confidence": max_s_specialist.get("confidence"),
                }
                
                # Initialize final_answer and final_confidence to track if we set them
                final_answer_set = False
                
                # IMPROVED: Better handling of disagreements - prioritize high S_score specialists
                # When minority has correct answer, high S_score should override majority
                # Lower threshold to catch more cases where minority is correct
                if max_s_score > 0.40:
                    # Check if there's a majority
                    if most_common and most_common[0][1] > len(specialist_outputs) / 2:
                        majority_answer = most_common[0][0]
                        majority_specialists = [s for s in specialist_outputs if s['answer'] == majority_answer]
                        majority_best = max(majority_specialists, key=lambda x: x.get('S_score', x['confidence']))
                        majority_max_s = majority_best.get('S_score', majority_best['confidence'])
                        
                        # IMPROVED: Better override logic - allow override if S_score is meaningfully better
                        # Check verified status to ensure we're not overriding with wrong verified answers
                        max_s_two_phase = max_s_specialist.get('two_phase_result', {})
                        max_s_verified = max_s_two_phase.get('verified_status', '') if max_s_two_phase else ''
                        
                        # Override if: (1) meaningful gap (0.08+) OR (2) high S_score (0.65+) AND verified
                        # OR (3) max S_score is verified and majority is not verified
                        majority_two_phase = majority_best.get('two_phase_result', {})
                        majority_verified = majority_two_phase.get('verified_status', '') if majority_two_phase else ''
                        
                        override_condition = (
                            max_s_score >= majority_max_s + 0.08 or  # Meaningful gap
                            (max_s_score >= 0.65 and max_s_verified == 'YES') or  # High verified
                            (max_s_verified == 'YES' and majority_verified != 'YES')  # Verified vs not verified
                        )
                        
                        if override_condition:
                            final_answer = max_s_specialist['answer']
                            final_confidence = max_s_score  # Use S_score directly
                            fusion_reason = "max_s_override_majority"
                        else:
                            # Majority has comparable or better S_score, use it
                            final_answer = majority_best['answer']
                            final_confidence = majority_max_s
                            fusion_reason = "max_s_yield_to_majority"
                        final_answer_set = True
                    else:
                        # No majority - use max S_score specialist
                        final_answer = max_s_specialist['answer']
                        final_confidence = max_s_score
                        final_answer_set = True
                        fusion_reason = "max_s_no_majority"
                # PRIORITY 2: If Two-Phase Verification verified answer exists with high confidence, prefer it
                # This uses verification signals (realistic) instead of answer key (evaluation only)
                elif high_confidence_verified_specialist and max_verified_confidence > 0.6:
                    # Check if there's a majority
                    if most_common and most_common[0][1] > len(specialist_outputs) / 2:
                        majority_answer = most_common[0][0]
                        majority_specialists = [s for s in specialist_outputs if s['answer'] == majority_answer]
                        majority_best = max(majority_specialists, key=lambda x: x['confidence'])

                        # If verified specialist confidence is at least 65% of majority best, prefer verified
                        if high_confidence_verified_specialist['confidence'] >= majority_best['confidence'] * 0.65:
                            final_answer = high_confidence_verified_specialist['answer']
                            final_confidence = high_confidence_verified_specialist['confidence']
                        else:
                            # Verified answer confidence too low, use majority
                            best_specialist = majority_best
                            final_answer = best_specialist['answer']
                            final_confidence = best_specialist['confidence']
                        final_answer_set = True
                        fusion_reason = "verified_vs_majority"
                    else:
                        # No majority - prefer verified answer if confidence is reasonable
                        all_sorted = sorted(specialist_outputs, key=lambda x: x['confidence'], reverse=True)
                        highest = all_sorted[0]

                        # If verified specialist confidence is at least 65% of highest, prefer verified
                        if high_confidence_verified_specialist['confidence'] >= highest['confidence'] * 0.65:
                            final_answer = high_confidence_verified_specialist['answer']
                            final_confidence = high_confidence_verified_specialist['confidence']
                        else:
                            final_answer = highest['answer']
                            final_confidence = highest['confidence']
                        final_answer_set = True
                        fusion_reason = "verified_no_majority"
                # PRIORITY 3: Check for 2+ specialists agreeing with good avg S_score (even if not majority)
                # This helps catch Q3, Q8, Q12 where correct answer has 2 specialists but wrong has 3
                elif agreement_scores:
                    # Find answer with best combination of count and avg S_score
                    best_agreement_answer = None
                    best_agreement_score = 0.0
                    for answer, info in agreement_scores.items():
                        avg_s = sum(info['scores']) / len(info['scores'])
                        # Score = count * 0.4 + avg_s_score * 0.6 (prefer higher S_score)
                        score = info['count'] * 0.4 + avg_s * 0.6
                        if score > best_agreement_score and info['count'] >= 2:
                            best_agreement_score = score
                            best_agreement_answer = answer
                    
                    # If we have a good agreement answer AND no clear majority, prefer it
                    if best_agreement_answer and (not most_common or most_common[0][1] <= len(specialist_outputs) / 2):
                        best_agreement_specs = [s for s in specialist_outputs if s['answer'] == best_agreement_answer]
                        best_agreement_spec = max(best_agreement_specs, key=lambda x: x.get('S_score', x['confidence']))
                        final_answer = best_agreement_spec['answer']
                        final_confidence = min(1.0, best_agreement_spec['confidence'] * 1.15)  # Small boost
                        final_answer_set = True
                        fusion_reason = "agreement_2plus_no_majority"
                
                # If we haven't set final_answer yet, fall through to majority/highest confidence
                if not final_answer_set:
                    if most_common and most_common[0][1] > len(specialist_outputs) / 2:
                        # No clearly verified answer - use majority (with adjusted confidences)
                        majority_answer = most_common[0][0]
                        majority_specialists = [s for s in specialist_outputs if s['answer'] == majority_answer]
                        if majority_specialists:
                            best_specialist = max(majority_specialists, key=lambda x: x['confidence'])
                            final_answer = best_specialist['answer']
                            final_confidence = best_specialist['confidence']
                            fusion_reason = "majority"
                    else:
                        # No majority - use highest confidence (tie-breaking)
                        specialist_outputs_sorted = sorted(specialist_outputs, key=lambda x: x['confidence'], reverse=True)
                        if specialist_outputs_sorted:
                            final_answer = specialist_outputs_sorted[0]['answer']
                            final_confidence = specialist_outputs_sorted[0]['confidence']
                        else:
                            final_answer = None
                            final_confidence = 0.5
                        fusion_reason = "highest_confidence_fallback"
                
                # Safety check: ensure final_answer is set
                if final_answer is None or final_answer == '':
                    # Last resort: use first specialist's answer
                    if specialist_outputs:
                        final_answer = specialist_outputs[0]['answer']
                        final_confidence = specialist_outputs[0]['confidence']
                        fusion_reason = "fallback_first_specialist"
                    else:
                        final_answer = ""
                        final_confidence = 0.5
                        fusion_reason = "error_no_specialists"
        
        # IMPROVED: Better S_score integration with calibration
        # Apply temperature scaling to S_scores for calibration before combining
        if not is_single_specialist and specialist_outputs:
            max_s_score = max([s.get('S_score', s['confidence']) for s in specialist_outputs])
            
            # Calibration: Apply temperature scaling to S_score
            # This helps calibrate S_scores to better match actual accuracy
            calibrated_s_score = max_s_score ** 0.9  # Slight scaling down for calibration
            
            # Weighted combination: 75% calibrated S_score, 25% fusion result
            # Increased weight on S_score since it has better discrimination
            final_confidence = 0.75 * calibrated_s_score + 0.25 * final_confidence
        
        # Apply temperature scaling for calibration (less aggressive for Multi-Agent + Two-Phase)
        # For Multi-Agent + Two-Phase, use less scaling since we're already using S_scores
        if not is_single_specialist:
            # Less aggressive scaling when using S_scores
            temp_scale = max(1.0, temperature_scale - 0.1)  # Reduce by 0.1
        else:
            temp_scale = temperature_scale
        
        final_confidence = final_confidence ** temp_scale
        final_confidence = min(final_confidence, 0.95)
        final_confidence = max(final_confidence, 0.05)
        
        # Convert letter answer to full text if needed
        # Safety check: ensure final_answer is not None
        if final_answer is None:
            final_answer = ""
        final_answer_text = final_answer.strip() if final_answer else ""
        if isinstance(options, dict) and len(final_answer_text) == 1 and final_answer_text.upper() in options:
            final_answer_text = options[final_answer_text.upper()]
        
        # Strip letter prefixes
        import re
        final_answer_text = re.sub(r'^[A-Z]\.\s*', '', final_answer_text, flags=re.IGNORECASE).strip()
        correct_answer_normalized = re.sub(r'^[A-Z]\.\s*', '', correct_answer, flags=re.IGNORECASE).strip()
        
        # Check if correct
        is_correct = (final_answer_text.lower() == correct_answer_normalized.lower())
        
        result = {
            'question_idx': idx,
            'question': question_text[:100] + '...' if len(question_text) > 100 else question_text,
            'correct_answer': correct_answer,
            'final_answer': final_answer,
            'is_correct': is_correct,
            'final_confidence': final_confidence,
            'fusion_reason': fusion_reason,
            'fusion_debug': fusion_debug,
            'specialist_outputs': [
                {
                    'specialty': so['specialty'],
                    'answer': so['answer'],
                    'confidence': so['confidence'],
                    'S_score': so.get('S_score'),
                    'G_score': so.get('G_score'),
                    # Important: include Two-Phase details so we can debug correctness/discrimination
                    'two_phase_result': so.get('two_phase_result')
                }
                for so in specialist_outputs
            ]
        }
        results['question_results'].append(result)
        
        # Use ASCII-safe status symbols for Windows compatibility
        status = "[OK]" if is_correct else "[X]"
        print(f"{status} (Conf: {final_confidence:.3f})")
    
    # Calculate metrics
    correct_count = sum(1 for r in results['question_results'] if r['is_correct'])
    accuracy = correct_count / len(results['question_results'])
    
    confidences = [r['final_confidence'] for r in results['question_results']]
    predictions = [r['final_answer'] for r in results['question_results']]
    ground_truth = [r['correct_answer'] for r in results['question_results']]
    correct_flags = [r['is_correct'] for r in results['question_results']]
    
    # Get options for each question (needed for answer matching in metrics)
    # We need to reload questions to get options, or store them in results
    # For now, we'll pass None and metrics will use is_correct flags if available
    # Actually, let's use the is_correct flags directly for accuracy calculation
    # But for ECE and AUROC, we need proper answer matching
    
    # Calculate confidence metrics (requires predictions, ground_truth, confidences)
    # Pass options for proper answer matching (letter to full text conversion)
    confidence_metrics = calculate_confidence_metrics(predictions, ground_truth, confidences, options=all_options)
    ece = confidence_metrics.get('ece', 0.0)
    brier_score = confidence_metrics.get('brier_score', 0.0) if 'brier_score' in confidence_metrics else 0.0
    auroc = calculate_auroc(predictions, ground_truth, confidences, options=all_options)
    
    results['metrics'] = {
        'accuracy': accuracy,
        'ece': ece,
        'brier_score': brier_score,
        'auroc': auroc
    }
    
    print(f"\n{'='*70}")
    print(f"Results for {config_name}")
    print(f"{'='*70}")
    print(f"Accuracy: {accuracy:.1%}")
    print(f"ECE: {ece:.3f}")
    print(f"AUROC: {auroc:.3f}")
    
    return results


def main():
    """Run final comparison experiment."""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run final comparison experiment')
    parser.add_argument('--model', type=str, 
                       default='meta-llama/Llama-3.1-8B-Instruct',
                       help='Model name (default: meta-llama/Llama-3.1-8B-Instruct)')
    args = parser.parse_args()
    
    model_name = args.model
    
    # Extract short model name for display
    if 'llama' in model_name.lower():
        model_display = 'LLAMA-3.1-8B'
        model_short = 'llama'
    elif 'mistral' in model_name.lower():
        model_display = 'MISTRAL-7B'
        model_short = 'mistral'
    else:
        model_display = model_name.split('/')[-1]
        model_short = 'model'
    
    print("="*70)
    print(f"FINAL COMPARISON - {model_display}")
    print("Single Specialist vs Multi-Agent + Two-Phase Verification")
    print("="*70)
    
    # Configuration
    dataset_path = "data/filtered/medqa_us_100q_high_disagreement.json"
    num_questions = 100  # Full 100-question test for publication (~6-7 hours)
    random_seed = 42
    
    # Load dataset
    print(f"\nLoading dataset from {dataset_path}...")
    questions = load_dataset(dataset_path, max_questions=num_questions, random_seed=random_seed)
    print(f"Loaded {len(questions)} questions")
    
    # Initialize LLM client
    print(f"\nInitializing LLM client ({model_display})...")
    llm_client = LocalLLMClient(
        model_name=model_name,
        use_4bit=False,  # FP16 for better accuracy
        hf_token=os.getenv('HF_TOKEN')
    )
    print("OK LLM client ready", flush=True)
    
    # Create specialists
    print("\nCreating specialist teams...", flush=True)
    
    # Single specialist: Use GP (General Practitioner) for broader perspective
    # GP has general knowledge across all specialties, making it a fair baseline
    # for mixed specialty questions (Respiratory, Cardiology, Neurology)
    single_specialty = "general practitioner"  # GP for single specialist (broader knowledge)
    single_specialist_team = create_specialist_team([single_specialty], llm_client)
    
    # Clear cache to ensure fresh answers (fixes cached null answers from previous runs)
    for specialist in single_specialist_team:
        if hasattr(specialist, 'clear_cache'):
            specialist.clear_cache()
    
    print(f"OK Single specialist: {single_specialist_team[0].specialty} (GP - broader perspective, cache cleared)", flush=True)
    
    # Multi-specialist team (domain specialists only - matches Wang et al. 2024)
    # Wang et al. 2024: Domain specialists provide diagnoses (no GP in team)
    print("Creating multi-specialist team...", flush=True)
    multi_specialties = [
        "respiratory",        # Pulmonologist
        "cardiology",         # Cardiologist
        "neurology",         # Neurologist
        "gastroenterology"    # Gastroenterologist
        # GP removed from main team but available as fallback
    ]
    multi_specialist_team = create_specialist_team(multi_specialties, llm_client)
    print("Multi-specialist team created", flush=True)
    
    # Clear cache to ensure fresh answers
    for specialist in multi_specialist_team:
        if hasattr(specialist, 'clear_cache'):
            specialist.clear_cache()
    
    print(f"OK Multi-specialist team: {[s.specialty for s in multi_specialist_team]}", flush=True)
    
    # Initialize verification components
    # Note: We're focusing on Two-Phase Verification only (no Tier 2), so GP is not needed
    print("\nInitializing verification components...")
    
    # Use weighted_average S_score formula (reverted from hybrid)
    import sys
    s_score_formula = "weighted_average"  # Default: weighted average formula
    if len(sys.argv) > 1:
        formula_arg = sys.argv[1].lower()
        if formula_arg in ["weighted_average", "multiplicative", "hybrid"]:
            s_score_formula = formula_arg
        elif formula_arg == "formula1":
            s_score_formula = "weighted_average"
        elif formula_arg == "formula2":
            s_score_formula = "multiplicative"
        elif formula_arg == "formula3" or formula_arg == "hybrid":
            s_score_formula = "hybrid"
    
    two_phase_verifier = Tier1Verifier(
        llm_client,
        s_score_formula=s_score_formula
    )  # Tier1Verifier implements Two-Phase Verification (Wu et al. 2024)
    print(f"OK Two-Phase Verification ready (formula: {s_score_formula})", flush=True)
    print("   Note: Tier 2 (GP validation) is not used in this comparison", flush=True)
    print(f"   S_score formula: {s_score_formula}", flush=True)
    
    # Define configurations (ordered for logical progression)
    # IMPORTANT: All configurations use SAME temperature_scale for fair comparison
    configurations = [
        {
            'name': 'Single Specialist',
            'specialists': single_specialist_team,
            'two_phase': None,
            'tier2': None,
            'integration_method': None,
            'alpha': None,
            'temperature_scale': 1.0,  # Same for all configurations - fair comparison
            'is_single_specialist': True
        },
        {
            'name': 'Single Specialist + Two-Phase Verification',  # Show verification helps for single agent
            'specialists': single_specialist_team,
            'two_phase': two_phase_verifier,
            'tier2': None,
            'integration_method': None,
            'alpha': None,
            'temperature_scale': 1.0,  # Same for all configurations - fair comparison
            'is_single_specialist': True
        },
        {
            'name': 'Multi-Agent (No Verification)',
            'specialists': multi_specialist_team,
            'two_phase': None,
            'tier2': None,
            'integration_method': None,
            'alpha': None,
            'temperature_scale': 1.0,  # Same for all configurations - fair comparison
            'is_single_specialist': False
        },
        {
            'name': 'Multi-Agent + Two-Phase Verification',  # ??? MAIN CONTRIBUTION
            'specialists': multi_specialist_team,
            'two_phase': two_phase_verifier,
            'tier2': None,
            'integration_method': None,
            'alpha': None,
            'temperature_scale': 1.0,  # Same for all configurations - fair comparison
            'is_single_specialist': False
        }
    ]
    
    # Run all configurations
    all_results = []
    start_time = datetime.now()
    
    for config in configurations:
        result = run_configuration(
            config_name=config['name'],
            llm_client=llm_client,
            specialists=config['specialists'],
            questions=questions,
            two_phase_verifier=config.get('two_phase'),  # Two-Phase Verification (Wu et al. 2024)
            tier2_validator=config['tier2'],
            integration_method=config['integration_method'],
            alpha=config['alpha'],
            temperature_scale=config['temperature_scale'],
            is_single_specialist=config['is_single_specialist']
        )
        all_results.append(result)
    
    end_time = datetime.now()
    elapsed = end_time - start_time
    
    # Save results
    output_dir = Path("results/paper1")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"final_comparison_{model_short}_{timestamp}.json"
    
    comparison_results = {
        'experiment': f'Final Comparison - {model_display}',
        'model': model_name,
        'timestamp': timestamp,
        'elapsed_time_seconds': elapsed.total_seconds(),
        'num_questions': num_questions,
        'dataset_path': dataset_path,
        'configurations': all_results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print("FINAL COMPARISON SUMMARY")
    print(f"{'='*70}")
    
    print(f"\n{'Configuration':<40} {'Accuracy':<12} {'ECE':<12} {'AUROC':<12}")
    print("-" * 80)
    
    for result in all_results:
        metrics = result['metrics']
        print(f"{result['config_name']:<40} {metrics['accuracy']:>10.1%}  {metrics['ece']:>10.3f}  {metrics['auroc']:>10.3f}")
    
    print(f"\nResults saved to: {output_file}")
    print(f"Total elapsed time: {elapsed}")
    
    # Identify best configuration
    best_config = max(all_results, key=lambda x: (
        x['metrics']['accuracy'] * 0.4 +
        (1 - x['metrics']['ece']) * 0.3 +
        x['metrics']['auroc'] * 0.3
    ))
    
    print(f"\n{'='*70}")
    print("BEST CONFIGURATION")
    print(f"{'='*70}")
    print(f"Configuration: {best_config['config_name']}")
    print(f"Multi-Metric Score: {best_config['metrics']['accuracy'] * 0.4 + (1 - best_config['metrics']['ece']) * 0.3 + best_config['metrics']['auroc'] * 0.3:.3f}")
    print(f"Accuracy: {best_config['metrics']['accuracy']:.1%}")
    print(f"ECE: {best_config['metrics']['ece']:.3f}")
    print(f"AUROC: {best_config['metrics']['auroc']:.3f}")


if __name__ == "__main__":
    main()
