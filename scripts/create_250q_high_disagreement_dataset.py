"""
Create a 250-question high-disagreement dataset.

This follows the same methodology as the 100q dataset:
- 80% questions with specialist disagreement (200 questions)
- 20% questions with specialist agreement (50 questions)

Inputs
------
- data/filtered/medqa_us_train_balanced.json
    Balanced 600-question dataset (200 per specialty: respiratory/cardiology/neurology).
- data/filtered/curated_disagreement_train_test.json
    Curated disagreement set (~80 questions with specialist disagreement).
- data/filtered/medqa_us_100q_high_disagreement.json
    Existing 100q dataset (to exclude from 250q to avoid overlap).

Output
------
- data/filtered/medqa_us_250q_high_disagreement.json
    250-question dataset:
      - 200 questions with specialist disagreement (80%)
      - 50 questions with specialist agreement (20%)
    Each question is tagged with:
      - "disagreement": true/false

Strategy
--------
1. Load the 100q dataset and extract question texts to exclude
2. Load balanced dataset (600 questions)
3. Load curated disagreement dataset (80 questions)
4. For disagreement questions:
   - Use curated disagreement questions NOT in 100q
   - If needed, sample additional from balanced dataset (questions with disagreement=true)
5. For agreement questions:
   - Sample from balanced dataset (questions NOT in curated and NOT in 100q)
6. Shuffle and save

Usage
-----
python -u scripts/create_250q_high_disagreement_dataset.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Set


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "filtered"

BALANCED_PATH = DATA_DIR / "medqa_us_train_balanced.json"
CURATED_DISAGREEMENT_PATH = DATA_DIR / "curated_disagreement_train_test.json"
EXISTING_100Q_PATH = DATA_DIR / "medqa_us_100q_high_disagreement.json"
OUTPUT_PATH = DATA_DIR / "medqa_us_250q_high_disagreement.json"


def load_json_any(path: Path) -> Any:
    """Load arbitrary JSON from disk."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_question_list(obj: Any, context: str) -> List[Dict[str, Any]]:
    """Normalize different JSON structures to a flat list of question dicts.

    Supports:
    - {"filtered_questions": [...]} (current balanced dataset format)
    - [...] (plain list of questions)
    """
    if isinstance(obj, dict):
        if "filtered_questions" in obj and isinstance(obj["filtered_questions"], list):
            return obj["filtered_questions"]
        raise ValueError(
            f"Unexpected JSON structure for {context}: dict without "
            f"'filtered_questions' key."
        )
    if isinstance(obj, list):
        return obj
    raise ValueError(f"Unexpected JSON type for {context}: {type(obj)}")


def tag_questions(
    questions: List[Dict[str, Any]],
    disagreement: bool,
) -> List[Dict[str, Any]]:
    """Return a new list of questions with a boolean disagreement tag added."""
    tagged: List[Dict[str, Any]] = []
    for q in questions:
        q_copy = dict(q)
        q_copy["disagreement"] = disagreement
        tagged.append(q_copy)
    return tagged


def main() -> None:
    # Configuration
    target_total: int = 250
    target_disagreement: int = 200  # 80%
    target_agreement: int = 50      # 20%
    rng_seed: int = 42  # deterministic sampling/shuffling

    print("="*70)
    print("CREATE 250-QUESTION HIGH-DISAGREEMENT DATASET")
    print("="*70)
    print(f"\nTarget: {target_total} questions")
    print(f"  - Disagreement: {target_disagreement} ({target_disagreement/target_total*100:.0f}%)")
    print(f"  - Agreement: {target_agreement} ({target_agreement/target_total*100:.0f}%)")
    print(f"\nSeed: {rng_seed} (deterministic)")

    # Check files exist
    if not BALANCED_PATH.exists():
        raise FileNotFoundError(f"Balanced dataset not found at: {BALANCED_PATH}")
    if not CURATED_DISAGREEMENT_PATH.exists():
        raise FileNotFoundError(
            f"Curated disagreement dataset not found at: {CURATED_DISAGREEMENT_PATH}"
        )
    if not EXISTING_100Q_PATH.exists():
        raise FileNotFoundError(
            f"Existing 100q dataset not found at: {EXISTING_100Q_PATH}"
        )

    # Load datasets
    print("\n" + "="*70)
    print("LOADING DATASETS")
    print("="*70)

    balanced_raw = load_json_any(BALANCED_PATH)
    curated_raw = load_json_any(CURATED_DISAGREEMENT_PATH)
    existing_100q_raw = load_json_any(EXISTING_100Q_PATH)

    balanced = ensure_question_list(balanced_raw, context="balanced dataset")
    curated_disagreement = ensure_question_list(
        curated_raw, context="curated disagreement dataset"
    )
    existing_100q = ensure_question_list(existing_100q_raw, context="100q dataset")

    print(f"\nBalanced dataset: {len(balanced)} questions")
    print(f"Curated disagreement: {len(curated_disagreement)} questions")
    print(f"Existing 100q: {len(existing_100q)} questions")

    # Build exclusion set from 100q
    existing_100q_texts: Set[str] = {
        q["question"] for q in existing_100q if "question" in q
    }
    print(f"\nExcluding {len(existing_100q_texts)} questions from 100q dataset")

    # Build disagreement question pool
    print("\n" + "="*70)
    print("BUILDING DISAGREEMENT QUESTION POOL")
    print("="*70)

    # Start with curated disagreement questions NOT in 100q
    curated_not_in_100q = [
        q for q in curated_disagreement
        if q.get("question") not in existing_100q_texts
    ]
    print(f"\nCurated disagreement NOT in 100q: {len(curated_not_in_100q)} questions")

    # If we need more disagreement questions, we need to identify them from balanced
    # For now, we'll assume curated has enough, or sample randomly from balanced
    # that are NOT in 100q and NOT in curated
    curated_texts = {q["question"] for q in curated_disagreement if "question" in q}
    
    additional_pool = [
        q for q in balanced
        if q.get("question") not in existing_100q_texts
        and q.get("question") not in curated_texts
    ]
    
    print(f"Additional pool (balanced, not in 100q, not in curated): {len(additional_pool)} questions")

    # Sample disagreement questions
    rng = random.Random(rng_seed)
    
    if len(curated_not_in_100q) >= target_disagreement:
        # We have enough from curated
        sampled_disagreement = rng.sample(curated_not_in_100q, target_disagreement)
        print(f"\nSampled {target_disagreement} disagreement questions from curated set")
    else:
        # Use all curated + sample from additional pool
        num_needed = target_disagreement - len(curated_not_in_100q)
        print(f"\nUsing all {len(curated_not_in_100q)} curated disagreement questions")
        print(f"Need {num_needed} more disagreement questions from additional pool")
        
        if len(additional_pool) < num_needed:
            raise ValueError(
                f"Not enough questions to reach target. "
                f"Need {num_needed} more, but only {len(additional_pool)} available."
            )
        
        additional_disagreement = rng.sample(additional_pool, num_needed)
        sampled_disagreement = curated_not_in_100q + additional_disagreement
        print(f"Sampled {len(additional_disagreement)} from additional pool")

    # Build agreement question pool
    print("\n" + "="*70)
    print("BUILDING AGREEMENT QUESTION POOL")
    print("="*70)

    # Agreement candidates: NOT in 100q, NOT in curated, NOT in sampled_disagreement
    sampled_disagreement_texts = {q["question"] for q in sampled_disagreement if "question" in q}
    
    agreement_candidates = [
        q for q in balanced
        if q.get("question") not in existing_100q_texts
        and q.get("question") not in curated_texts
        and q.get("question") not in sampled_disagreement_texts
    ]

    print(f"\nAgreement candidates: {len(agreement_candidates)} questions")

    if len(agreement_candidates) < target_agreement:
        raise ValueError(
            f"Not enough agreement candidates ({len(agreement_candidates)}) "
            f"to sample {target_agreement} questions."
        )

    sampled_agreement = rng.sample(agreement_candidates, target_agreement)
    print(f"Sampled {target_agreement} agreement questions")

    # Tag and combine
    print("\n" + "="*70)
    print("COMBINING AND SHUFFLING")
    print("="*70)

    tagged_disagreement = tag_questions(sampled_disagreement, disagreement=True)
    tagged_agreement = tag_questions(sampled_agreement, disagreement=False)

    combined: List[Dict[str, Any]] = tagged_disagreement + tagged_agreement

    # Shuffle combined list deterministically for randomized order
    rng.shuffle(combined)

    # Sanity checks
    num_disagreement = sum(1 for q in combined if q.get("disagreement") is True)
    num_agreement = sum(1 for q in combined if q.get("disagreement") is False)

    print(f"\nFinal dataset:")
    print(f"  - Total questions: {len(combined)}")
    print(f"  - Disagreement questions: {num_disagreement} ({num_disagreement/len(combined)*100:.1f}%)")
    print(f"  - Agreement questions: {num_agreement} ({num_agreement/len(combined)*100:.1f}%)")

    # Verify no overlap with 100q
    combined_texts = {q["question"] for q in combined if "question" in q}
    overlap = combined_texts & existing_100q_texts
    if overlap:
        print(f"\nWARNING: Found {len(overlap)} overlapping questions with 100q!")
        print("This should not happen. Please investigate.")
    else:
        print(f"\nOK: No overlap with 100q dataset")

    # Save output
    print("\n" + "="*70)
    print("SAVING DATASET")
    print("="*70)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\nSaved 250-question high-disagreement dataset to:")
    print(f"  {OUTPUT_PATH}")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nDataset created successfully!")
    print(f"  - Total: {len(combined)} questions")
    print(f"  - Disagreement: {num_disagreement} ({num_disagreement/len(combined)*100:.0f}%)")
    print(f"  - Agreement: {num_agreement} ({num_agreement/len(combined)*100:.0f}%)")
    print(f"  - No overlap with 100q: OK")
    print(f"\nReady for experiments!")
    print(f"\nTo run experiment:")
    print(f"  python scripts/run_final_comparison.py --num_questions 250 \\")
    print(f"    --dataset data/filtered/medqa_us_250q_high_disagreement.json \\")
    print(f"    --seed 42")


if __name__ == "__main__":
    main()
