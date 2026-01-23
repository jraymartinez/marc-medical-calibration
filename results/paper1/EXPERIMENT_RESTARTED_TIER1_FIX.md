# Experiment Restarted with Tier 1 Penalty Fix

## Date
2026-01-12

## Critical Fix Applied

**Tier 1 Penalty Values Corrected**:
- **NO penalty**: 0.1 (was incorrectly 0.3)
- **UNCERTAIN penalty**: 0.4 (was incorrectly 0.6)

## Root Cause

The tuning summary documentation said NO=0.3, UNCERTAIN=0.6, but analysis of the actual tuning run S_scores revealed the real values were:
- NO: 0.1
- UNCERTAIN: 0.4

This discrepancy caused the optimized run to get 40.0% accuracy instead of 46.7%.

## All Parameters Now Correct

| Parameter | Value | Status |
|-----------|-------|--------|
| Alpha (α) | 0.6 | ✅ |
| Tier 2 Temperature | 0.25 | ✅ |
| Tier 2 REJECTED Penalty | 0.5 | ✅ |
| Tier 2 NEEDS_REVIEW Penalty | 0.75 | ✅ |
| Tier 1 Temperature | 0.2 | ✅ |
| **Tier 1 NO Penalty** | **0.1** | ✅ **FIXED** |
| **Tier 1 UNCERTAIN Penalty** | **0.4** | ✅ **FIXED** |
| Specialist Temperature | 0.3 | ✅ |
| Fusion Method | Highest Confidence | ✅ |
| Random Seed | 42 | ✅ |

## Expected Results

With all parameters matching the tuning run:
- **Accuracy**: 46.7% (vs 40.0% in previous run)
- **ECE**: 0.035 (excellent calibration)
- **AUROC**: 0.569 (improved discrimination)

## Experiment Status
🔄 **Running in background with corrected parameters**
