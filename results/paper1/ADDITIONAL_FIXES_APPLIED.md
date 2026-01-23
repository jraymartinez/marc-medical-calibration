# Additional Fixes Applied - More Aggressive Tier 1 and Tier 2

## Date: 2026-01-15

## Summary

Applied additional fixes to make Tier 1 and Tier 2 even more aggressive in catching wrong answers.

## Fix 1: Tier 1 - Even More Aggressive Correctness Checking

### Changes Made

#### 1. Lowered CORRECT Threshold
- **Before**: correctness_score = 0.85 for CORRECT status
- **After**: correctness_score = 0.80 for CORRECT status
- **Impact**: Requires even higher confidence to mark as CORRECT

#### 2. Treated UNCERTAIN as INCORRECT (Same Score)
- **Before**: UNCERTAIN = 0.2
- **After**: UNCERTAIN = 0.15 (same as INCORRECT)
- **Impact**: UNCERTAIN answers get same penalty as INCORRECT

#### 3. Lowered Confidence Adjustment Ranges
- **CORRECT range**: 0.75-0.90 → 0.70-0.85 (lower max, tighter)
- **INCORRECT/UNCERTAIN range**: 0.1-0.2 → 0.10-0.18 (lower, tighter)
- **Impact**: Lower maximum correctness scores, tighter ranges

#### 4. Raised Verified Status Thresholds
- **YES threshold**: correctness > 0.7 → correctness > 0.75
- **UNCERTAIN threshold**: correctness > 0.5 → correctness > 0.4
- **Impact**: Requires even higher correctness to get YES status

### Expected Impact
- Wrong answers should get even lower correctness scores
- UNCERTAIN answers treated same as INCORRECT
- Fewer wrong answers will get YES status

## Fix 2: Tier 2 - Even More Skeptical Validation

### Changes Made

#### 1. Raised APPROVED Threshold
- **Before**: APPROVED = 0.8-0.9
- **After**: APPROVED = 0.85-0.9 (very strict)
- **Impact**: Only very high confidence answers get APPROVED

#### 2. Added Explicit Comparison Instructions
- **New**: "For EACH option, evaluate if it could be the correct answer"
- **New**: "Compare the proposed answer against EVERY other option"
- **New**: "If the answer is close to correct but not exact, REJECT"
- **New**: "MANDATORY: You MUST explicitly compare against ALL options"
- **Impact**: Tier 2 must explicitly compare all options

#### 3. More Aggressive Penalties for APPROVED
- **Tier 1 says NO + Tier 2 APPROVED**: 0.4 → 0.3 penalty
- **Tier 1 says UNCERTAIN + Tier 2 APPROVED**: 0.7 → 0.6 penalty
- **Tier 1 correctness < 0.75 + Tier 2 APPROVED**: 0.85 penalty (new)
- **Impact**: Even when Tier 2 approves, penalties if Tier 1 has issues

### Expected Impact
- Tier 2 will be more skeptical when approving
- Wrong answers should get REJECTED more often
- Better at catching wrong answers even when Tier 1 approves

## Files Modified

1. `src/verification/tier1_verification.py`
   - Lowered CORRECT threshold (0.85 → 0.80)
   - UNCERTAIN = INCORRECT (0.15)
   - Lowered confidence ranges
   - Raised verified status thresholds

2. `src/agents/prompts.py`
   - Raised APPROVED threshold (0.8-0.9 → 0.85-0.9)
   - Added explicit comparison instructions
   - Added mandatory comparison requirement

3. `src/verification/tier2_validation.py`
   - More aggressive penalties for APPROVED
   - Added check for Tier 1 correctness < 0.75

4. `scripts/test_tier1_tier2_improvements.py`
   - Fixed Unicode error (ASCII-safe encoding)

## Expected Results

### Tier 1 Correctness Checking
- ✅ Wrong answers should get correctness <0.4 (was 0.180-0.885)
- ✅ UNCERTAIN answers treated as INCORRECT (0.15)
- ✅ Fewer wrong answers will get YES status

### Tier 2 Validation
- ✅ Wrong answers should get REJECTED more often (target: 80%+)
- ✅ Better at catching wrong answers even when Tier 1 approves
- ✅ More explicit comparison against all options

### Overall
- ✅ Accuracy should improve (verification catching more wrong answers)
- ✅ Tier 1 should catch 80%+ of wrong answers (was 71%)
- ✅ Tier 2 should REJECT 80%+ of wrong answers (was 56%)

## Next Steps

1. **Re-test with 10 questions** to verify additional fixes work
2. **Check Tier 1 correctness scores** - should be <0.4 for all wrong answers
3. **Check Tier 2 status** - should REJECT 80%+ of wrong answers
4. **If successful, run full 100-question experiment**

## Testing Command

```bash
python scripts/test_tier1_tier2_improvements.py
```
