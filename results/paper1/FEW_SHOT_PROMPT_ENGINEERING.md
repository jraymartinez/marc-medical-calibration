# Few-Shot Prompt Engineering for Tier 1 Correctness Checking

## Date: 2026-01-17

## Problem

We've been adjusting parameters (thresholds, penalties) but Tier 1 is still not beating baseline. The user correctly identified that this might be a **prompt engineering issue** rather than just parameter tuning.

## Solution: Add Few-Shot Examples

### Why Few-Shot?

1. **Clear Examples**: Shows the LLM exactly what we want
2. **Pattern Recognition**: Helps the LLM understand the evaluation criteria
3. **Better Accuracy**: Few-shot examples can significantly improve LLM performance
4. **Reduces Ambiguity**: Makes it clear what "CORRECT" vs "INCORRECT" means

### Few-Shot Examples Added

#### Example 1: CORRECT Answer
- Shows a clear correct answer with good reasoning
- Demonstrates when to mark as CORRECT with high confidence

#### Example 2: INCORRECT Answer (Wrong Medical Fact)
- Shows a wrong answer that seems plausible
- Demonstrates how to identify when reasoning is medically incorrect
- Shows how to identify the correct answer among options

#### Example 3: INCORRECT Answer (Close but Wrong)
- Shows a wrong answer that's close to correct
- Demonstrates how to catch subtle errors
- Shows the importance of medical accuracy over general reasoning

## Expected Impact

1. **Better Correctness Assessment**: LLM will better distinguish correct from incorrect answers
2. **Higher Accuracy on Correct Answers**: Few-shot examples guide the LLM to correctly identify correct answers
3. **Better Rejection of Wrong Answers**: Examples show how to catch wrong answers even with good reasoning

## Files Modified

1. `src/verification/tier1_verification.py`
   - Added 3 few-shot examples to `_check_answer_correctness` prompt
   - Examples cover: CORRECT, INCORRECT (wrong fact), INCORRECT (close but wrong)

## Next Steps

1. **Test with 10 questions** to see if few-shot examples improve Tier 1 correctness checking
2. **If successful, run full 100-question experiment**
3. **Expected**: Tier 1 should now better identify correct vs incorrect answers
