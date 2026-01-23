# Multi-Specialty Filtering Complete

## Date
2026-01-13

## Status
✅ **COMPLETE** - Filtering finished successfully

## Results

### Datasets Processed

1. **MedQA-USMLE** (English) ✅
   - dev: 849/1,272 (66.7%)
   - test: 849/1,273 (66.7%)
   - train: 6,812/10,178 (66.9%)

2. **MedQA-Mainland** (Chinese) ❌ **EXCLUDED**
   - Skipped - Llama struggles with Chinese

3. **MedQA-Taiwan** (English) ✅
   - dev: 452/1,412 (32.0%)
   - test: 489/1,413 (34.6%)
   - train: 3,795/11,297 (33.6%)
   - Filtered out 1 Chinese question from train

4. **MedMCQA** (English/Hindi) ✅
   - dev: 593/4,183 (14.2%)
   - test: 717/6,150 (11.7%)
   - train: 31,654/182,822 (17.3%)

## Total Filtered
**~43,000 questions** (Respiratory, Cardiology, or Neurology)

## Output
Saved to: `data/filtered/multi_specialty_cases_all.json`

## Next Step
Run Phase 2: Find disagreement cases from this filtered dataset
```bash
python scripts/create_curated_disagreement_dataset.py
```
