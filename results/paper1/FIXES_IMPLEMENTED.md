# Fixes Implemented for Tier 1 + Tier 2 Improvements

## Date: 2026-01-15

## Summary

Implemented three critical fixes based on test results:
1. **Tier 1 Correctness Checker - More Aggressive**
2. **Tier 2 - More Independent Validation**
3. **ECE Degradation - Improved Calibration**

## Fix 1: Tier 1 Correctness Checker - More Aggressive

### Problem
- Wrong answers were getting high correctness scores (mean: 0.885)
- LLM was marking wrong answers as "CORRECT" even with stricter prompt
- Only 0/2 wrong answers had correctness <0.4 (should be most/all)

### Changes Made

#### 1. Updated Prompt (`src/verification/tier1_verification.py`)
- **Removed UNCERTAIN option**: Now only CORRECT/INCORRECT
- **Added explicit rule**: "If you are uncertain, mark as INCORRECT"
- **More aggressive language**: "BE EXTREMELY SKEPTICAL"
- **Critical rule**: "UNCERTAIN answers should be treated as INCORRECT unless you are very confident"

#### 2. Updated Parsing Logic
- **Default changed**: From 0.5 (uncertain) to 0.2 (INCORRECT) - conservative approach
- **UNCERTAIN treated as INCORRECT**: If LLM says UNCERTAIN, score = 0.2
- **Lowered CORRECT threshold**: From 0.9 to 0.85
- **Lowered INCORRECT score**: From 0.2 to 0.15
- **Tighter CORRECT range**: 0.75-0.90 (was 0.7-0.9)
- **Added uncertainty detection**: If response contains uncertainty indicators, reduce score by 30%

#### 3. Updated Verified Status Thresholds
- **YES threshold raised**: correctness > 0.7 (was > 0.6)
- **UNCERTAIN threshold raised**: correctness > 0.5 (was > 0.4)
- **More aggressive**: Requires higher correctness to get YES status

### Expected Impact
- Wrong answers should now get correctness scores <0.4
- More answers will be marked as INCORRECT (conservative approach)
- Better accuracy in identifying wrong answers

## Fix 2: Tier 2 - More Independent Validation

### Problem
- Tier 2 was trusting Tier 1's correctness assessment
- Tier 2 was approving wrong answers even when Tier 1 said they were correct (but Tier 1 was wrong)
- 2 wrong answers got APPROVED by Tier 2

### Changes Made

#### 1. Updated Prompt (`src/agents/prompts.py`)
- **Added explicit independence instruction**: "Do NOT trust Tier 1's correctness assessment"
- **Added validation steps**: "You must evaluate the answer yourself based on medical knowledge"
- **Raised APPROVED threshold**: From 0.7-0.9 to 0.8-0.9 (more strict)
- **More explicit skepticism**: "If you are uncertain, mark as NEEDS_REVIEW or REJECTED (not APPROVED)"
- **Independent validation steps**: Explicit 5-step process

#### 2. Updated Penalty Logic (`src/verification/tier2_validation.py`)
- **More aggressive penalties when Tier 1 says NO**:
  - REJECTED: 0.15 (was 0.2)
  - NEEDS_REVIEW: 0.4 (was 0.5)
- **APPROVED with Tier 1 issues**:
  - If Tier 1 says NO: 0.4 penalty (was 0.6)
  - If Tier 1 says UNCERTAIN: 0.7 penalty (new)
  - If Tier 1 says YES and correctness > 0.6: No penalty (both agree)

### Expected Impact
- Tier 2 will validate independently, not trusting Tier 1
- Wrong answers should get REJECTED more often
- Better accuracy in catching wrong answers

## Fix 3: ECE Degradation - Improved Calibration

### Problem
- ECE got worse: Tier 1 (0.209 → 0.366), Full Linear (0.209 → 0.330)
- Confidence scores are less calibrated (less reliable)
- Over-aggressive penalties may be causing poor calibration

### Changes Made

#### 1. Adjusted Temperature Scaling (`scripts/run_optimized_multi_specialist.py`)
- **Less aggressive scaling**: T=1.3 (was 1.5)
- **Preserves calibration better**: Less reduction in confidence
- **Added minimum floor**: 0.05 (prevents too-low scores)

#### 2. Added Confidence Floor (`src/verification/tier1_verification.py`)
- **Minimum S_score**: 0.05 (was 0.0)
- **Prevents too-low scores**: Helps preserve calibration
- **Better ECE**: Prevents extreme low scores that hurt calibration

### Expected Impact
- Better ECE (calibration)
- Confidence scores more reliable
- Less over-aggressive reduction in confidence

## Files Modified

1. `src/verification/tier1_verification.py`
   - Updated `_check_answer_correctness()` prompt and parsing
   - Updated verified status thresholds
   - Added confidence floor

2. `src/agents/prompts.py`
   - Updated `TIER2_VALIDATION_PROMPT` for independence

3. `src/verification/tier2_validation.py`
   - Updated penalty logic for more aggressive penalties
   - Added checks for Tier 1 status

4. `scripts/run_optimized_multi_specialist.py`
   - Adjusted temperature scaling (T=1.3)
   - Added minimum confidence floor

## Expected Results

### Tier 1 Correctness Checking
- ✅ Wrong answers should get correctness <0.4 (was 0.885)
- ✅ More answers marked as INCORRECT (conservative)
- ✅ Better identification of wrong answers

### Tier 2 Validation
- ✅ More independent validation (not trusting Tier 1)
- ✅ Wrong answers should get REJECTED more often
- ✅ Better accuracy in catching wrong answers

### ECE (Calibration)
- ✅ Better ECE (should be <0.3, was 0.366)
- ✅ More reliable confidence scores
- ✅ Better calibration

### Overall
- ✅ Accuracy should improve (verification catching wrong answers)
- ✅ AUROC should remain high (discrimination working)
- ✅ ECE should improve (calibration better)

## Next Steps

1. **Re-test with 10 questions** to verify fixes work
2. **Check Tier 1 correctness scores** - should be <0.4 for wrong answers
3. **Check Tier 2 status** - should REJECT more wrong answers
4. **Check ECE** - should be better than 0.366
5. **If successful, run full 100-question experiment**

## Testing Command

```bash
python scripts/test_tier1_tier2_improvements.py
```
