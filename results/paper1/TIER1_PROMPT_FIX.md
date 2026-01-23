# Tier 1 Prompt Fix - Addressing UNCERTAIN Overuse

## Date
2026-01-14

## Problem Identified

**Root Cause**: Tier 1 verification prompt was too conservative, causing LLM to return `UNCERTAIN` for almost all verifications (800/800 cases).

### Original Prompt Issues

1. **"BE SKEPTICAL"** - Encouraged finding problems
2. **"Say VERIFIED: UNCERTAIN if there are any doubts or alternative possibilities"** - This is too broad! Medical questions almost always have alternative possibilities
3. **"Only say VERIFIED: YES if you are highly confident"** - Too strict threshold
4. **"err on the side of lower confidence"** - Biased toward uncertainty

### Impact

- All specialists got similar low confidence (0.375-0.4)
- Fusion method couldn't distinguish between correct/incorrect answers
- **No accuracy improvement** (53% across all configs)
- Only 2 answer changes (net 0)

## Fix Applied

### Updated Prompt (src/agents/prompts.py)

**Key Changes**:
1. Removed "BE SKEPTICAL" language
2. Changed UNCERTAIN criteria: "only if the answer is ambiguous, the reasoning is unclear, or you genuinely cannot determine correctness"
3. Encouraged YES: "Say VERIFIED: YES if the answer is medically correct, well-reasoned, and appropriately addresses the question (even if other valid options exist)"
4. More balanced tone: "Be balanced: Medical questions often have multiple valid perspectives, but you should still make a clear decision when possible"

### New Prompt Text

```
You are a medical verification expert performing first-tier self-verification.
Your goal is to assess whether the proposed answer is medically sound and well-reasoned.

IMPORTANT DECISION CRITERIA:
- Say VERIFIED: YES if the answer is medically correct, well-reasoned, and appropriately addresses the question (even if other valid options exist)
- Say VERIFIED: UNCERTAIN only if the answer is ambiguous, the reasoning is unclear, or you genuinely cannot determine correctness
- Say VERIFIED: NO if you find clear medical errors, logical flaws, or the answer clearly does not address the question

Be balanced: Medical questions often have multiple valid perspectives, but you should still make a clear decision when possible.
```

## Expected Improvements

### Before Fix
- **YES**: 0 cases
- **NO**: 0 cases  
- **UNCERTAIN**: 800 cases (100%)

### After Fix (Expected)
- **YES**: 200-400 cases (25-50%)
- **NO**: 50-150 cases (6-19%)
- **UNCERTAIN**: 250-550 cases (31-69%)

### Expected Impact on Metrics

1. **Better Score Distinction**: 
   - YES → S_score ~0.6-0.8 (higher)
   - UNCERTAIN → S_score ~0.4-0.5 (medium)
   - NO → S_score ~0.15-0.3 (lower)

2. **More Answer Changes**:
   - Fusion can now distinguish between specialists
   - Should see 10-20 answer changes (vs 2 before)
   - Net accuracy improvement: +2-5%

3. **Better Calibration**:
   - ECE should improve with better confidence distinction
   - Target: <0.25 (from 0.265-0.269)

4. **Better Discrimination**:
   - AUROC should improve further
   - Target: >0.65 (from 0.611)

## Next Steps

1. **Re-run experiment** with fixed prompt
2. **Monitor Tier 1 status distribution** - should see more YES/NO
3. **Check answer changes** - should see more than 2
4. **Verify accuracy improvement** - should see >53%
5. **Confirm better score distinction** - S_scores should vary more

## Additional Considerations

### Temperature
- Current: 0.2 (conservative)
- Consider: 0.3-0.4 if still too conservative
- Balance: Need decisive answers but not random

### UNCERTAIN Penalty
- Current: `adjustment_factor = 0.5` (halves confidence)
- May need adjustment if UNCERTAIN rate is still high
- Consider: 0.6-0.7 if UNCERTAIN is used appropriately

### Verification Parsing
- Current regex: `r'VERIFIED:\s*(YES|NO|UNCERTAIN)'`
- Should work with new prompt
- Monitor for parsing failures

## Testing Plan

1. Run 10-question test with new prompt
2. Check Tier 1 status distribution
3. Verify S_score variation
4. If good, run full 100-question experiment
5. Compare metrics with previous run
