# Improved Prompts Results Analysis

## Results Summary

**Latest Run** (`final_comparison_20260121_153413.json`):

| Configuration | Accuracy | ECE | AUROC | Change from Previous |
|--------------|----------|-----|-------|---------------------|
| Single Specialist | 70.0% | 0.759 | 0.455 | No change |
| Single Specialist + Two-Phase | 70.0% | 0.330 | **0.577** | ECE: 0.158→0.330 (worse), AUROC: 0.442→0.577 (better) |
| Multi-Agent (No Verification) | 70.0% | 0.781 | 0.458 | No change |
| **Multi-Agent + Two-Phase** | **63.3%** | **0.568** | **0.545** | **Accuracy: 70%→63.3% (worse), ECE: 0.279→0.568 (worse), AUROC: 0.519→0.545 (slightly better)** |

## Key Findings

### 1. **Accuracy Dropped for Multi-Agent + Two-Phase**
- **Before**: 70.0% (21/30 correct)
- **After**: 63.3% (19/30 correct)
- **Lost 2 questions** - This is concerning

### 2. **ECE Got Worse**
- **Before**: 0.279
- **After**: 0.568 (much worse!)
- **Confidence gap**: Only +0.006 (correct=0.603, wrong=0.597)
- The system is now **overconfident** - assigning high confidence (0.60) to both correct and wrong answers

### 3. **AUROC Improved Slightly**
- **Before**: 0.519
- **After**: 0.545
- **Still below target** (0.60-0.70)
- Confidence gap is still too small (+0.006)

### 4. **Correctness Scores Still Not Discriminating**
- **Correct answers**: mean correctness = 0.419 (n=6)
- **Wrong answers**: mean correctness = 0.433 (n=144)
- **Gap: -0.014** (WRONG answers still get HIGHER correctness scores!)

## What Went Wrong?

### Issue 1: Correctness Scores Still Inverted
The prompt improvements didn't fix the core problem - wrong answers are still getting higher correctness scores than correct ones. This suggests:
- The LLM evaluator is still not working correctly
- OR the ranking boost is being applied incorrectly
- OR the new statuses (PROBABLY_CORRECT, etc.) are not being parsed correctly

### Issue 2: Overconfidence
Confidence scores increased significantly (0.38 → 0.60), but discrimination didn't improve. This suggests:
- The ranking boost (+15% for rank 1) is being applied too aggressively
- OR the less conservative default (0.35) combined with boosts is pushing scores too high
- The system is now overconfident about wrong answers

### Issue 3: Accuracy Loss
Lost 2 correct answers, suggesting:
- The fusion override logic might be selecting wrong answers more often
- OR the higher confidence scores are causing wrong answers to win fusion
- OR the ranking boost is favoring wrong answers that happen to rank #1

## Root Cause Hypothesis

The improvements made the system **less conservative but not more accurate**:
1. **Default score increased** (0.20 → 0.35) - but this applies to both correct and wrong
2. **Ranking boost** (+15% for rank 1) - but if wrong answer ranks #1, it gets boosted
3. **Less aggressive penalties** - wrong answers are no longer penalized as much
4. **Result**: Wrong answers get higher scores, leading to overconfidence and accuracy loss

## What Needs to Be Fixed

### Priority 1: Fix Correctness Score Discrimination
- The correctness checker is still giving wrong answers higher scores
- Need to investigate why the LLM evaluator is ranking wrong answers #1
- May need to add more explicit instructions about what makes an answer correct

### Priority 2: Reduce Overconfidence
- The ranking boost might be too aggressive
- Consider reducing boost from +15% to +5-10%
- Or only apply boost if correctness score is already high (>0.5)

### Priority 3: Rebalance Defaults
- Default of 0.35 might be too high
- Consider 0.25-0.30 instead
- Or make default depend on whether answer matches an option

## Next Steps

1. **Check LLM responses** - See what correctness statuses and rankings the LLM is actually returning
2. **Adjust ranking boost** - Reduce from +15% to +5-10%, or make it conditional
3. **Fix correctness discrimination** - This is the core issue - wrong answers shouldn't rank #1
4. **Consider reverting some changes** - The less conservative approach might not work if the LLM evaluator isn't accurate

## Conclusion

The prompt improvements had **mixed results**:
- ✅ AUROC improved slightly (0.519 → 0.545)
- ❌ Accuracy dropped (70% → 63.3%)
- ❌ ECE got much worse (0.279 → 0.568)
- ❌ Correctness scores still not discriminating (gap still negative)

The system is now **less conservative but less accurate**. We need to find a balance - less conservative defaults but better discrimination between correct and wrong answers.
