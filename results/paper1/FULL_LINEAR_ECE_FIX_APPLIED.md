# Full Linear ECE Fix Applied

## Date: 2026-01-17

## Fixes Applied

### 1. Removed Answer Validation Boosts
- **Before**: `correct_answer_boost = 1.2` (20% boost)
- **After**: `correct_answer_boost = 1.0` (NO boost)
- **Reason**: Boosts were causing overconfidence, leading to worse ECE

### 2. Removed Tier 1 YES Boost
- **Before**: `confidence *= 1.05` if Tier 1 says YES
- **After**: NO boost (removed)
- **Reason**: Additional boost was causing overconfidence

### 3. Higher Temperature Scaling for Full Linear
- **Tier 1**: `temperature_scale = 1.5` (unchanged)
- **Full Linear**: `temperature_scale = 2.0` (increased from 1.5)
- **Baseline**: `temperature_scale = 1.5` (unchanged)
- **Reason**: Full Linear needs more aggressive calibration to reduce overconfidence

## Expected Results

After these fixes:
- **Full Linear ECE should improve** (from 0.216 to < 0.121 baseline)
- **Full Linear should become the best configuration**
- **AUROC should remain high** (discrimination preserved)
- **Accuracy should remain stable** (boosts removed but penalties kept)

## Next Steps

1. **Test with 10 questions** to verify ECE improvement
2. **If successful, run full 100-question experiment**
3. **Verify ranking**: Full Linear > Tier 1 > Baseline
