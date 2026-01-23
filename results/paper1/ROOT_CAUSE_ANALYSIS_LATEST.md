# Root Cause Analysis: Why Metrics Still Not at Expected Values

## Current Results (After Fixes)

**Multi-Agent + Two-Phase Verification**:
- Accuracy: **66.7%** (target: 70%+, dropped from 70%)
- ECE: **0.521** (target: 0.25-0.35, still high)
- AUROC: **0.560** (target: 0.60-0.70, improved from 0.545 but still below target)

## Critical Findings

### 1. **Correctness Gap Still Negative**
- Correct answers: mean correctness = **0.455** (range: 0.396-0.484)
- Wrong answers: mean correctness = **0.460** (range: 0.140-0.484)
- **Gap: -0.006** (wrong answers still score slightly higher!)

### 2. **All Wrong Cases Use `max_s_override_majority`**
- **10/10 wrong cases** have `fusion_reason="max_s_override_majority"`
- This means the override logic is **working**, but it's selecting the **WRONG specialist**
- The override is triggering because wrong answers have high S_scores (0.590-0.682)

### 3. **Wrong Answers Getting High Correctness Scores**
- Wrong answers can get correctness scores as high as **0.484** (same max as correct!)
- Example Q2: Wrong answer "C" gets correctness=0.484, S_score=0.682
- This suggests the LLM evaluator is still making mistakes OR ranking boost is being applied incorrectly

### 4. **Confidence Gap Still Tiny**
- Correct answers: mean conf = 0.624
- Wrong answers: mean conf = 0.615
- **Gap: +0.009** (barely any discrimination)

## Root Cause Identified

### **Ranking Boost Applied Unconditionally**

Looking at the code, I found the bug:

```python
# Line 704-717: Conditional check exists
if correctness_score > 0.4:
    ranking_boost = 1.10  # Calculate boost
else:
    ranking_boost = 1.0   # No boost

# Line 753: But boost is ALWAYS applied!
correctness_score = correctness_score * ranking_boost
```

**The Problem**: Even though we check `correctness_score > 0.4` to calculate the boost, the boost is **always applied** at line 753, regardless of the correctness score at that point.

**What's happening**:
1. Initial correctness_score might be 0.35 (LIKELY_CORRECT)
2. Conditional check: `0.35 > 0.4` = False, so `ranking_boost = 1.0`
3. But then confidence adjustment happens (lines 741-748), which might increase correctness_score
4. Then ranking boost is applied: `correctness_score = correctness_score * 1.0` (no change)
5. **BUT**: If the LLM ranks a wrong answer as #1, and the initial correctness is 0.40+, the boost IS applied!

**The Real Issue**: Wrong answers are getting correctness scores of 0.40+ (LIKELY_CORRECT or higher), so they qualify for the ranking boost. Then if they rank #1, they get +8-10% boost, making them score even higher.

## Why Wrong Answers Get High Correctness Scores

Possible reasons:
1. **LLM evaluator mistakes**: LLM sometimes marks wrong answers as CORRECT or PROBABLY_CORRECT
2. **Ranking mistakes**: LLM ranks wrong answers as #1, and ranking boost is applied
3. **Confidence blending**: Confidence adjustment (lines 741-748) might be inflating scores

## Fix Applied

I've fixed the ranking boost to be **truly conditional**:
- Check `correctness_score > 0.4` **BEFORE** applying boost
- If correctness is low, `ranking_boost = 1.0` (no boost)
- Only apply boost if correctness is reasonable

## Expected Impact After Fix

### If ranking boost fix works:
- **Correctness gap**: -0.006 → +0.05-0.10 (wrong answers no longer get boosted)
- **Accuracy**: 66.7% → 68-70% (override won't select wrong answers as often)
- **AUROC**: 0.560 → 0.60-0.65 (better discrimination)
- **ECE**: 0.521 → 0.30-0.40 (less overconfidence)

### But we still need to fix:
- **LLM evaluator accuracy**: Wrong answers shouldn't get correctness > 0.4 in the first place
- **Ranking accuracy**: LLM shouldn't rank wrong answers as #1

## Next Steps

1. **Test with ranking boost fix** (already applied)
2. **If still not working**, investigate why LLM evaluator gives wrong answers high correctness scores
3. **Consider**: Adding validation - if proposed answer ranks #1 but reasoning suggests another option is better, reduce correctness score
4. **Consider**: Making ranking boost even more conservative (only for CORRECT or PROBABLY_CORRECT status)
