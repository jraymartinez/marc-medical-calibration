# Full 100-Question Experiment Started

## Date
2026-01-14

## Experiment Configuration

### Dataset
- **File**: `data/filtered/medqa_us_100q_high_disagreement.json`
- **Total Questions**: 100
- **Composition**: 
  - 80 disagreement questions (80%)
  - 20 agreement questions (20%)
- **Specialties**: Respiratory, Cardiology, Neurology (balanced)

### Configurations
1. **Multi (No Verification)**: Baseline
2. **Multi + Tier 1**: Wu et al. Two-Phase Verification only
3. **Multi + Full Linear (Optimized)**: Tier 1 + Tier 2 with alpha=0.6

### Tier 1 Implementation
- **Method**: Wu et al. 2024 Two-Phase Verification
- **Steps**:
  1. Formulate verification questions from explanation
  2. Answer questions independently (without reference)
  3. Answer questions with reference to explanation
  4. Measure inconsistencies → uncertainty score

### Tier 1 Thresholds (Adjusted)
- **YES**: inconsistency < 0.5
- **UNCERTAIN**: inconsistency < 0.7
- **NO**: inconsistency >= 0.7
- **Adjustment factors**: NO=0.3, UNCERTAIN=0.6, YES=1.0

### Tier 2 Parameters (Optimized)
- **Temperature**: 0.25
- **REJECTED penalty**: 0.4
- **NEEDS_REVIEW penalty**: 0.7
- **Alpha (for Full Linear)**: 0.6

### Expected Results

Based on 10-question test:
- **Tier 1 Status Distribution**: ~30% YES, ~10% UNCERTAIN, ~60% NO
- **S Score Range**: 0.135-0.950 (excellent variation)
- **S Score Mean**: ~0.4

Expected improvements:
- **Accuracy**: 53% → 55-58% (+2-5%)
- **ECE**: Should improve with better confidence distinction
- **AUROC**: Should improve with varied S scores

## Status
⏳ **RUNNING** - Experiment started in background

## Expected Runtime
- **100 questions × 3 configurations × 4 specialists = 1,200 LLM calls**
- **Estimated time**: 2-4 hours
- **Tier 1 verification adds ~3 LLM calls per specialist** (formulate questions, answer independently, answer with reference)
- **Total LLM calls**: ~4,800 (including Tier 1 verification steps)

## Monitoring

Check progress by:
1. Monitoring GPU usage
2. Checking output file: `results/paper1/optimized_multi_specialist_*.json`
3. Looking for completion message

## Next Steps After Completion

1. Analyze results with `scripts/analyze_latest_100q_results.py`
2. Compare metrics: Accuracy, ECE, AUROC
3. Check answer changes between configurations
4. Analyze disagreement vs agreement subsets separately
5. Generate visualizations
