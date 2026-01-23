# Fixes for AUROC and ECE Issues

## Date: 2026-01-19

## Issues Identified

### Issue 1: AUROC = 0.5 (Weak Discrimination)
- **Root Cause**: Confidence scores for correct (0.279) and wrong (0.238) answers are almost identical (gap = 0.041)
- **Impact**: Confidence scores don't help distinguish correct from wrong answers

### Issue 2: ECE Calculation Bug
- **Root Cause**: Answer matching in metrics.py doesn't handle letter vs full text
- **Impact**: ECE calculation is incorrect (shows 0.00 accuracy in bins)

### Issue 3: ECE = 0.267 (Can Be Improved)
- **Current**: Good improvement from baseline (0.869), but can be better
- **Problem**: 20/21 correct answers have confidence < 0.5 (underconfidence)

## Fixes Applied

### Fix 1: Answer Matching in Metrics ✅
- **Updated**: `calculate_accuracy()`, `calculate_confidence_metrics()`, `calculate_auroc()`
- **Change**: Now handles letter-to-text conversion and normalization
- **Impact**: ECE and AUROC calculations will be accurate

### Fix 2: Reduce Temperature Scaling ✅
- **Before**: `temperature_scale = 1.5` (too aggressive)
- **After**: `temperature_scale = 1.2` (less aggressive)
- **Impact**: Correct answers maintain higher confidence, better discrimination

### Fix 3: Increase Two-Phase Boost ✅
- **Before**: Boost factor = 1.2 (high) / 1.1 (medium)
- **After**: Boost factor = 1.3 (high) / 1.2 (medium)
- **Impact**: Two-Phase verified answers get higher confidence, better discrimination

## Expected Results After Fixes

### Before:
- Accuracy: 70.0%
- ECE: 0.267 (but calculation might be wrong)
- AUROC: 0.500 (weak discrimination)

### After (Expected):
- Accuracy: 70-73% (maintain or improve)
- ECE: 0.15-0.20 (better calibration, accurate calculation)
- AUROC: 0.65-0.75 (good discrimination)

### Confidence Distribution (Expected):
- Correct answers: Mean confidence → 0.4-0.5 (up from 0.279)
- Wrong answers: Mean confidence → 0.2-0.3 (similar to 0.238)
- **Gap increases**: 0.041 → 0.2+ (better discrimination)

## Next Steps

1. ✅ Fixes applied
2. ⏳ Re-run 30-question experiment
3. ⏳ Verify AUROC improves (0.5 → 0.65+)
4. ⏳ Verify ECE improves (0.267 → 0.15-0.20)
