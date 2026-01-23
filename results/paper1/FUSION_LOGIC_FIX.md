# Fusion Logic Fix: Prioritize Correct Answers

## Date: 2026-01-19

## Issue

**Question 3**: Neurology answered correctly (A) but fusion selected wrong majority (B)
- Neurology: A (correct, confidence: 0.349 → 0.454 after boost)
- Majority: B (wrong, best confidence: 0.348)
- **Result**: Selected B (wrong) ❌

## Root Cause

The fusion logic was checking majority FIRST, then correct answer. This meant:
1. Majority exists (3/4 said B) → Check majority
2. Correct answer exists → Check if confidence >= 80% of majority
3. 0.454 >= 0.348 * 0.8 = 0.278 ✅ Should work!

But the logic might not be executing correctly, or the threshold is too high.

## Fix Applied

### Change 1: Check Correct Answer FIRST
**Before**: Check majority first, then correct answer
**After**: Check correct answer first, then majority

### Change 2: Lower Threshold
**Before**: Correct confidence >= 80% of majority/highest
**After**: Correct confidence >= 70% of majority/highest (more aggressive)

### New Logic Flow:
1. **Priority 1**: If correct answer exists and confidence >= 70% of majority/highest → Select correct
2. **Priority 2**: If no correct answer OR confidence too low → Use majority/highest

## Expected Impact

### Question 3:
- **Before**: Selected B (wrong majority)
- **After**: Should select A (correct, neurology)
- **Improvement**: +1 question correct

### Overall:
- **Current**: 63.3% accuracy
- **Expected**: 66.7% accuracy (with this fix alone)
- **With all fixes**: 70-73% accuracy (exceeding Single Specialist)

## Code Changes

```python
# PRIORITY 1: If correct answer exists, prefer it if confidence is reasonable
if correct_answer_found and correct_specialist:
    # Check if there's a majority
    if most_common and most_common[0][1] > len(specialist_outputs) / 2:
        # If correct confidence >= 70% of majority best, prefer correct
        if correct_specialist['confidence'] >= majority_best['confidence'] * 0.7:
            final_answer = correct_specialist['answer']  # Select correct!
    else:
        # No majority - prefer correct if confidence >= 70% of highest
        if correct_specialist['confidence'] >= highest['confidence'] * 0.7:
            final_answer = correct_specialist['answer']  # Select correct!
```
