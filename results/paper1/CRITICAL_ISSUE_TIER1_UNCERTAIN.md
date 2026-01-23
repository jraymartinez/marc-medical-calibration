# Critical Issue: Tier 1 Verification Returns UNCERTAIN for Everything

## Date
2026-01-14

## Problem Summary

**Tier 1 verification is running but returning `UNCERTAIN` status for almost all verifications**, causing:
- All specialists to get similar low confidence scores (0.375-0.4)
- Fusion method cannot distinguish between correct and incorrect answers
- **No accuracy improvement** (53% across all configurations)
- Only 2 answer changes (1 improvement, 1 degradation = net 0)

## Evidence

### Tier 1 Status Distribution
From comprehensive diagnosis:
- **Almost all verifications**: `verified_status: UNCERTAIN`
- **Scores**: All specialists get 0.375-0.4 confidence (very similar)
- **Result**: Fusion method can't pick the correct specialist

### Metrics Comparison
```
Configuration                    Accuracy    ECE      AUROC
Multi (No Verification)         53.0%      0.265    0.555
Multi + Tier 1                   53.0%      0.264    0.526  (worse AUROC!)
Multi + Full Linear (Optimized)  53.0%      0.269    0.611  (better AUROC, same accuracy)
```

### Answer Changes
- **Tier 1 vs Baseline**: 1 change (0 net improvement)
- **Full Linear vs Baseline**: 2 changes (1 improvement, 1 degradation = 0 net)

## Root Cause

### Why UNCERTAIN is Problematic

1. **UNCERTAIN penalty**: When Tier 1 returns UNCERTAIN, `adjustment_factor = 0.5`
   - This halves the confidence: `S_score = (0.5 * initial + 0.5 * verification) * 0.5`
   - With initial confidence ~0.7-1.0, this results in S_score ~0.375-0.4

2. **All specialists get similar scores**: 
   - When all specialists have confidence 0.375-0.4, fusion can't distinguish
   - Confidence-weighted voting sums similar values → same ranking
   - Highest confidence selection picks first specialist (arbitrary)

3. **Verification doesn't help**:
   - Can't identify correct answers (all look equally uncertain)
   - Can't reject wrong answers (all get same penalty)
   - Only adjusts confidence uniformly → no answer changes

## Why This Happens

### Possible Causes

1. **Tier 1 prompt too conservative**: 
   - LLM is hesitant to say YES or NO
   - Defaults to UNCERTAIN for ambiguous cases
   - Medical questions are inherently uncertain → LLM reflects this

2. **Verification parsing issue**:
   - May not be correctly extracting YES/NO from LLM response
   - Default fallback is UNCERTAIN

3. **Temperature too low**:
   - Current: 0.2 (very conservative)
   - May cause LLM to be overly cautious

4. **Prompt design**:
   - May not encourage definitive YES/NO answers
   - May need more explicit instructions

## Impact on Results

### Accuracy
- **No improvement**: All configurations = 53%
- **Disagreement subset**: All = 50% (80 questions)
- **Verification not helping**: Can't identify correct answers

### Calibration (ECE)
- **Slight improvement**: 0.265 → 0.264 → 0.269
- **Not significant**: Still high ECE (~0.26)
- **Overconfidence persists**: Avg confidence ~0.79-0.80

### Discrimination (AUROC)
- **Tier 1 worse**: 0.555 → 0.526 (degradation!)
- **Full Linear better**: 0.555 → 0.611 (improvement)
- **But no accuracy gain**: Better discrimination doesn't help if answers don't change

## Solutions

### Option 1: Fix Tier 1 Prompt (Recommended)
- Make prompt more explicit about YES/NO decisions
- Reduce ambiguity in verification instructions
- Add examples of clear YES/NO responses
- Encourage definitive answers when possible

### Option 2: Adjust UNCERTAIN Penalty
- Current: `adjustment_factor = 0.5` (too aggressive)
- Consider: `adjustment_factor = 0.7` (less aggressive)
- Or: Different handling for UNCERTAIN vs NO

### Option 3: Improve Verification Parsing
- Check if LLM is actually returning YES/NO but parser misses it
- Improve regex patterns for extraction
- Add fallback logic

### Option 4: Temperature Tuning
- Current: 0.2 (very conservative)
- Try: 0.3-0.4 (more decisive)
- Balance between accuracy and decisiveness

### Option 5: Two-Stage Verification
- Stage 1: Binary YES/NO (is answer plausible?)
- Stage 2: Confidence refinement (how confident?)
- Separate concerns to get clearer decisions

## Immediate Actions

1. **Check Tier 1 prompt**: Review `get_verification_prompt(tier=1)` 
2. **Check parsing**: Review `_parse_verification()` method
3. **Sample LLM responses**: See what LLM actually returns
4. **Test with higher temperature**: Try 0.3-0.4
5. **Adjust UNCERTAIN handling**: Make it less aggressive

## Expected Outcome After Fix

- **More YES/NO decisions**: Less UNCERTAIN responses
- **Better score distinction**: Different specialists get different S_scores
- **Answer changes**: Verification can pick correct specialist
- **Accuracy improvement**: Should see 2-5% improvement
- **Better calibration**: ECE should improve with better confidence distinction

## Next Steps

1. Investigate Tier 1 prompt and parsing
2. Test with modified prompt/temperature
3. Re-run experiment with fixes
4. Verify that Tier 1 returns more YES/NO decisions
5. Confirm accuracy improvement
