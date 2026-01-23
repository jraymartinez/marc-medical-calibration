# Disagreement Finding Started

## Date
2026-01-13

## Dataset
- **Source**: MedQA-US Train Set (balanced)
- **Total questions**: 600
- **Distribution**: 
  - Respiratory: 200
  - Cardiology: 200
  - Neurology: 200
- **File**: `data/filtered/medqa_us_train_balanced.json`

## Process
Running `scripts/create_curated_disagreement_dataset_test.py` to:
1. Process each of the 600 questions
2. Get answers from 4 specialists (GP, Respiratory, Cardiology, Neurology)
3. Identify questions where specialists disagree
4. Save disagreement cases

## Expected Results
- **Processing time**: 2-4 hours (600 questions × 4 specialists × ~1-2 sec/question)
- **Expected disagreement rate**: 5-10% = 30-60 disagreement cases
- **Output**: `data/filtered/curated_disagreement_train_test.json`

## Status
⏳ **RUNNING** - Process started in background
