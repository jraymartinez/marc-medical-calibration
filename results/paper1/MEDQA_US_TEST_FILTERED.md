# MedQA-US Test Set Filtered

## Date
2026-01-13

## Results

### Filtering Statistics
- **Total questions**: 1,273
- **Filtered**: 849 (66.7%)
- **Output**: `data/filtered/medqa_us_test_filtered.json`

### By Specialty
- **Respiratory**: 70 questions
- **Cardiology**: 339 questions
- **Neurology**: 57 questions
- **Multiple specialties**: 383 questions

## Next Step
Run disagreement finding on these 849 filtered questions:
```bash
python scripts/create_curated_disagreement_dataset_test.py
```

## Expected Results
- Processing time: 30-60 minutes
- Expected disagreement cases: 30-50 (5-10% disagreement rate)
- Output: `data/filtered/curated_disagreement_test.json`
