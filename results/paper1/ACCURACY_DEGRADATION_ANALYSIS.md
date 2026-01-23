# Accuracy Degradation Analysis and Parameter Fixes

## Date
2026-01-14

## Problem Summary

**Tier 1 accuracy degraded from 53% to 48% (-5%)**
**Full Linear accuracy stayed at 53% (no improvement)**

### Metrics
```
Configuration                    Accuracy    ECE      AUROC
Multi (No Verification)         53.0%      0.265    0.555
Multi + Tier 1                   48.0%      0.343    0.593  [DEGRADED]
Multi + Full Linear (Optimized)  53.0%      0.268    0.603  [NO IMPROVEMENT]
```

## Root Causes Identified

### 1. Tier 1 Degradations (10 cases)

**Pattern**: Baseline correct → Tier 1 wrong

**Key Findings**:
- **57.5% NO status** in degradations (23/40 specialist verifications)
- **Mean S score same as baseline** (0.382), but **distribution is wrong**
- **S scores by status**:
  - NO: mean=0.155 (too low, all specialists penalized)
  - UNCERTAIN: mean=0.403 (moderate)
  - YES: mean=0.846 (good, but only 27.5% of cases)

**Problem**: When all specialists get low S scores (NO status), fusion picks the wrong specialist because all confidences are similar (0.135-0.188 range).

**Example (Q1)**:
- Baseline: GP selected (correct answer "Haemophilus influenzae")
- Tier 1: All specialists got NO status → S scores: 0.150, 0.188, 0.188, 0.150
- Fusion picked Respiratory (0.188) → wrong answer "Streptococcus pneumoniae"

### 2. Full Linear Degradations (2 cases)

**Pattern**: Baseline correct → Full Linear wrong

**Key Findings**:
- **Tier 2 APPROVED 7/8 wrong answers** in degradations
- Tier 2 is not rejecting incorrect answers
- Tier 1 status: 2 NO, 4 UNCERTAIN, 2 YES (better than Tier 1 alone)
- But Tier 2 validation is too lenient

**Example (Q4)**:
- Correct: "Increase in length constant"
- Full Linear selected: "Decrease in transmembrane resistance" (Respiratory specialist)
- Respiratory got Tier 1: YES (S=0.825), Tier 2: APPROVED (G=0.850)
- But this is the WRONG answer!

### 3. Wrong Answers Have High Confidence

**Pattern**: Verification not reducing confidence enough for wrong answers

- **Tier 1 wrong answers**: 49/52 (94%) have confidence >0.6
- **Full Linear wrong answers**: 45/47 (96%) have confidence >0.6

**Problem**: Verification is not effectively identifying and penalizing wrong answers.

## Parameter Fixes Required

### Fix 1: Tier 1 Inconsistency Thresholds (Too Strict)

**Current**:
- YES: inconsistency < 0.5
- UNCERTAIN: inconsistency < 0.7
- NO: inconsistency >= 0.7

**Problem**: 57.5% NO status in degradations → all specialists penalized → wrong selection

**Recommended**:
- YES: inconsistency < 0.6 (more lenient)
- UNCERTAIN: inconsistency < 0.8 (more lenient)
- NO: inconsistency >= 0.8 (only very high inconsistency)

**Rationale**: More lenient thresholds will reduce NO status rate, preserving confidence distinction.

### Fix 2: Tier 1 Adjustment Factors (Too Aggressive for NO)

**Current**:
- NO: adjustment_factor = 0.3
- UNCERTAIN: adjustment_factor = 0.6
- YES: adjustment_factor = 1.0

**Problem**: NO status reduces S score to 0.135-0.188 range → all specialists similar → wrong selection

**Recommended**:
- NO: adjustment_factor = 0.5 (less aggressive, was 0.3)
- UNCERTAIN: adjustment_factor = 0.75 (less aggressive, was 0.6)
- YES: adjustment_factor = 1.0 (unchanged)

**Rationale**: Less aggressive penalties preserve confidence distinction, allowing fusion to work.

### Fix 3: Similarity Matching (Too Strict)

**Current**: threshold = 0.5 (Jaccard similarity)

**Problem**: Answers may be semantically similar but worded differently → marked as inconsistent

**Recommended**: threshold = 0.4 (more lenient)

**Rationale**: Better matching of semantically similar answers.

### Fix 4: Consistency Weight (Favor Initial Confidence)

**Current**: consistency_weight = 0.5 (equal weight)

**Problem**: Verification confidence may be unreliable, but we're giving it equal weight

**Recommended**: consistency_weight = 0.65 (favor initial confidence)

**Rationale**: Initial confidence from specialist may be more reliable than verification.

### Fix 5: Tier 2 Validation (Too Lenient)

**Current**: 
- REJECTED penalty: 0.4
- NEEDS_REVIEW penalty: 0.7
- APPROVED: no penalty

**Problem**: Tier 2 APPROVED 7/8 wrong answers in degradations

**Recommended**:
- Make Tier 2 more strict in validation
- Or: Adjust Tier 2 penalties to be more aggressive for wrong answers
- Check if Tier 2 prompt needs improvement

## Implementation Plan

### Step 1: Update Tier 1 Parameters

```python
# In src/verification/tier1_verification.py

# Inconsistency thresholds (more lenient)
if inconsistency_score < 0.6:  # was 0.5
    verified_status = "YES"
elif inconsistency_score < 0.8:  # was 0.7
    verified_status = "UNCERTAIN"
else:
    verified_status = "NO"

# Adjustment factors (less aggressive)
if verified_status == "NO":
    adjustment_factor = 0.5  # was 0.3
elif verified_status == "UNCERTAIN":
    adjustment_factor = 0.75  # was 0.6
else:
    adjustment_factor = 1.0

# Similarity threshold (more lenient)
def _answers_similar(self, answer1: str, answer2: str, threshold: float = 0.4):  # was 0.5

# Consistency weight (favor initial confidence)
consistency_weight: float = 0.65  # was 0.5
```

### Step 2: Review Tier 2 Validation

- Check Tier 2 prompt for leniency
- Consider making validation more strict
- Review Tier 2 penalties

### Step 3: Re-test with Fixed Parameters

1. Run 10-question test with new parameters
2. Verify improvements:
   - Reduced NO status rate
   - Better S score distribution
   - Fewer degradations
3. Run full 100-question experiment

## Expected Improvements

### With Fixed Parameters

**Tier 1**:
- NO status rate: 57.5% → ~40% (reduced)
- S score mean for NO: 0.155 → ~0.25 (higher, preserves distinction)
- Degradations: 10 → ~5 (reduced)

**Full Linear**:
- Tier 2 should reject more wrong answers
- Degradations: 2 → ~0 (eliminated)

**Overall Accuracy**:
- Tier 1: 48% → 52-54% (+4-6%)
- Full Linear: 53% → 55-58% (+2-5%)

## Next Steps

1. ✅ **Analysis complete** - Root causes identified
2. **Apply parameter fixes** - Update Tier 1 parameters
3. **Re-test** - 10-question test with new parameters
4. **Full experiment** - Run 100-question experiment
5. **Verify improvements** - Check accuracy, ECE, AUROC
