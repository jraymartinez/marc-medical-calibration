"""
Run 4-Configuration Comparison
Configurations:
1. Single Specialist (respiratory only, no verification)
2. Single Specialist + Two-Phase Verification  
3. Multi-Agent + S-Score Weighted Fusion (no verification)
4. Multi-Agent + Two-Phase + S-Score Weighted Fusion - MAIN CONTRIBUTION

Clean ablation design: Config 3→4 isolates Two-Phase Verification contribution.
This script runs all 4 configurations and saves results for comparison.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.llm_client import LocalLLMClient
from src.agents.specialist_agent import create_specialist_team
from src.verification.tier1_verification import Tier1Verifier
from src.fusion.agreement_based_fusion import SScoreWeightedFusion
from src.evaluation.metrics import calculate_confidence_metrics, calculate_auroc

def load_dataset(dataset_path: str, num_questions: int = None):
    """Load dataset, normalising MedQA and MedMCQA formats to a common schema.

    Common schema fields required downstream:
      - question  : str
      - options   : dict  {A: text, B: text, C: text, D: text}
      - correct_answer : str  single uppercase letter
    """
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'questions' in data:
        questions = data['questions']
    elif isinstance(data, list):
        questions = data
    else:
        raise ValueError("Unknown dataset format")

    _COP_TO_LETTER = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}  # MedMCQA cop is 1-indexed

    for q in questions:
        # ── MedMCQA format: opa/opb/opc/opd + cop (1-indexed int) ──────────
        if 'opa' in q or 'opb' in q:
            # Build options dict if missing
            if not q.get('options'):
                q['options'] = {
                    'A': q.get('opa', ''),
                    'B': q.get('opb', ''),
                    'C': q.get('opc', ''),
                    'D': q.get('opd', ''),
                }
            # Derive correct_answer from cop (1→A, 2→B, 3→C, 4→D)
            cop = q.get('cop')
            q['correct_answer'] = _COP_TO_LETTER.get(int(cop), '') if cop is not None else ''
            continue

        # ── MedQA format: options dict + answer_idx / answer ────────────────
        if 'answer_idx' in q and q['answer_idx']:
            q['correct_answer'] = q['answer_idx']
        elif 'answer' in q and q['answer']:
            ans = str(q['answer']).strip()
            if len(ans) == 1 and ans.upper() in 'ABCDE':
                q['correct_answer'] = ans.upper()
            else:
                # Full-text answer — map back to letter via options dict
                for letter, text in q.get('options', {}).items():
                    if text == ans:
                        q['correct_answer'] = letter
                        break

    if num_questions:
        questions = questions[:num_questions]

    return questions

def extract_answer_letter(answer: str, valid_letters: list = None) -> str:
    """Extract letter from answer, optionally constraining to valid_letters.

    valid_letters should be the list of option keys for the current question
    (e.g. ['A','B','C','D'] for MedMCQA).  Letters outside this set are
    treated as extraction failures so we do not silently count a hallucinated
    option as the model's prediction.
    """
    if not answer:
        return ""
    all_letters = ['A', 'B', 'C', 'D', 'E']
    allowed = [l.upper() for l in valid_letters] if valid_letters else all_letters
    answer = answer.strip()
    if len(answer) == 1 and answer.upper() in allowed:
        return answer.upper()
    for letter in allowed:
        if answer.upper().startswith(letter + '.') or \
           answer.upper().startswith(letter + ':') or \
           answer.upper().startswith(letter + ')'):
            return letter
    # Fallback: first character, but only if it is a valid option
    first = answer[:1].upper() if answer else ""
    return first if first in allowed else ""

def run_config1_single_specialist(llm_client, questions):
    """Config 1: Single Specialist (respiratory only, no verification)."""
    start_time = time.time()
    
    print("\n" + "="*80)
    print("Configuration 1: Single Specialist (Baseline)")
    print("="*80)
    
    # Create single respiratory specialist
    specialists = create_specialist_team(
        llm_client=llm_client,
        specialties=['respiratory']
    )
    specialist = specialists[0]
    
    results = []
    predictions = []
    ground_truth = []
    confidences = []
    
    for idx, q in enumerate(questions, 1):
        print(f"\rProcessing Q{idx}/{len(questions)}...", end='', flush=True)
        
        question_text = q.get('question', '')
        options = q.get('options', {})
        correct_answer = q.get('correct_answer', q.get('answer_idx', ''))
        
        # Get diagnosis from specialist
        diagnosis = specialist.analyze_question(question_text, options)
        valid_letters = list(options.keys()) if isinstance(options, dict) else None
        predicted_answer = extract_answer_letter(diagnosis.get('answer', ''), valid_letters)
        confidence = diagnosis.get('confidence', 0.5)
        
        is_correct = (predicted_answer == correct_answer)
        
        # Print result
        status = "[OK]" if is_correct else "[X]"
        print(f"{status} Predicted: {predicted_answer}, Ground Truth: {correct_answer} (Conf: {confidence:.3f})")
        
        results.append({
            'question_idx': idx,
            'predicted_answer': predicted_answer,
            'correct_answer': correct_answer,
            'confidence': confidence,
            'is_correct': is_correct
        })
        
        predictions.append(predicted_answer)
        ground_truth.append(correct_answer)
        confidences.append(confidence)
    
    # Calculate metrics
    accuracy = sum(1 for r in results if r['is_correct']) / len(results)
    is_correct_list = [r['is_correct'] for r in results]
    metrics = calculate_confidence_metrics(predictions, ground_truth, confidences)
    auroc = calculate_auroc(predictions, ground_truth, confidences)
    
    elapsed_time = time.time() - start_time
    elapsed_minutes = elapsed_time / 60
    elapsed_hours = elapsed_time / 3600
    
    print("\n" + "="*80)
    print("RESULTS: Single Specialist (Baseline)")
    print("="*80)
    print(f"Accuracy: {accuracy:.1%}")
    print(f"ECE: {metrics['ece']:.3f}")
    print(f"AUROC: {auroc:.3f}")
    if elapsed_hours >= 1:
        print(f"Elapsed Time: {elapsed_hours:.2f} hours ({elapsed_minutes:.1f} minutes)")
    else:
        print(f"Elapsed Time: {elapsed_minutes:.1f} minutes")
    
    return {
        'config_name': 'Single Specialist',
        'accuracy': accuracy,
        'ece': metrics['ece'],
        'auroc': auroc,
        'elapsed_time_seconds': elapsed_time,
        'elapsed_time_minutes': elapsed_minutes,
        'results': results
    }

def run_config2_single_plus_2p(llm_client, questions):
    """Config 2: Single Specialist + Two-Phase Verification."""
    start_time = time.time()
    
    print("\n" + "="*80)
    print("Configuration 2: Single Specialist + Two-Phase Verification")
    print("="*80)
    
    # Create single respiratory specialist
    specialists = create_specialist_team(
        llm_client=llm_client,
        specialties=['respiratory']
    )
    specialist = specialists[0]
    
    # Create Two-Phase Verifier
    two_phase = Tier1Verifier(
        llm_client=llm_client,
        s_score_formula='multiplicative'
    )
    
    results = []
    predictions = []
    ground_truth = []
    confidences = []
    
    for idx, q in enumerate(questions, 1):
        print(f"\rProcessing Q{idx}/{len(questions)}...", end='', flush=True)
        
        question_text = q.get('question', '')
        options = q.get('options', {})
        correct_answer = q.get('correct_answer', q.get('answer_idx', ''))
        
        # Get diagnosis from specialist
        diagnosis = specialist.analyze_question(question_text, options)
        valid_letters = list(options.keys()) if isinstance(options, dict) else None
        predicted_answer = extract_answer_letter(diagnosis.get('answer', ''), valid_letters)
        initial_confidence = diagnosis.get('confidence', 0.5)
        reasoning = diagnosis.get('reasoning', '')
        
        # Apply Two-Phase Verification
        verification_result = two_phase.verify_specialist(
            specialist_name='respiratory',
            question=question_text,
            answer=predicted_answer,
            reasoning=reasoning,
            initial_confidence=initial_confidence,
            options=list(options.values()) if options else None
        )
        
        s_score = verification_result.get('specialist_confidence_S', initial_confidence)
        inconsistency = verification_result.get('inconsistency_score', 0.0)
        
        is_correct = (predicted_answer == correct_answer)
        
        # Print result with debug info
        status = "[OK]" if is_correct else "[X]"
        print(f"Initial: {initial_confidence:.3f}, Inconsistency: {inconsistency:.3f}, S_score: {s_score:.3f}")
        print(f"{status} Predicted: {predicted_answer}, Ground Truth: {correct_answer} (S-score: {s_score:.3f})")
        
        results.append({
            'question_idx': idx,
            'predicted_answer': predicted_answer,
            'correct_answer': correct_answer,
            'confidence': s_score,
            'is_correct': is_correct,
            'S_score': s_score
        })
        
        predictions.append(predicted_answer)
        ground_truth.append(correct_answer)
        confidences.append(s_score)
    
    # Calculate metrics
    accuracy = sum(1 for r in results if r['is_correct']) / len(results)
    is_correct_list = [r['is_correct'] for r in results]
    metrics = calculate_confidence_metrics(predictions, ground_truth, confidences)
    auroc = calculate_auroc(predictions, ground_truth, confidences)
    
    elapsed_time = time.time() - start_time
    elapsed_minutes = elapsed_time / 60
    elapsed_hours = elapsed_time / 3600
    
    print("\n" + "="*80)
    print("RESULTS: Single Specialist + Two-Phase Verification")
    print("="*80)
    print(f"Accuracy: {accuracy:.1%}")
    print(f"ECE: {metrics['ece']:.3f}")
    print(f"AUROC: {auroc:.3f}")
    if elapsed_hours >= 1:
        print(f"Elapsed Time: {elapsed_hours:.2f} hours ({elapsed_minutes:.1f} minutes)")
    else:
        print(f"Elapsed Time: {elapsed_minutes:.1f} minutes")
    
    return {
        'config_name': 'Single Specialist + Two-Phase',
        'accuracy': accuracy,
        'ece': metrics['ece'],
        'auroc': auroc,
        'elapsed_time_seconds': elapsed_time,
        'elapsed_time_minutes': elapsed_minutes,
        'results': results
    }

def run_config3_multi_no_verification(llm_client, questions):
    """Config 3: Multi-Agent + S-Score Weighted Fusion (no verification)."""
    start_time = time.time()
    
    print("\n" + "="*80)
    print("Configuration 3: Multi-Agent + S-Score Weighted Fusion (No Verification)")
    print("="*80)
    
    # Create 4 specialists
    print("\nCreating multi-specialist team...")
    specialists = create_specialist_team(
        llm_client=llm_client,
        specialties=['respiratory', 'cardiology', 'neurology', 'gastroenterology']
    )
    print("OK Created 4 domain specialists:")
    for spec in specialists:
        print(f"  - {spec.specialty}")
    
    # Create S-Score Weighted Fusion (will use raw confidence as S_score without verification)
    print("\nInitializing S-Score Weighted Fusion...")
    fusion = SScoreWeightedFusion()
    print(f"OK Fusion ready: {fusion.name}")
    print("   Strategy: Winner = answer with highest (vote_count × mean_S_score)")
    print("   Confidence: Vote-strength weighted blend of mean and min S-scores")
    print("   Note: No Two-Phase Verification in this config (S_score = confidence)")
    
    results = []
    predictions = []
    ground_truth = []
    confidences = []
    
    for idx, q in enumerate(questions, 1):
        print(f"\rProcessing Q{idx}/{len(questions)}...", end='', flush=True)
        
        question_text = q.get('question', '')
        options = q.get('options', {})
        correct_answer = q.get('correct_answer', q.get('answer_idx', ''))
        
        # Get diagnoses from all specialists (no verification)
        valid_letters = list(options.keys()) if isinstance(options, dict) else None
        specialist_outputs = []
        for specialist in specialists:
            diagnosis = specialist.analyze_question(question_text, options)
            answer = extract_answer_letter(diagnosis.get('answer', ''), valid_letters)
            confidence = diagnosis.get('confidence', 0.5)
            
            # Print specialist result (no verification, so S_score = confidence)
            print(f"DEBUG: {specialist.specialty} answer={answer}, conf={confidence:.3f}, S_score={confidence:.3f} (no 2P)")
            
            # Use confidence as S_score (no verification, so S_score = confidence)
            specialist_outputs.append({
                'answer': answer,
                'confidence': confidence,
                'S_score': confidence  # No verification, so S_score equals confidence
            })
        
        # Apply S-Score Weighted Fusion
        predicted_answer, final_confidence, debug_info = fusion.fuse(specialist_outputs)
        
        is_correct = (predicted_answer == correct_answer)
        
        # Print result with fusion debug info
        status = "[OK]" if is_correct else "[X]"
        all_agree = debug_info.get('all_agree', False)
        reason = debug_info.get('confidence_reason', 'unknown')
        print(f"FUSION: All_agree={all_agree}, Reason={reason}, Winner={predicted_answer}, Conf={final_confidence:.3f}")
        print(f"{status} Predicted: {predicted_answer}, Ground Truth: {correct_answer} (Conf: {final_confidence:.3f})")
        
        results.append({
            'question_idx': idx,
            'predicted_answer': predicted_answer,
            'correct_answer': correct_answer,
            'confidence': final_confidence,
            'is_correct': is_correct
        })
        
        predictions.append(predicted_answer)
        ground_truth.append(correct_answer)
        confidences.append(final_confidence)
    
    # Calculate metrics
    accuracy = sum(1 for r in results if r['is_correct']) / len(results)
    is_correct_list = [r['is_correct'] for r in results]
    metrics = calculate_confidence_metrics(predictions, ground_truth, confidences)
    auroc = calculate_auroc(predictions, ground_truth, confidences)
    
    elapsed_time = time.time() - start_time
    elapsed_minutes = elapsed_time / 60
    elapsed_hours = elapsed_time / 3600
    
    print("\n" + "="*80)
    print("RESULTS: Multi-Agent + S-Score Weighted Fusion (No Verification)")
    print("="*80)
    print(f"Accuracy: {accuracy:.1%}")
    print(f"ECE: {metrics['ece']:.3f}")
    print(f"AUROC: {auroc:.3f}")
    if elapsed_hours >= 1:
        print(f"Elapsed Time: {elapsed_hours:.2f} hours ({elapsed_minutes:.1f} minutes)")
    else:
        print(f"Elapsed Time: {elapsed_minutes:.1f} minutes")
    
    return {
        'config_name': 'Multi-Agent + S-Score Weighted Fusion (No Verification)',
        'accuracy': accuracy,
        'ece': metrics['ece'],
        'auroc': auroc,
        'elapsed_time_seconds': elapsed_time,
        'elapsed_time_minutes': elapsed_minutes,
        'results': results
    }

def run_config4_multi_plus_2p_hybrid(llm_client, questions):
    """Config 4: Multi-Agent + Two-Phase + S-Score Weighted Fusion - MAIN CONTRIBUTION."""
    start_time = time.time()
    
    print("\n" + "="*80)
    print("Configuration 4: Multi-Agent + Two-Phase + S-Score Weighted Fusion")
    print("="*80)
    
    # Create 4 specialists
    print("\nCreating multi-specialist team...")
    specialists = create_specialist_team(
        llm_client=llm_client,
        specialties=['respiratory', 'cardiology', 'neurology', 'gastroenterology']
    )
    print("OK Created 4 domain specialists:")
    for spec in specialists:
        print(f"  - {spec.specialty}")
    
    # Create Two-Phase Verifier
    print("\nInitializing Two-Phase Verification...")
    two_phase = Tier1Verifier(
        llm_client=llm_client,
        s_score_formula='multiplicative'
    )
    print("OK Two-Phase Verification ready")
    print("   S_score formula: multiplicative (S = initial_conf × (1 - inconsistency))")
    
    # Create S-Score Weighted Fusion
    print("\nInitializing S-Score Weighted Fusion...")
    fusion = SScoreWeightedFusion()
    print(f"OK Fusion ready: {fusion.name}")
    print("   Strategy: Winner = answer with highest (vote_count × mean_S_score)")
    print("   Confidence: Vote-strength weighted blend of mean and min S-scores")
    
    results = []
    predictions = []
    ground_truth = []
    confidences = []
    
    for idx, q in enumerate(questions, 1):
        print(f"\rProcessing Q{idx}/{len(questions)}...", end='', flush=True)
        
        question_text = q.get('question', '')
        options = q.get('options', {})
        correct_answer = q.get('correct_answer', q.get('answer_idx', ''))
        
        # Get diagnoses from all specialists with Two-Phase Verification
        valid_letters = list(options.keys()) if isinstance(options, dict) else None
        specialist_outputs = []
        for specialist in specialists:
            diagnosis = specialist.analyze_question(question_text, options)
            answer = extract_answer_letter(diagnosis.get('answer', ''), valid_letters)
            initial_confidence = diagnosis.get('confidence', 0.5)
            reasoning = diagnosis.get('reasoning', '')
            
            # Apply Two-Phase Verification
            verification_result = two_phase.verify_specialist(
                specialist_name=specialist.specialty,
                question=question_text,
                answer=answer,
                reasoning=reasoning,
                initial_confidence=initial_confidence,
                options=list(options.values()) if options else None
            )
            
            s_score = verification_result.get('specialist_confidence_S', initial_confidence)
            
            # Print specialist result
            print(f"DEBUG: {specialist.specialty} answer={answer}, initial_conf={initial_confidence:.3f}, S_score={s_score:.3f}")
            
            specialist_outputs.append({
                'answer': answer,
                'confidence': diagnosis.get('confidence', 0.5),
                'S_score': s_score,
                'two_phase_result': verification_result
            })
        
        # Apply S-Score Weighted Fusion
        predicted_answer, final_confidence, debug_info = fusion.fuse(specialist_outputs)
        
        is_correct = (predicted_answer == correct_answer)
        
        # Print fusion result
        status = "[OK]" if is_correct else "[X]"
        all_agree = debug_info.get('all_agree', False)
        reason = debug_info.get('confidence_reason', 'unknown')
        print(f"FUSION: All_agree={all_agree}, Reason={reason}, Winner={predicted_answer}, Conf={final_confidence:.3f}")
        print(f"{status} Predicted: {predicted_answer}, Ground Truth: {correct_answer} (Conf: {final_confidence:.3f})")
        print()  # Blank line between questions
        
        results.append({
            'question_idx': idx,
            'predicted_answer': predicted_answer,
            'correct_answer': correct_answer,
            'confidence': final_confidence,
            'is_correct': is_correct
        })
        
        predictions.append(predicted_answer)
        ground_truth.append(correct_answer)
        confidences.append(final_confidence)
    
    # Calculate metrics
    accuracy = sum(1 for r in results if r['is_correct']) / len(results)
    is_correct_list = [r['is_correct'] for r in results]
    metrics = calculate_confidence_metrics(predictions, ground_truth, confidences)
    auroc = calculate_auroc(predictions, ground_truth, confidences)
    
    elapsed_time = time.time() - start_time
    elapsed_minutes = elapsed_time / 60
    elapsed_hours = elapsed_time / 3600
    
    print("\n" + "="*80)
    print("RESULTS: Multi-Agent + Two-Phase + S-Score Weighted Fusion")
    print("="*80)
    print(f"Accuracy: {accuracy:.1%}")
    print(f"ECE: {metrics['ece']:.3f}")
    print(f"AUROC: {auroc:.3f}")
    if elapsed_hours >= 1:
        print(f"Elapsed Time: {elapsed_hours:.2f} hours ({elapsed_minutes:.1f} minutes)")
    else:
        print(f"Elapsed Time: {elapsed_minutes:.1f} minutes")
    
    return {
        'config_name': 'Multi-Agent + Two-Phase + S-Score Weighted Fusion',
        'accuracy': accuracy,
        'ece': metrics['ece'],
        'auroc': auroc,
        'elapsed_time_seconds': elapsed_time,
        'elapsed_time_minutes': elapsed_minutes,
        'results': results
    }

def main():
    parser = argparse.ArgumentParser(description='Run 4-configuration comparison')
    parser.add_argument('--model', type=str, required=True, help='Model name')
    parser.add_argument('--dataset', type=str, required=True, help='Dataset path')
    parser.add_argument('--num_questions', type=int, default=100, help='Number of questions')
    args = parser.parse_args()
    
    print(f"\n{'='*80}")
    print(f"4-Configuration Comparison")
    print(f"Model: {args.model}")
    print(f"Dataset: {args.dataset}")
    print(f"Questions: {args.num_questions}")
    print(f"{'='*80}\n")
    
    # Load dataset
    questions = load_dataset(args.dataset, args.num_questions)
    print(f"Loaded {len(questions)} questions\n")
    
    # Initialize LLM
    print("Initializing LLM client...")
    llm_client = LocalLLMClient(model_name=args.model, use_4bit=False, device="cuda")
    print("LLM client ready\n")
    
    start_time = datetime.now()
    
    # Run all 4 configurations
    config1_results = run_config1_single_specialist(llm_client, questions)
    config2_results = run_config2_single_plus_2p(llm_client, questions)
    config3_results = run_config3_multi_no_verification(llm_client, questions)
    config4_results = run_config4_multi_plus_2p_hybrid(llm_client, questions)
    
    end_time = datetime.now()
    elapsed = end_time - start_time
    
    # Save results
    output_dir = Path("results/4_config_comparison")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_short = 'qwen' if 'qwen' in args.model.lower() else 'llama' if 'llama' in args.model.lower() else 'model'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"4_config_{model_short}_{timestamp}.json"
    
    all_results = {
        'model': args.model,
        'dataset': args.dataset,
        'num_questions': args.num_questions,
        'timestamp': datetime.now().isoformat(),
        'elapsed_time': str(elapsed),
        'configurations': {
            'config1': config1_results,
            'config2': config2_results,
            'config3': config3_results,
            'config4': config4_results
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    
    # Print summary
    print(f"\n{'='*80}")
    # Format time helper
    def format_time(minutes):
        if minutes >= 60:
            hours = minutes / 60
            return f"{hours:.2f}h ({minutes:.0f}m)"
        else:
            return f"{minutes:.1f}m"
    
    print("SUMMARY")
    print(f"{'='*100}")
    print(f"{'Configuration':<50} {'Accuracy':>10} {'ECE':>10} {'AUROC':>10} {'Time':>15}")
    print("-" * 100)
    print(f"{'1. Single Specialist':<50} {config1_results['accuracy']:>9.1%} {config1_results['ece']:>10.3f} {config1_results['auroc']:>10.3f} {format_time(config1_results['elapsed_time_minutes']):>15}")
    print(f"{'2. Single + Two-Phase':<50} {config2_results['accuracy']:>9.1%} {config2_results['ece']:>10.3f} {config2_results['auroc']:>10.3f} {format_time(config2_results['elapsed_time_minutes']):>15}")
    print(f"{'3. Multi + S-Score Weighted Fusion (No 2P)':<50} {config3_results['accuracy']:>9.1%} {config3_results['ece']:>10.3f} {config3_results['auroc']:>10.3f} {format_time(config3_results['elapsed_time_minutes']):>15}")
    print(f"{'4. Multi + Two-Phase + S-Score Weighted':<50} {config4_results['accuracy']:>9.1%} {config4_results['ece']:>10.3f} {config4_results['auroc']:>10.3f} {format_time(config4_results['elapsed_time_minutes']):>15}")
    print("=" * 100)
    print(f"\nResults saved to: {output_file}")
    print(f"Total time: {elapsed}")
    print()

if __name__ == '__main__':
    main()
