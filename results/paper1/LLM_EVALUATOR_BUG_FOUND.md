# Critical Bug Found: LLM Evaluator Confusing Proposed Answer

## The Problem

When testing the correctness checker with a **wrong answer** (B. Levodopa), the LLM response shows:

```
**Comparison with Proposed Answer:**
The proposed answer is D. Penicillamine, which ranks #1.
**Accuracy and Appropriateness:**
The proposed answer is CORRECT.
...
CORRECTNESS: CORRECT
```

**But we passed "B" (Levodopa) as the proposed answer!**

The LLM is **not evaluating the actual proposed answer**. Instead, it's:
1. Identifying the correct answer (D. Penicillamine)
2. Then incorrectly thinking that's what was proposed
3. Marking it as CORRECT

## Root Cause

The prompt might not be clear enough about:
1. **What the proposed answer is** - The LLM might be confusing it with the correct answer
2. **The distinction between proposed answer and correct answer** - The LLM might be evaluating what it thinks should be the answer, not what was actually proposed

## Impact

This explains why wrong answers are getting high correctness scores (0.484):
- LLM identifies the correct answer
- LLM thinks that's what was proposed
- LLM marks it as CORRECT or PROBABLY_CORRECT
- Wrong answer gets high correctness score

## Fix Needed

1. **Make the prompt more explicit** about what the proposed answer is
2. **Add explicit instruction** to evaluate ONLY the proposed answer, not what the LLM thinks should be the answer
3. **Add validation** to ensure the LLM is evaluating the correct proposed answer
4. **Add examples** showing wrong proposed answers being marked as INCORRECT

## Test Case

**Question**: Wilson's disease question
**Proposed Answer**: B (Levodopa) - **WRONG**
**Correct Answer**: D (Penicillamine)

**LLM Response**: 
- Correctly identifies D as correct
- But says "The proposed answer is D" (WRONG - proposed was B)
- Marks as CORRECT (WRONG - should be INCORRECT)

**Result**: Wrong answer B gets correctness score of 0.475 (should be ~0.15)
