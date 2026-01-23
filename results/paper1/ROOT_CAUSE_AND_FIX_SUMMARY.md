# Root Cause Analysis: Why Wrong Answers Get High Correctness Scores

## Summary

**Root Cause Found**: The LLM evaluator is **confusing the proposed answer with what it thinks is the correct answer**.

## The Bug

When testing with a **wrong answer** (B. Levodopa), the LLM response showed:

```
**Comparison with Proposed Answer:**
The proposed answer is D. Penicillamine, which ranks #1.
**Accuracy and Appropriateness:**
The proposed answer is CORRECT.
...
CORRECTNESS: CORRECT
```

**But we passed "B" (Levodopa) as the proposed answer!**

The LLM:
1. Correctly identifies D (Penicillamine) as the correct answer
2. Then **incorrectly thinks that's what was proposed**
3. Marks it as CORRECT
4. Wrong answer B gets high correctness score (0.475)

## Impact

This explains why:
- **95/108 wrong answers** have correctness score of exactly **0.484**
- Wrong answers are getting **LIKELY_CORRECT** or **UNCERTAIN** status instead of **INCORRECT**
- The correctness gap is **negative** (-0.006) - wrong answers score higher than correct ones
- All wrong cases use `max_s_override_majority` - fusion is selecting wrong specialists with high S_scores

## Fixes Applied

### 1. **Made Prompt Explicit About Proposed Answer**
- Added bold emphasis: `**PROPOSED ANSWER TO EVALUATE: {answer}**`
- Added critical instruction: "You MUST evaluate ONLY the answer '{answer}' above. Do NOT evaluate what you think the correct answer should be."

### 2. **Added Critical Step to Identify Proposed Answer**
- Step 4: "Identify which option is the proposed answer '{answer}' from the list above."
- Explicit instruction: "DO NOT confuse the proposed answer with what you think is correct"

### 3. **Updated Example to Be Clearer**
- Example 2 now explicitly states: "The proposed answer is A. Alpha toxin, but... Therefore, the proposed answer A is wrong."

### 4. **Fixed Ranking Boost Bug** (from previous fix)
- Ranking boost now only applies if `correctness_score > 0.4` at application time
- Prevents wrong answers that rank #1 from getting boosted

## Expected Impact

After these fixes:
- **Correctness gap**: -0.006 → +0.10-0.15 (wrong answers will be marked as INCORRECT)
- **Accuracy**: 66.7% → 70-73% (fusion won't select wrong answers as often)
- **AUROC**: 0.560 → 0.65-0.70 (better discrimination)
- **ECE**: 0.521 → 0.30-0.40 (less overconfidence)

## Next Steps

1. **Test with fixed prompt** - Run a 30-question test to validate the fix
2. **Monitor LLM responses** - Check if it's now correctly evaluating the proposed answer
3. **If still issues** - May need to add validation to check if LLM is evaluating the right answer
