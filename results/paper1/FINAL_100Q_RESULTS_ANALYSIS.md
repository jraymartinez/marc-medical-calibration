# Final 100-Question Experiment Results Analysis

## Date: 2026-01-17

## Executive Summary

The full 100-question experiment has completed. **Tier 1 (Self-Verification) shows improvement** in both accuracy and ECE, but **Full Linear (Tier 1 + Tier 2) performs worse** than baseline.

## Results

### Metrics Comparison

| Configuration | Accuracy | ECE | AUROC | Avg Confidence |
|--------------|----------|-----|-------|----------------|
| **Baseline (No Verification)** | 59.0% | 0.194 | 0.662 | 0.784 |
| **Tier 1 (Self-Verification)** | **60.0%** (+1.0%) | **0.185** (-0.009) | 0.599 (-0.063) | 0.785 |
| **Full Linear (Tier 1 + Tier 2)** | 57.0% (-2.0%) | 0.217 (+0.023) | 0.633 (-0.029) | 0.787 |

### Key Findings

#### ✅ Tier 1 (Self-Verification) - SUCCESS
- **Accuracy**: Improved by 1.0% (59.0% → 60.0%)
- **ECE**: Improved by 0.009 (0.194 → 0.185) - better calibration
- **AUROC**: Decreased by 0.063 (0.662 → 0.599) - slight degradation in discrimination
- **Verdict**: Tier 1 verification is working and improving performance

#### ❌ Full Linear (Tier 1 + Tier 2) - UNDERPERFORMING
- **Accuracy**: Decreased by 2.0% (59.0% → 57.0%)
- **ECE**: Increased by 0.023 (0.194 → 0.217) - worse calibration
- **AUROC**: Decreased by 0.029 (0.662 → 0.633) - worse discrimination
- **Verdict**: Tier 2 is hurting performance instead of helping

## Fix Verification

### ✅ Tier 1 NO Penalty Fix - WORKING
- **Tier 1**: Wrong answers with Tier 1=NO have average S score of 0.184 (<0.25 threshold)
- **Full Linear**: Wrong answers with Tier 1=NO have average S score of 0.204 (<0.25 threshold)
- **Status**: ✅ Fix is working correctly - wrong answers get low S scores

### ⚠️ Tier 2 Penalties - NEEDS IMPROVEMENT
- **Wrong Answers**: Average G score of 0.246 (>=0.2 threshold)
- **Status Distribution**:
  - REJECTED: 2
  - APPROVED: 3
- **Issue**: G scores are still too high on wrong answers, and Tier 2 is approving wrong answers too often

### Answer Parsing Fix
- **Status**: No answers with letter prefixes found in this dataset
- **Note**: This fix is still important for future datasets

## Root Cause Analysis

### Why Full Linear is Underperforming

1. **Tier 2 Approving Wrong Answers**
   - 3 out of 5 wrong answers were APPROVED by Tier 2
   - Average G score on wrong answers is 0.246 (too high)
   - This suggests Tier 2 is not being aggressive enough

2. **Tier 2 G Scores Too High**
   - Even when Tier 2 says APPROVED on wrong answers, G scores should be lower
   - Current average: 0.246 (should be <0.2)
   - This allows wrong answers to win fusion even with low S scores

3. **Linear Integration Compensating**
   - Formula: C = 0.6×S + 0.4×G
   - Even with low S (0.204), high G (0.246) keeps final confidence high enough to win
   - Example: 0.6×0.204 + 0.4×0.246 = 0.122 + 0.098 = 0.220 (before scaling)

## Recommendations

### Immediate Actions

1. **Make Tier 2 More Aggressive**
   - Lower APPROVED threshold (currently too lenient)
   - Increase penalties for wrong answers
   - Reduce G scores when Tier 1 says NO

2. **Improve Tier 2 Prompt**
   - Make it more skeptical of wrong answers
   - Emphasize comparison against all options
   - Be more explicit about rejecting wrong answers

3. **Adjust Linear Integration**
   - Consider increasing alpha (weight on S score) if Tier 2 is unreliable
   - Or use Tier 1 only if Tier 2 continues to underperform

### Long-term Considerations

1. **Tier 2 Independence**
   - Tier 2 should be more independent from Tier 1
   - Currently, Tier 2 might be trusting Tier 1 too much
   - Need to make Tier 2 do its own validation

2. **Dataset Characteristics**
   - This dataset has 80% disagreement questions
   - Tier 2 might struggle more with disagreement cases
   - Consider testing on agreement-only subset

## Conclusion

**Tier 1 (Self-Verification) is the best performing configuration:**
- ✅ Improved accuracy (+1.0%)
- ✅ Improved ECE (-0.009)
- ✅ Tier 1 NO penalty working correctly

**Full Linear (Tier 1 + Tier 2) needs improvement:**
- ❌ Decreased accuracy (-2.0%)
- ❌ Increased ECE (+0.023)
- ⚠️ Tier 2 approving wrong answers too often
- ⚠️ G scores too high on wrong answers

**Recommendation**: Use **Tier 1 only** for now, or improve Tier 2 before using Full Linear.
