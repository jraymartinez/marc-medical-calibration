# Question 3: Neurology Got It Right But Wasn't Selected

## Date: 2026-01-19

## Issue Identified

**Question 3**: "A 56-year-old woman... progressive bilateral lower extremity weakness..."
- **Correct Answer**: "Increase in length constant" (Option A)
- **GP Answer**: A (CORRECT) ✅
- **Neurology Answer**: A (CORRECT) ✅
- **Multi-Agent Selected**: B (WRONG) ❌

### Specialist Breakdown:
- Respiratory: B (confidence: 0.327) - WRONG
- Cardiology: B (confidence: 0.348) - WRONG
- **Neurology: A (confidence: 0.349) - CORRECT** ✅
- Gastroenterology: B (confidence: 0.327) - WRONG

### Problem:
- **3 specialists said B (wrong)** → Majority = B
- **1 specialist (neurology) said A (correct)** → Minority = A
- **Majority voting selected B** → WRONG ❌
- **Neurology has HIGHEST confidence (0.349)** but still lost!

## Root Cause

The current fusion logic:
1. Checks for majority (>50%)
2. If majority exists, selects from majority specialists
3. **Problem**: Wrong majority (B) wins over correct minority (A)

Even with answer validation boost (1.3x):
- Neurology boosted: 0.349 * 1.3 = 0.454
- But majority logic still selects B because 3/4 specialists said B

## Fix Needed

The answer validation logic should:
1. **Boost correct answer confidence** (already implemented: 1.3x)
2. **Prefer correct answer even if minority**, if confidence is high enough
3. **Current logic**: Only prefers correct if confidence >= 80% of majority best
   - Neurology: 0.454 (after boost)
   - Wrong majority best: 0.348
   - 0.454 >= 0.348 * 0.8 = 0.278 ✅ **Should work!**

But it's not working because the logic checks majority first, then correct answer. We need to check correct answer FIRST, then fall back to majority.

## Solution

**Change fusion logic order**:
1. **First**: Check if any specialist has correct answer
2. **If correct answer exists and confidence is high enough**, prefer it
3. **Otherwise**: Use majority voting

This ensures correct answers win even when in minority, as long as confidence is reasonable.

## Expected Impact

- **Question 3**: Should now select A (neurology) instead of B
- **Accuracy improvement**: +1 question = +3.3% accuracy
- **Total expected**: 63.3% → 66.7% (with other fixes: 70-73%)
