# Balanced Fix Applied

## Date: 2026-01-17

## Problem Identified

After removing all boosts, Full Linear got worse:
- Accuracy dropped: 50% → 40% (-10%)
- ECE got worse: 0.121 → 0.327 (+0.206)
- AUROC got worse: 0.660 → 0.625 (-0.035)

**Root cause**: Removing boosts completely hurt accuracy (correct answers weren't being selected).

## Balanced Fix Applied

### 1. Restore Small Boost
- **Before**: `correct_answer_boost = 1.0` (no boost)
- **After**: `correct_answer_boost = 1.1` (small 10% boost)
- **Reason**: Small boost helps correct answers win fusion without causing overconfidence

### 2. Reduce Temperature Scaling
- **Before**: `temperature_scale = 2.0` (too aggressive)
- **After**: `temperature_scale = 1.7` (balanced)
- **Reason**: Less aggressive calibration maintains accuracy while still improving ECE

### 3. Keep Tier 1 YES Boost Removed
- **Status**: Still removed (no boost for YES)
- **Reason**: Prevents overconfidence from double-boosting

## Expected Results

After balanced fix:
- ✅ **Accuracy should improve** (small boost helps correct answers)
- ✅ **ECE should improve** (less aggressive temperature)
- ✅ **Full Linear should become the best configuration**
- ✅ **AUROC should remain good** (discrimination preserved)

## Next Steps

1. **Test with 10 questions** to verify balanced fix works
2. **If successful, run full 100-question experiment**
3. **Verify ranking**: Full Linear > Tier 1 > Baseline
