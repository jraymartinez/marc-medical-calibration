# Few-Shot + No YES Boost Results Analysis

## Date: 2026-01-17

## Test Results Summary

### Metrics Comparison

| Configuration | Accuracy | ECE | AUROC |
|--------------|----------|-----|-------|
| **Baseline** | 50.0% | 0.284 | 0.700 |
| **Tier 1** | 50.0% | **0.255 (-0.029)** | **0.880 (+0.180)** |
| **Full Linear** | 50.0% | **0.383 (+0.099)** | **0.880 (+0.180)** |

### Key Findings

#### ✅ Tier 1 - EXCELLENT!
- **ECE**: Improved from 0.284 → 0.255 (-0.029) - **Better calibration**
- **AUROC**: Improved from 0.700 → 0.880 (+0.180) - **Much better discrimination**
- **Status**: Tier 1 is now beating baseline on both ECE and AUROC!

#### ⚠️ Full Linear - Mixed Results
- **ECE**: Got worse from 0.284 → 0.383 (+0.099) - **Worse calibration**
- **AUROC**: Improved from 0.700 → 0.880 (+0.180) - **Much better discrimination**
- **Status**: Better discrimination but worse calibration

### Analysis

#### Tier 1 Success
- **Few-shot examples are working**: AUROC improved significantly (0.700 → 0.880)
- **Removing YES boost fixed ECE**: ECE improved (0.284 → 0.255)
- **Tier 1 is now better than baseline** on both ECE and AUROC

#### Full Linear Issue
- **AUROC improved**: 0.700 → 0.880 (same as Tier 1)
- **ECE got worse**: 0.284 → 0.383
- **Root cause**: Likely the linear integration (C = α×S + (1-α)×G) is causing overconfidence
  - When Tier 1 says YES and Tier 2 approves, confidence might be too high
  - Need to check if temperature scaling is being applied correctly

### Confidence Scores

From terminal output:
- **Question 7** (Correct): Tier 1 confidence = 0.668 (vs baseline 0.711) - lower, good
- **Question 10** (Correct): Tier 1 confidence = 0.845 (vs baseline 0.711) - higher, might be overconfident
- **Question 8** (Wrong): Tier 1 confidence = 0.631 (vs baseline 0.582) - higher, bad

**Issue**: Some wrong answers still have high confidence (0.631, 0.771, 0.780)

## Recommendations

### For Full Linear ECE Fix

1. **Check temperature scaling**: Ensure it's being applied correctly in Full Linear
2. **Check linear integration**: The formula C = 0.6×S + 0.4×G might be causing issues
3. **Apply more aggressive temperature scaling**: If confidence is too high, scale it down more

### Next Steps

1. **Fix Full Linear ECE** - investigate why it's worse
2. **Re-test with 10 questions** to verify fix
3. **If successful, run full 100-question experiment**

## Current Status

✅ **Tier 1 is working well**: Better than baseline on ECE and AUROC
⚠️ **Full Linear needs ECE fix**: Better AUROC but worse ECE
✅ **Few-shot examples are working**: Significant AUROC improvement
