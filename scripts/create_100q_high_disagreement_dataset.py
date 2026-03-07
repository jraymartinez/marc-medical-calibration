"""
Create a 100-question high-disagreement dataset.

Inputs
------
- data/filtered/medqa_us_train_balanced.json
    Balanced 600-question dataset (200 per specialty: respiratory/cardiology/neurology).
- data/filtered/curated_disagreement_train_test.json
    Curated disagreement set (subset of the above, ~80 questions with specialist disagreement).

Output
------
- data/filtered/medqa_us_100q_high_disagreement.json
    100-question dataset:
      - 80 questions with specialist disagreement
      - 20 questions with specialist agreement
    Each question is tagged with:
      - "disagreement": true/false

Usage
-----
python -u scripts/create_100q_high_disagreement_dataset.py
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
OUTPUT_PATH = DATA_DIR / "medqa_us_100q_high_disagreement.json"


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
    target_total: int = 100
    target_disagreement: int = 80
    target_agreement: int = target_total - target_disagreement
    rng_seed: int = 42  # deterministic sampling/shuffling

    if not BALANCED_PATH.exists():
        raise FileNotFoundError(f"Balanced dataset not found at: {BALANCED_PATH}")
    if not CURATED_DISAGREEMENT_PATH.exists():
        raise FileNotFoundError(
            f"Curated disagreement dataset not found at: {CURATED_DISAGREEMENT_PATH}"
        )

    balanced_raw = load_json_any(BALANCED_PATH)
    curated_raw = load_json_any(CURATED_DISAGREEMENT_PATH)

    balanced = ensure_question_list(balanced_raw, context="balanced dataset")
    curated_disagreement = ensure_question_list(
        curated_raw, context="curated disagreement dataset"
    )

    print(f"Loaded balanced dataset: {len(balanced)} questions from {BALANCED_PATH}")
    print(
        f"Loaded curated disagreement dataset: {len(curated_disagreement)} questions "
        f"from {CURATED_DISAGREEMENT_PATH}"
    )

    if len(curated_disagreement) != target_disagreement:
        print(
            f"[WARN] Expected {target_disagreement} disagreement questions, "
            f"but found {len(curated_disagreement)}. Proceeding anyway."
        )
        target_disagreement = len(curated_disagreement)
        target_agreement = target_total - target_disagreement
        if target_agreement < 0:
            raise ValueError(
                "Curated disagreement set is larger than target_total; "
                "reduce target_total or regenerate curated set."
            )

    # Build a set of question texts for the curated disagreement questions
    disagreement_questions_text: Set[str] = {
        q["question"] for q in curated_disagreement if "question" in q
    }

    # Agreement candidates are questions from the balanced set that are not in the curated set
    agreement_candidates: List[Dict[str, Any]] = [
        q for q in balanced if q.get("question") not in disagreement_questions_text
    ]

    print(f"Agreement candidates (not in curated set): {len(agreement_candidates)}")

    if len(agreement_candidates) < target_agreement:
        raise ValueError(
            f"Not enough agreement candidates ({len(agreement_candidates)}) "
            f"to sample {target_agreement} questions."
        )

    rng = random.Random(rng_seed)
    sampled_agreement: List[Dict[str, Any]] = rng.sample(
        agreement_candidates, target_agreement
    )

    # Tag questions with disagreement flag
    tagged_disagreement = tag_questions(curated_disagreement, disagreement=True)
    tagged_agreement = tag_questions(sampled_agreement, disagreement=False)

    combined: List[Dict[str, Any]] = tagged_disagreement + tagged_agreement

    # Shuffle combined list deterministically for randomized order
    rng.shuffle(combined)

    # Sanity checks
    num_disagreement = sum(1 for q in combined if q.get("disagreement") is True)
    num_agreement = sum(1 for q in combined if q.get("disagreement") is False)

    print("Summary of combined 100-question dataset:")
    print(f"- Total questions: {len(combined)}")
    print(f"- Disagreement questions: {num_disagreement}")
    print(f"- Agreement questions: {num_agreement}")

    # Save output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"Saved 100-question high-disagreement dataset to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

