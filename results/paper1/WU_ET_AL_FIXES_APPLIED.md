# Wu et al. Implementation Fixes Applied

## Problem Identified

**Root Cause**: Wu et al.'s method only checks **consistency**, not **correctness**. Wrong answers can be internally consistent, leading to high confidence scores.

**Evidence**:
- Q2: Wrong answer with inconsistency=0.000 → confidence=0.950
- Q4: Wrong answer with inconsistency=0.250 → confidence=0.847
- Mean inconsistency: 0.538, but many wrong answers have low inconsistency

## Fixes Applied

### 1. **Stricter Inconsistency Thresholds**
- **YES threshold**: `inconsistency_score < 0.15` (was 0.3) - Much stricter
- **UNCERTAIN threshold**: `inconsistency_score < 0.5` (was 0.6) - Stricter
- **Rationale**: Only answers with VERY low inconsistency should get YES status

### 2. **More Aggressive Adjustment Factors**
- **NO**: 0.3 (was 0.4) - More aggressive penalty
- **UNCERTAIN**: 0.6 (was 0.7) - More aggressive penalty
- **YES**: 0.85 (was 1.0) - **CRITICAL**: Even consistent answers get slight penalty
- **Rationale**: Even if an answer is consistent, it might be wrong. Apply slight penalty to account for this.

### 3. **Reduced Consistency Weight**
- **consistency_weight**: 0.5 (was 0.65)
- **Rationale**: Give more weight to verification confidence (inconsistency) and less to initial confidence

## Expected Impact

### Before Fixes:
- Accuracy: 56.7%
- ECE: 0.760
- AUROC: 0.561
- Wrong answers with inconsistency=0.000 → confidence=0.950

### After Fixes:
- **Accuracy**: Should improve (wrong but consistent answers will get lower confidence)
- **ECE**: Should improve (less overconfidence)
- **AUROC**: Should improve (better discrimination)
- **Wrong answers**: Even if consistent, will get lower confidence (0.85 penalty)

## Why This Should Work

1. **Stricter thresholds**: Fewer wrong answers will get YES status
2. **YES penalty**: Even consistent answers get 0.85 penalty, reducing confidence
3. **More weight to verification**: Inconsistency score has more impact on final S_score

## Next Steps

Run 30-question test to validate these fixes.
