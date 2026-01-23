# Adjustment Factor Impact Analysis

## Key Finding: **YES, adjustment factors are making things WORSE!**

## Evidence

### 1. **Discrimination Gap Comparison**

**Without adjustment factors** (simulated):
- Wrong answers: mean S_score = **0.559**
- Correct answers: mean S_score = **0.600**
- **Gap: 0.042** (some discrimination)

**With adjustment factors** (current):
- Wrong answers: mean S_score = **0.588**
- Correct answers: mean S_score = **0.612**
- **Gap: 0.024** (less discrimination!)

**Conclusion**: Adjustment factors are **reducing discrimination** by 57% (0.024 vs 0.042)!

### 2. **Wrong Answers with YES Status**

5 wrong answers have YES status (low inconsistency):
- Mean S_score: **0.891** (very high!)
- Mean inconsistency: **0.200** (low)
- Adjustment factor: **0.85** (slight penalty)

**Problem**: Even with 0.85 penalty, wrong but consistent answers still get very high S_scores (0.891).

### 3. **Specific Case: Q2**

- Wrong answer with inconsistency=0.000 (perfect consistency)
- initial=1.000, verif=1.000
- **Without adjustment**: S=1.000
- **With adjustment (0.85)**: S=1.000 (should be 0.85!)
- **Difference: 0.000** (adjustment not working!)

**This suggests the adjustment factor isn't being applied correctly, or there's clamping happening.**

## Root Cause

The adjustment factors are:
1. **Not helping**: They reduce discrimination (gap: 0.024 vs 0.042)
2. **Not working correctly**: Q2 shows S=1.000 even with 0.85 adjustment
3. **Making wrong answers worse**: Wrong answers with YES status get 0.891 (too high)

## Why Adjustment Factors Don't Help

1. **Wrong but consistent answers** get YES status → 0.85 adjustment → still high confidence
2. **Correct but inconsistent answers** get NO status → 0.3 adjustment → low confidence
3. **Net effect**: Reduces discrimination because it penalizes correct inconsistent answers more than wrong consistent answers

## Recommendation

**Remove adjustment factors entirely** and use:
```python
S_score = 0.5 * initial_confidence + 0.5 * verification_confidence
```

This would:
- Improve discrimination (gap: 0.042 vs 0.024)
- Simplify the method
- Be closer to what Wu et al. actually describe (they don't mention adjustment factors)

## Alternative: Use Inconsistency Directly

Even simpler approach (closer to Wu et al.):
```python
S_score = initial_confidence * (1 - inconsistency_score)
```

This directly uses inconsistency as uncertainty measure, as Wu et al. describe.
