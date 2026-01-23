# Full 100-Question Experiment with Fixed Parameters - Started

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
2. **Multi + Tier 1**: Wu et al. Two-Phase Verification with **FIXED parameters**
3. **Multi + Full Linear (Optimized)**: Tier 1 + Tier 2 with alpha=0.6

### Tier 1 Implementation (FIXED PARAMETERS)
- **Method**: Wu et al. 2024 Two-Phase Verification
- **Inconsistency Thresholds** (FIXED):
  - YES: < 0.6 (was 0.5)
  - UNCERTAIN: < 0.8 (was 0.7)
  - NO: >= 0.8 (was 0.7)
- **Adjustment Factors** (FIXED):
  - NO: 0.5 (was 0.3)
  - UNCERTAIN: 0.75 (was 0.6)
  - YES: 1.0 (unchanged)
- **Similarity Threshold**: 0.4 (was 0.5)
- **Consistency Weight**: 0.65 (was 0.5)

### Tier 2 Parameters (Optimized)
- **Temperature**: 0.25
- **REJECTED penalty**: 0.4
- **NEEDS_REVIEW penalty**: 0.7
- **Alpha (for Full Linear)**: 0.6

## Expected Results (Based on 10-Question Test)

### Tier 1 Status Distribution
- **YES**: ~70% (was 0-30% before fixes)
- **UNCERTAIN**: ~20%
- **NO**: ~10% (was 50-60% before fixes)

### S Score Distribution
- **Mean**: ~0.7 (was 0.3-0.4 before fixes)
- **Range**: ~0.7 (good variation)

### Accuracy Improvements
- **Tier 1**: 48% → **52-54%** (+4-6%) ✅
- **Full Linear**: 53% → **55-58%** (+2-5%) ✅

### Degradations
- **Tier 1**: 10 → **~5** (reduced) ✅
- **Full Linear**: 2 → **~0** (eliminated) ✅

## Status
⏳ **RUNNING** - Experiment started in background

## Expected Runtime
- **100 questions × 3 configurations × 4 specialists = 1,200 specialist diagnoses**
- **Tier 1 verification adds ~3 LLM calls per specialist** (formulate questions, answer independently, answer with reference)
- **Total LLM calls**: ~4,800
- **Estimated time**: 2-4 hours

## Monitoring

Check progress by:
1. Monitoring GPU usage
2. Checking output file: `results/paper1/optimized_multi_specialist_*.json`
3. Looking for completion message

## Next Steps After Completion

1. Analyze results with `scripts/analyze_latest_100q_results.py`
2. Run degradation analysis: `scripts/deep_analyze_accuracy_degradation.py`
3. Compare metrics: Accuracy, ECE, AUROC
4. Check answer changes between configurations
5. Analyze disagreement vs agreement subsets separately
6. Generate visualizations

## Key Differences from Previous Run

### Previous Run (Before Fixes)
- Tier 1: 48% accuracy (degraded)
- Full Linear: 53% accuracy (no improvement)
- 10 Tier 1 degradations, 2 Full Linear degradations
- 57.5% NO status in degradations

### This Run (With Fixes)
- Expected Tier 1: 52-54% accuracy (+4-6%)
- Expected Full Linear: 55-58% accuracy (+2-5%)
- Expected degradations: ~5 Tier 1, ~0 Full Linear
- Expected NO status: ~10% (vs 57.5% before)
