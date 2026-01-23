# Full Linear ECE Root Cause Analysis

## Date: 2026-01-17

## Current Results

| Configuration | Accuracy | ECE | AUROC | Rank |
|--------------|----------|-----|-------|------|
| Tier 1 | 50.0% | 0.139 | 0.880 | **1st** |
| Baseline | 50.0% | 0.121 | 0.660 | 2nd |
| Full Linear | 40.0% | **0.462** | 0.667 | 3rd |

## Root Cause Identified

### Problem 1: Wrong Answers Getting High Confidence
- **Question 6**: Wrong answer "Alpha toxin" has confidence **0.622** (very high!)
- **Question 9**: Wrong answer has confidence **0.639** (very high!)
- **Impact**: High confidence on wrong answers → terrible ECE (0.462)

### Problem 2: Correct Answers Changed to Wrong
- **Question 3**: Baseline CORRECT → Full Linear WRONG
- **Question 7**: Baseline CORRECT → Full Linear WRONG
- **Impact**: Accuracy dropped from 50% → 40% (-10%)

### Problem 3: Confidence Distribution
- **Correct answers**: Avg confidence = 0.501 (reasonable)
- **Wrong answers**: Avg confidence = 0.438 (too high for wrong!)
- **Baseline comparison**: Wrong answers have 0.437 (similar), but Full Linear has more wrong answers

## Why This Is Happening

1. **Fusion selecting wrong answers**: Full Linear's fusion method is picking wrong answers over correct ones
2. **Temperature scaling not helping**: Even with T=1.7, wrong answers still get high confidence
3. **Boosts/penalties not effective**: The 1.1 boost and 0.8 penalty aren't preventing wrong answers from winning

## Solution Needed

The core issue is that **Full Linear's fusion is selecting wrong answers**. We need to:

1. **Make Tier 2 more aggressive** when it sees wrong answers
2. **Make Tier 1 more aggressive** on wrong answers
3. **Improve answer validation** to better identify correct answers
4. **Check if fusion method is correct** - maybe we need to use a different fusion strategy

## Next Steps

1. Investigate why fusion is selecting wrong answers
2. Check if Tier 2 is properly rejecting wrong answers
3. Verify that answer validation is working correctly
4. Consider using a different fusion method (e.g., require majority agreement)
