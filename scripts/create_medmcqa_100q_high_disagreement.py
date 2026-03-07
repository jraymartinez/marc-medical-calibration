"""
Create a 100-question high-disagreement MedMCQA dataset.

Inputs
------
- data/filtered/curated_disagreement_medmcqa.json
    Questions with specialist disagreement (created by create_curated_disagreement_medmcqa.py)
- data/filtered/curated_agreement_medmcqa.json
    Questions with specialist agreement (created by create_curated_disagreement_medmcqa.py)

Output
------
- data/filtered/medmcqa_100q_high_disagreement.json
    100-question dataset:
      - 80 questions with specialist disagreement
      - 20 questions with specialist agreement
    Each question is tagged with:
      - "disagreement": true/false

Usage
-----
python scripts/create_medmcqa_100q_high_disagreement.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "filtered"

DISAGREEMENT_PATH = DATA_DIR / "curated_disagreement_medmcqa.json"
AGREEMENT_PATH = DATA_DIR / "curated_agreement_medmcqa.json"
OUTPUT_PATH = DATA_DIR / "medmcqa_100q_high_disagreement.json"


def load_json(path: Path) -> List[Dict[str, Any]]:
    """Load JSON file and return as list."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Handle different formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        if "filtered_questions" in data:
            return data["filtered_questions"]
        elif "questions" in data:
            return data["questions"]
    
    raise ValueError(f"Unexpected JSON structure in {path}")


def main() -> None:
    # Configuration
    target_total: int = 100
    target_disagreement: int = 80
    target_agreement: int = target_total - target_disagreement
    rng_seed: int = 42  # deterministic sampling/shuffling

    print("="*70)
    print("CREATING MEDMCQA 100Q HIGH-DISAGREEMENT DATASET")
    print("="*70)
    
    # Check inputs
    if not DISAGREEMENT_PATH.exists():
        raise FileNotFoundError(
            f"Disagreement dataset not found: {DISAGREEMENT_PATH}\n"
            f"Please run: python scripts/create_curated_disagreement_medmcqa.py first"
        )
    
    if not AGREEMENT_PATH.exists():
        raise FileNotFoundError(
            f"Agreement dataset not found: {AGREEMENT_PATH}\n"
            f"Please run: python scripts/create_curated_disagreement_medmcqa.py first"
        )

    # Load datasets
    print(f"\nLoading disagreement questions from: {DISAGREEMENT_PATH}")
    disagreement_questions = load_json(DISAGREEMENT_PATH)
    disagreement_questions = [q for q in disagreement_questions if q.get('cop') is not None]
    print(f"  Loaded {len(disagreement_questions)} disagreement questions (cop != None)")
    
    print(f"\nLoading agreement questions from: {AGREEMENT_PATH}")
    agreement_questions = load_json(AGREEMENT_PATH)
    agreement_questions = [q for q in agreement_questions if q.get('cop') is not None]
    print(f"  Loaded {len(agreement_questions)} agreement questions (cop != None)")

    # Check if we have enough questions
    if len(disagreement_questions) < target_disagreement:
        print(
            f"\nWARNING: Only {len(disagreement_questions)} disagreement questions available, "
            f"but need {target_disagreement}."
        )
        print(f"  Adjusting target to {len(disagreement_questions)} disagreement questions")
        target_disagreement = len(disagreement_questions)
        target_agreement = target_total - target_disagreement
    
    if len(agreement_questions) < target_agreement:
        raise ValueError(
            f"Not enough agreement questions ({len(agreement_questions)}) "
            f"to sample {target_agreement} questions."
        )

    # Sample questions
    rng = random.Random(rng_seed)
    
    # Sample disagreement questions (prioritize higher disagreement)
    # Sort by unique_answer_count (higher = more disagreement)
    sorted_disagreement = sorted(
        disagreement_questions,
        key=lambda x: x.get('unique_answer_count', 0),
        reverse=True
    )
    sampled_disagreement = sorted_disagreement[:target_disagreement]
    
    # Sample agreement questions randomly
    sampled_agreement = rng.sample(agreement_questions, target_agreement)

    # Tag questions with disagreement flag (ensure clean format)
    def clean_question(q: Dict, disagreement: bool) -> Dict:
        """Remove analysis fields and add disagreement tag."""
        q_clean = dict(q)
        # Remove specialist analysis fields
        q_clean.pop('specialist_answers', None)
        q_clean.pop('unique_answer_count', None)
        # Set disagreement flag
        q_clean['disagreement'] = disagreement
        return q_clean
    
    tagged_disagreement = [clean_question(q, True) for q in sampled_disagreement]
    tagged_agreement = [clean_question(q, False) for q in sampled_agreement]

    # Combine and shuffle
    combined: List[Dict[str, Any]] = tagged_disagreement + tagged_agreement
    rng.shuffle(combined)

    # Sanity checks
    num_disagreement = sum(1 for q in combined if q.get("disagreement") is True)
    num_agreement = sum(1 for q in combined if q.get("disagreement") is False)

    print("\n" + "="*70)
    print("DATASET SUMMARY")
    print("="*70)
    print(f"Total questions: {len(combined)}")
    print(f"Disagreement questions: {num_disagreement} ({num_disagreement/len(combined)*100:.1f}%)")
    print(f"Agreement questions: {num_agreement} ({num_agreement/len(combined)*100:.1f}%)")

    # Save output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {OUTPUT_PATH}")
    print("="*70)


if __name__ == "__main__":
    main()
