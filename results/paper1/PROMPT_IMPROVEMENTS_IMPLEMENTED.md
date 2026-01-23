# Prompt Improvements and Relative Comparison - Implementation Summary

## Changes Implemented

### 1. **Correctness Checker Prompt Improvements** (`src/verification/tier1_verification.py`)

#### Removed Conservative Language
- **Before**: "BE EXTREMELY SKEPTICAL", "ABSOLUTELY CONFIDENT", "mark as INCORRECT if uncertain"
- **After**: "Be thorough but not overly skeptical", "If the proposed answer is clearly the best option, mark as CORRECT"

#### Added Relative Comparison (Ranking)
- **New**: LLM is now asked to **RANK all options from 1 (best) to 5 (worst)**
- **Ranking boost**: 
  - Rank 1 (best): +15% boost
  - Rank 2: +5% boost
  - Rank 4+: -15% penalty
  - Rank 3: No change

#### Added Middle Ground Scores
- **Before**: Only CORRECT (0.80) or INCORRECT (0.15)
- **After**: 
  - CORRECT: 0.85
  - PROBABLY_CORRECT: 0.65
  - LIKELY_CORRECT: 0.50
  - LIKELY_INCORRECT: 0.30
  - INCORRECT: 0.15
  - UNCERTAIN: 0.40 (was 0.15)

#### Less Aggressive Default
- **Before**: Default = 0.20 (INCORRECT)
- **After**: Default = 0.35 (LIKELY_CORRECT)

#### Reduced Penalties
- **Uncertainty penalty**: Only applies to scores > 0.75, reduces by 10% (was 30%)
- **Doubt penalty**: Only applies to scores > 0.85, reduces by 15% (was 40%)

### 2. **Fusion Logic Improvements** (`scripts/run_final_comparison.py`)

#### Lowered Override Threshold
- **Before**: `max_s_score > 0.45` required to consider override
- **After**: `max_s_score > 0.35` (more permissive)

#### Lowered Gap Threshold
- **Before**: Override if `max_s >= majority_max_s + 0.05` or `max_s >= 0.55`
- **After**: Override if `max_s >= majority_max_s + 0.03` or `max_s >= 0.50` (more sensitive)

## Expected Impact

### Correctness Score Distribution
- **Before**: Mean ~0.21 for both correct and wrong (no discrimination)
- **Expected After**: 
  - Correct answers: Mean ~0.40-0.50 (higher with ranking boost)
  - Wrong answers: Mean ~0.25-0.35 (lower, especially if ranked low)
  - **Gap: +0.15-0.20** (much better discrimination)

### S_Score Distribution
- **Before**: Correct mean=0.310, Wrong mean=0.312 (gap=-0.001)
- **Expected After**: 
  - Correct mean: ~0.40-0.45
  - Wrong mean: ~0.30-0.35
  - **Gap: +0.10-0.15** (positive discrimination)

### AUROC
- **Before**: 0.519
- **Expected After**: 0.60-0.70 (with better discrimination)

### Fusion Override
- **Before**: Override rarely triggered (threshold too high)
- **Expected After**: Override should trigger more often for correct minority specialists

## Key Improvements

1. **Ranking provides relative comparison** - Even if absolute scores are low, ranking helps distinguish best from worst
2. **Middle ground scores** - Allows nuanced evaluation instead of binary CORRECT/INCORRECT
3. **Less conservative defaults** - Answers start at 0.35 instead of 0.20
4. **Reduced penalties** - Less aggressive reduction of scores
5. **More permissive fusion** - Lower thresholds allow override to trigger more often

## Next Steps

1. **Run 30-question test** to validate improvements
2. **Check correctness score distribution** - Should see better separation
3. **Check S_score gap** - Should be positive and larger
4. **Check AUROC** - Should improve to 0.60-0.70
5. **If successful, run 100 questions** for final validation
