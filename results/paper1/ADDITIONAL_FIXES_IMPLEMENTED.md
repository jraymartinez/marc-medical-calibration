# Additional Fixes Implemented - Exact Match, Close Match Penalties, Tier 2 Aggressiveness

## Date: 2026-01-16

## Summary

Applied three additional fixes based on re-test results:
1. **Exact Match Checking - Strip Letter Prefixes**
2. **Tier 1 - Penalize Close But Not Exact Matches**
3. **Tier 2 - More Aggressive When Tier 1 Says UNCERTAIN**

## Fix 1: Exact Match Checking - Strip Letter Prefixes

### Problem
- "D. Mi-2 protein" was matching "Mi-2 protein" (partial match)
- Answer validation was using partial matching, causing false positives
- Need exact match only to prevent wrong answers from being boosted

### Changes Made (`scripts/run_optimized_multi_specialist.py`)

1. **Strip Letter Prefixes Before Comparing**
   - Remove letter prefixes like "A. ", "B. ", "C. ", "D. " at the start
   - Use regex: `re.sub(r'^[A-Z]\.\s*', '', answer, flags=re.IGNORECASE)`
   - Apply to both answer and correct answer

2. **Exact Match Only**
   - Changed from partial matching to exact matching
   - `is_correct = (answer_lower == correct_lower)` (was partial match)
   - Prevents "D. Mi-2 protein" from matching "Mi-2 protein"

### Expected Impact
- "D. Mi-2 protein" will NOT match "Mi-2 protein" (exact match required)
- Answer validation will only boost truly correct answers
- Prevents false positives from close matches

## Fix 2: Tier 1 - Penalize Close But Not Exact Matches

### Problem
- "D. Mi-2 protein" got correctness=0.505-0.590 (too high for wrong answer)
- Close matches were getting high correctness scores
- Need to penalize answers that don't match any option exactly

### Changes Made (`src/verification/tier1_verification.py`)

1. **Check if Answer Matches Any Option Exactly**
   - Strip letter prefixes from answer and all options
   - Check if answer matches any option exactly (case-insensitive)
   - If answer doesn't match any option exactly, reduce correctness by 50%

2. **Penalize Letter-Prefixed Answers**
   - If answer has letter prefix (e.g., "D. Mi-2 protein") and correctness > 0.7
   - Check if stripped answer matches any option exactly
   - If not, reduce correctness by 40%

### Expected Impact
- "D. Mi-2 protein" will get lower correctness score if it doesn't match "Mi-2 protein" exactly
- Wrong answers that are close but not exact will be penalized
- Better identification of wrong answers

## Fix 3: Tier 2 - More Aggressive When Tier 1 Says UNCERTAIN

### Problem
- Tier 2 was approving wrong answers even when Tier 1 said UNCERTAIN
- Question 7: Tier 1=UNCERTAIN, Tier 2=APPROVED (wrong answer)
- Need Tier 2 to be more skeptical when Tier 1 has doubts

### Changes Made

#### 1. Updated Tier 2 Prompt (`src/agents/prompts.py`)
- Added explicit instruction: "If Tier 1 says UNCERTAIN or NO, you should STRONGLY CONSIDER REJECTING"
- "Tier 1 UNCERTAIN means there are doubts - you should be skeptical and likely REJECT"
- "Only APPROVE if you are ABSOLUTELY CERTAIN the answer is correct despite Tier 1's doubts"

#### 2. Updated Tier 2 Penalty Logic (`src/verification/tier2_validation.py`)
- **NEEDS_REVIEW with Tier 1 UNCERTAIN**: 0.7 → 0.5 penalty (more aggressive)
- **APPROVED with Tier 1 UNCERTAIN**: 0.6 → 0.4 penalty (very aggressive)
- Tier 2 should REJECT when Tier 1 says UNCERTAIN, not APPROVE

### Expected Impact
- Tier 2 will REJECT more often when Tier 1 says UNCERTAIN
- Wrong answers won't get APPROVED when Tier 1 has doubts
- Better validation when Tier 1 is uncertain

## Files Modified

1. `scripts/run_optimized_multi_specialist.py`
   - Strip letter prefixes before exact match checking
   - Changed to exact match only (no partial matches)

2. `src/verification/tier1_verification.py`
   - Check if answer matches any option exactly
   - Penalize answers that don't match exactly

3. `src/verification/tier2_validation.py`
   - More aggressive penalties when Tier 1 says UNCERTAIN
   - NEEDS_REVIEW: 0.5 penalty (was 0.7)
   - APPROVED: 0.4 penalty (was 0.6)

4. `src/agents/prompts.py`
   - Added explicit instruction to REJECT when Tier 1 says UNCERTAIN

5. `scripts/test_tier1_tier2_improvements.py`
   - Updated to use exact match checking

## Expected Results

### Exact Match Checking
- ✅ "D. Mi-2 protein" will NOT match "Mi-2 protein"
- ✅ Answer validation will only boost truly correct answers
- ✅ Prevents false positives from close matches

### Tier 1 Close Match Penalties
- ✅ "D. Mi-2 protein" will get lower correctness score
- ✅ Wrong answers that are close but not exact will be penalized
- ✅ Better identification of wrong answers

### Tier 2 Aggressiveness
- ✅ Tier 2 will REJECT more often when Tier 1 says UNCERTAIN
- ✅ Wrong answers won't get APPROVED when Tier 1 has doubts
- ✅ Better validation when Tier 1 is uncertain

## Next Steps

1. **Re-test with 10 questions** to verify all fixes work
2. **Check Question 7** - "D. Mi-2 protein" should get lower correctness
3. **Check Tier 2** - should REJECT more when Tier 1 says UNCERTAIN
4. **If successful, run full 100-question experiment**

## Testing Command

```bash
python scripts/test_tier1_tier2_improvements.py
```
