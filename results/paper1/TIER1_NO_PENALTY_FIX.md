# Tier 1 NO Penalty Fix - Prevent Wrong Answers from Winning Fusion

## Date: 2026-01-16

## Problem Identified

**Question 7 Analysis**:
- Wrong answer "D. Mi-2 protein" won fusion with 0.813 votes
- GP: Final=0.416 (S=0.406, G=0.190) - Tier 1 said NO, but S score still high
- Neurology: Final=0.397 (S=0.376, G=0.190) - Tier 1 said NO, but S score still high

**Root Cause**:
- Tier 1 NO penalty (0.5) is not aggressive enough
- S scores remain high (0.406, 0.376) even when Tier 1 says NO
- Even with low G scores (0.190), high S scores keep final confidence high enough to win fusion

**Calculation**:
- Initial confidence: ~1.0
- Verification confidence: ~0.5
- Combined: 0.65 × 1.0 + 0.35 × 0.5 = 0.825
- After NO penalty (0.5): 0.825 × 0.5 = 0.4125 ✓ (matches observed S=0.406)

## Fix Applied

### Updated Tier 1 NO Penalty (`src/verification/tier1_verification.py`)

**Before**:
- NO status: adjustment_factor = 0.5
- UNCERTAIN status: adjustment_factor = 0.75

**After**:
- NO status: adjustment_factor = **0.3** (more aggressive)
- UNCERTAIN status: adjustment_factor = **0.6** (more aggressive)

**Expected Impact**:
- S score with NO: 0.825 × 0.3 = 0.2475 (instead of 0.4125)
- Final confidence: 0.6 × 0.2475 + 0.4 × 0.190 = 0.2245
- After temperature scaling: 0.2245^(1/1.3) = 0.285 (instead of 0.416)

**This will make wrong answers have much lower final confidence, preventing them from winning fusion.**

## Expected Results

### Question 7 Scenario (After Fix)

**Before Fix**:
- GP: Final=0.416 (S=0.406, G=0.190) → Wrong answer won
- Neurology: Final=0.397 (S=0.376, G=0.190) → Wrong answer won

**After Fix** (Expected):
- GP: Final=~0.285 (S=~0.248, G=0.190) → Wrong answer won't win
- Neurology: Final=~0.280 (S=~0.247, G=0.190) → Wrong answer won't win

**Result**: Wrong answers will have much lower final confidence and won't win fusion.

## Files Modified

1. `src/verification/tier1_verification.py`
   - NO penalty: 0.5 → 0.3 (more aggressive)
   - UNCERTAIN penalty: 0.75 → 0.6 (more aggressive)

## Trade-offs

**Pros**:
- Wrong answers won't win fusion even when multiple specialists agree
- Better accuracy when Tier 1 correctly identifies wrong answers
- Works together with low G scores to prevent wrong answers

**Cons**:
- May reduce confidence too much for correct answers that Tier 1 incorrectly says NO
- Need to balance: catch wrong answers without penalizing correct ones too much

## Next Steps

1. **Re-test with 10 questions** to verify fix works
2. **Check if wrong answers still win fusion** - should be prevented now
3. **Check if correct answers are penalized too much** - may need adjustment
4. **If successful, run full 100-question experiment**
