# Parameter Fixes Applied

## Date
2026-01-14

## Fixes Applied

### 1. Inconsistency Thresholds (More Lenient)

**Before**:
- YES: inconsistency < 0.5
- UNCERTAIN: inconsistency < 0.7
- NO: inconsistency >= 0.7

**After**:
- YES: inconsistency < 0.6
- UNCERTAIN: inconsistency < 0.8
- NO: inconsistency >= 0.8

**Rationale**: Reduce NO status rate from 57.5% to ~40% in degradations, preserving confidence distinction.

### 2. Adjustment Factors (Less Aggressive)

**Before**:
- NO: adjustment_factor = 0.3
- UNCERTAIN: adjustment_factor = 0.6
- YES: adjustment_factor = 1.0

**After**:
- NO: adjustment_factor = 0.5
- UNCERTAIN: adjustment_factor = 0.75
- YES: adjustment_factor = 1.0

**Rationale**: Preserve confidence distinction. NO status S scores will be ~0.25 instead of 0.15-0.18, allowing fusion to work.

### 3. Similarity Threshold (More Lenient)

**Before**: threshold = 0.5

**After**: threshold = 0.4

**Rationale**: Better matching of semantically similar answers that are worded differently.

### 4. Consistency Weight (Favor Initial Confidence)

**Before**: consistency_weight = 0.5 (equal weight)

**After**: consistency_weight = 0.65 (favor initial confidence)

**Rationale**: Initial confidence from specialist may be more reliable than verification confidence.

## Expected Impact

### Tier 1 Status Distribution
- **Before**: 57.5% NO, 15% UNCERTAIN, 27.5% YES (in degradations)
- **Expected**: ~40% NO, ~25% UNCERTAIN, ~35% YES

### S Score Distribution
- **Before**: NO mean=0.155, UNCERTAIN mean=0.403, YES mean=0.846
- **Expected**: NO mean=~0.25, UNCERTAIN mean=~0.45, YES mean=~0.85

### Accuracy
- **Before**: Tier 1 = 48%, Full Linear = 53%
- **Expected**: Tier 1 = 52-54%, Full Linear = 55-58%

## Next Steps

1. ✅ **Fixes applied** - Parameters updated in code
2. **Re-test** - Run 10-question test to verify improvements
3. **Full experiment** - Run 100-question experiment with fixed parameters
4. **Verify** - Check accuracy, ECE, AUROC improvements
