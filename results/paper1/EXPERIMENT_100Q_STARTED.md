# 100-Question Experiment Started

## Date
2026-01-12

## Configuration

- **Questions**: 100 (scaled up from 30 for statistical power)
- **Configurations**: 3 (No Verification, Tier 1, Full Linear)
- **Bayesian**: Removed (focusing on Full Linear)
- **Random Seed**: 42 (same as tuning run)

## Expected Runtime

- **Total**: ~6 hours 9 minutes
- **Breakdown**:
  - No Verification: ~1.5 hours
  - Tier 1: ~2.0 hours
  - Full Linear: ~2.5 hours
  - Model Loading: ~9 minutes

## Expected Results

With 100 questions, we should see:
- **Statistical Power**: ~80% to detect 3.4% improvement
- **Expected Accuracy**: 
  - Baseline: 43.3%
  - Full Linear: 46.7% (+3.4% improvement)
- **Better Calibration**: ECE ~0.057 (vs 0.502 baseline)
- **Better Discrimination**: AUROC ~0.554 (vs 0.468 baseline)

## Parameters

All optimized parameters are set:
- Alpha: 0.6
- Tier 2: temp=0.25, REJECTED=0.5, NEEDS_REVIEW=0.75
- Tier 1: temp=0.2, NO=0.1, UNCERTAIN=0.4
- Specialist: temp=0.3
- Fusion: Highest Confidence Selection

## Status

🔄 **Running in background**
