# 10-Question Test Results Analysis - After Tier 2 Aggressive Fixes V2

## Date: 2026-01-17

## Test Results Summary

### Metrics Comparison

| Configuration | Accuracy | ECE | AUROC |
|--------------|----------|-----|-------|
| **Baseline** | 50.0% | 0.284 | 0.700 |
| **Tier 1** | 50.0% | 0.282 (-0.002) | 0.640 (-0.060) |
| **Full Linear** | 50.0% | 0.289 (+0.005) | 0.640 (-0.060) |

### Key Findings

#### ✅ Tier 1 - Working Well
- **Accuracy**: Maintained at 50.0%
- **ECE**: Improved slightly (0.284 → 0.282)
- **Status**: Working as expected

#### ⚠️ Full Linear - Needs Improvement
- **Accuracy**: Maintained at 50.0% (no improvement)
- **ECE**: Got worse (0.284 → 0.289)
- **Status**: Not improving over baseline

### Tier 2 Status on Wrong Answers

From terminal output:
- **Question 6**: Tier 2 APPROVED wrong answers (Respiratory and Neurology) with G=0.190
- **Tier 1 Status**: NO for both specialists
- **Issue**: Tier 2 is approving wrong answers even when Tier 1 says NO

**However**, detailed analysis shows:
- No wrong answers were approved when Tier 1 says NO (in final answer selection)
- This suggests the issue might be with individual specialist outputs, not final fusion

### Analysis

1. **Tier 2 is still approving wrong answers** in some cases (Question 6)
2. **G scores are 0.190** - penalties are being applied (0.95 × 0.2 = 0.19)
3. **But Tier 2 shouldn't approve at all** when Tier 1 says NO

### Issues Identified

1. **Tier 2 Prompt**: May not be strict enough about rejecting when Tier 1 says NO
2. **Tier 2 Penalties**: G score of 0.190 is still too high - should be <0.1
3. **Tier 2 Status**: Should force REJECTED when Tier 1 says NO, not just apply penalty

## Recommendations

### Immediate Fixes Needed

1. **Make Tier 2 ALWAYS REJECT when Tier 1 says NO**
   - Current: Apply penalty (G_score *= 0.2)
   - Proposed: Force REJECTED status or apply very aggressive penalty (G_score *= 0.05)

2. **Lower G Score Threshold**
   - Current: G=0.190 when Tier 1=NO and Tier 2=APPROVED
   - Target: G<0.1 for wrong answers

3. **Improve Tier 2 Prompt**
   - Make it explicit: "If Tier 1 says NO, you MUST REJECT"
   - Don't allow APPROVED when Tier 1 says NO

### Next Steps

1. **Apply additional fixes** to make Tier 2 more aggressive when Tier 1 says NO
2. **Re-test with 10 questions** to verify fixes
3. **If successful, proceed with full 100-question experiment**

## Conclusion

The fixes for UNCERTAIN status are working, but **Tier 2 is still approving wrong answers when Tier 1 says NO**. This needs to be fixed before running the full experiment.
