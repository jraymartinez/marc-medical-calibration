# Experiment Restarted with Corrected Parameters

## Date
2026-01-12

## Reason for Restart
Previous run showed 40.0% accuracy instead of expected 46.7% due to incorrect parameters.

## Parameters Corrected

### 1. Tier 2 Parameters
- **Before**: DEFAULT (temp=0.2, REJECTED=0.35, NEEDS_REVIEW=0.65)
- **After**: Less Aggressive (temp=0.25, REJECTED=0.5, NEEDS_REVIEW=0.75) ✅

### 2. Tier 1 Penalties
- **Before**: NO=0.1, UNCERTAIN=0.4
- **After**: NO=0.3, UNCERTAIN=0.6 ✅

## All Parameters Now Set

| Parameter | Value | Status |
|-----------|-------|--------|
| Alpha (α) | 0.6 | ✅ |
| Tier 2 Temperature | 0.25 | ✅ |
| Tier 2 REJECTED Penalty | 0.5 | ✅ |
| Tier 2 NEEDS_REVIEW Penalty | 0.75 | ✅ |
| Tier 1 Temperature | 0.2 | ✅ |
| Tier 1 NO Penalty | 0.3 | ✅ |
| Tier 1 UNCERTAIN Penalty | 0.6 | ✅ |
| Specialist Temperature | 0.3 | ✅ |
| Fusion Method | Highest Confidence | ✅ |

## Expected Results

Based on resume tuning run:
- **Accuracy**: 46.7% (vs 40.0% in previous run)
- **ECE**: 0.035 (excellent calibration)
- **AUROC**: 0.569 (improved discrimination)

## Experiment Status
🔄 **Running in background**
