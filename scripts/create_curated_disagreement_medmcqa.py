"""
Create curated MedMCQA dataset with 80% specialist disagreement.

This script:
1. Loads MedMCQA questions from the filtered multi-specialty dataset
2. Runs 4 specialists (Respiratory, Cardiology, Neurology, Gastroenterology) on each question
3. Identifies questions where specialists disagree
4. Creates curated datasets with target disagreement rate

Outputs:
- data/filtered/curated_disagreement_medmcqa.json (all disagreement questions)
- data/filtered/curated_agreement_medmcqa.json (all agreement questions)
"""

import json
import random
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.llm_client import LocalLLMClient


def load_medmcqa_from_multi_specialty(multi_specialty_path: Path) -> List[Dict[str, Any]]:
    """
    Extract MedMCQA questions from the multi-specialty filtered dataset.
    
    Args:
        multi_specialty_path: Path to multi_specialty_cases_all.json
        
    Returns:
        List of MedMCQA question dictionaries
    """
    print("Loading multi-specialty dataset...")
    with open(multi_specialty_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_questions = data.get('filtered_questions', [])
    print(f"  Total questions in multi-specialty: {len(all_questions)}")
    
    # Filter for MedMCQA questions
    # MedMCQA questions have fields like: opa, opb, opc, opd, subject, exp
    medmcqa_questions = []
    for q in all_questions:
        # Check if it's MedMCQA format (has opa/opb/opc/opd or has 'subject' field)
        has_mcqa_format = ('opa' in q or 'opb' in q or 'opc' in q or 'opd' in q or 
                          'subject' in q or 'exp' in q or 'choice_type' in q)
        
        # MedQA has 'metamap_phrases' and 'meta_info' with 'step2&3' value
        is_medqa = 'metamap_phrases' in q or (q.get('meta_info') == 'step2&3')
        
        if has_mcqa_format and not is_medqa:
            medmcqa_questions.append(q)
    
    print(f"  Extracted {len(medmcqa_questions)} MedMCQA questions")
    return medmcqa_questions


SPECIALTIES = [
    ("respiratory", "Respiratory Medicine specialist (pulmonology, lung disease)"),
    ("cardiology",  "Cardiology specialist (heart disease, cardiac conditions)"),
    ("neurology",   "Neurology specialist (brain, spinal cord, nervous system)"),
    ("gastroenterology", "Gastroenterology specialist (GI tract, liver, pancreas)"),
]

# Minimal prompt for fast disagreement curation — just needs the answer letter
_SYSTEM_TMPL = "You are an expert {label}. Answer the multiple-choice question below with ONLY the option letter (A, B, C, or D). Do not explain."
_USER_TMPL = """Question: {question}

Options:
{options}

Reply with a single letter: A, B, C, or D."""


def get_specialist_answer(
    llm_client: LocalLLMClient,
    specialty_label: str,
    question_text: str,
    options_list: List[str],
) -> str:
    """
    Call the LLM once for a given specialty and return the answer letter.
    Uses a minimal prompt (no chain-of-thought) for speed.
    """
    system = _SYSTEM_TMPL.format(label=specialty_label)
    user = _USER_TMPL.format(
        question=question_text,
        options="\n".join(options_list),
    )
    response = llm_client.generate(
        system_prompt=system,
        user_prompt=user,
        do_sample=False,       # greedy — deterministic
        max_new_tokens=8,      # we only need a single letter
    )
    # Extract first A/B/C/D letter from the response
    import re
    m = re.search(r'\b([A-D])\b', response.strip(), re.IGNORECASE)
    return m.group(1).upper() if m else response.strip()[:1].upper()


def analyze_specialist_disagreement(
    questions: List[Dict[str, Any]],
    llm_client: LocalLLMClient,
    max_questions: int = None,
    target_disagreement: int = None,
    target_agreement: int = None,
) -> Tuple[List[Dict], List[Dict]]:
    """
    Analyze questions with 4 virtual specialists to identify disagreement.

    Uses a minimal direct prompt (no chain-of-thought) so each specialist
    answer takes ~1-2s instead of ~20s.

    Early stopping: loop breaks as soon as both quotas are filled.

    Returns:
        Tuple of (disagreement_questions, agreement_questions)
    """
    print("\n" + "="*70)
    print("ANALYZING SPECIALIST DISAGREEMENT")
    print("="*70)

    questions_to_process = questions if max_questions is None else questions[:max_questions]
    print(f"Available questions: {len(questions_to_process)}")
    print(f"Specialties: {[s[0] for s in SPECIALTIES]}")

    if target_disagreement and target_agreement:
        print(f"Early-stop targets: {target_disagreement} disagreement + {target_agreement} agreement")
    print()

    disagreement_questions = []
    agreement_questions = []

    for idx, q in enumerate(questions_to_process, 1):
        if idx % 50 == 0:
            print(f"\nProcessed {idx} questions so far...", flush=True)
            print(f"  Disagreement: {len(disagreement_questions)}"
                  + (f" / {target_disagreement}" if target_disagreement else ""), flush=True)
            print(f"  Agreement:    {len(agreement_questions)}"
                  + (f" / {target_agreement}" if target_agreement else ""), flush=True)
        elif idx % 10 == 0:
            print(f"  Q{idx} | disagree={len(disagreement_questions)} agree={len(agreement_questions)}", flush=True)

        # Extract question text and options
        question_text = q.get('question', '') or q.get('Question', '')
        options = q.get('options', {}) or q.get('Options', {})

        # Handle MedMCQA format: opa, opb, opc, opd → A, B, C, D
        if not options:
            options = {}
            for key in ['opa', 'opb', 'opc', 'opd']:
                if key in q:
                    options[key.upper().replace('OP', '')] = q[key]

        if isinstance(options, dict):
            options_list = [f"{k}: {v}" for k, v in options.items()]
        else:
            options_list = list(options)

        # Get one answer per specialist using fast minimal prompt
        specialist_answers = []
        error = False
        for specialty_name, specialty_label in SPECIALTIES:
            try:
                answer = get_specialist_answer(llm_client, specialty_label, question_text, options_list)
                specialist_answers.append(answer)
            except Exception as e:
                print(f"\n  Error on Q{idx} [{specialty_name}]: {e}", flush=True)
                error = True
                break

        if error or len(specialist_answers) != len(SPECIALTIES):
            print(f"\n  Skipping Q{idx}", flush=True)
            continue

        unique_answers = len(set(specialist_answers))

        q_with_analysis = dict(q)
        q_with_analysis['specialist_answers'] = specialist_answers
        q_with_analysis['unique_answer_count'] = unique_answers
        q_with_analysis['disagreement'] = unique_answers > 1

        if unique_answers > 1:
            disagreement_questions.append(q_with_analysis)
        else:
            agreement_questions.append(q_with_analysis)

        # Early stopping: both quotas filled
        if (target_disagreement and target_agreement
                and len(disagreement_questions) >= target_disagreement
                and len(agreement_questions) >= target_agreement):
            print(f"\n  Early stop at Q{idx}: "
                  f"{len(disagreement_questions)} disagreement + {len(agreement_questions)} agreement.",
                  flush=True)
            break

    total = len(disagreement_questions) + len(agreement_questions)
    print(f"\n\n" + "="*70)
    print("ANALYSIS SUMMARY")
    print("="*70)
    print(f"Total processed: {total}")
    print(f"Disagreement: {len(disagreement_questions)} ({len(disagreement_questions)/total*100:.1f}%)")
    print(f"Agreement:    {len(agreement_questions)} ({len(agreement_questions)/total*100:.1f}%)")

    return disagreement_questions, agreement_questions


def main():
    """Create curated MedMCQA disagreement dataset."""
    
    # Paths
    multi_specialty_path = project_root / "data" / "filtered" / "multi_specialty_cases_all.json"
    output_dir = project_root / "data" / "filtered"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    disagreement_output = output_dir / "curated_disagreement_medmcqa.json"
    agreement_output = output_dir / "curated_agreement_medmcqa.json"
    
    print("="*70)
    print("MEDMCQA SPECIALIST DISAGREEMENT ANALYSIS")
    print("="*70)
    
    # Check if multi-specialty dataset exists
    if not multi_specialty_path.exists():
        print(f"\nERROR: Multi-specialty dataset not found: {multi_specialty_path}")
        print("Please run: python src/filtering/multi_specialty_filter.py first")
        return
    
    # Load MedMCQA questions
    medmcqa_questions = load_medmcqa_from_multi_specialty(multi_specialty_path)
    
    if not medmcqa_questions:
        print("ERROR: No MedMCQA questions found!")
        return
    
    # Shuffle for randomness
    random.seed(42)
    random.shuffle(medmcqa_questions)
    
    # Initialize LLM client
    # Using Qwen2.5-7B-Instruct (already cached locally, no HF_TOKEN needed)
    print("\nInitializing LLM client...")
    llm_client = LocalLLMClient(
        model_name="Qwen/Qwen2.5-7B-Instruct",
        use_4bit=False,  # FP16
    )
    print("OK LLM client ready")
    
    # Analyze disagreement with early stopping.
    # Targets cover the largest downstream subset (250q = 200 disagreement + 50 agreement).
    # The 100q subset (80 disagreement + 20 agreement) is fully covered by these numbers.
    # Fast minimal prompt (~2s/specialist) exits after ~500 questions instead of ~49K.
    print("\nStarting disagreement analysis...")
    disagreement_questions, agreement_questions = analyze_specialist_disagreement(
        questions=medmcqa_questions,
        llm_client=llm_client,
        max_questions=None,
        target_disagreement=220,  # buffer above 200 to account for cop=None after filtering
        target_agreement=60,      # buffer above 50 to account for cop=None after filtering
    )
    
    # Save disagreement questions
    print(f"\nSaving disagreement questions to: {disagreement_output}")
    with open(disagreement_output, 'w', encoding='utf-8') as f:
        json.dump(disagreement_questions, f, indent=2, ensure_ascii=False)
    
    # Save agreement questions
    print(f"Saving agreement questions to: {agreement_output}")
    with open(agreement_output, 'w', encoding='utf-8') as f:
        json.dump(agreement_questions, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("DATASET CREATION COMPLETE")
    print("="*70)
    print(f"Disagreement questions: {len(disagreement_questions)}")
    print(f"Agreement questions: {len(agreement_questions)}")
    print(f"Disagreement rate: {len(disagreement_questions)/(len(disagreement_questions)+len(agreement_questions))*100:.1f}%")
    
    print("\nNext steps:")
    print("1. Run: python scripts/create_medmcqa_100q_high_disagreement.py")
    print("2. Run: python scripts/create_medmcqa_250q_high_disagreement.py")


if __name__ == '__main__':
    main()
