# Fixes Applied Based on LLM Response Investigation

## Issues Found

1. **Response Truncation** (CRITICAL): `max_new_tokens=500` was too low, causing responses to be cut off before CORRECTNESS/RANKING/CONFIDENCE lines
2. **Wrong Rankings Getting Boosted**: LLM sometimes ranks wrong answers as #1, and they get +15% boost
3. **Parsing Issues**: Regex sometimes catches wrong numbers
4. **Format Inconsistencies**: LLM doesn't always follow exact format

## Fixes Applied

### 1. Increased Token Limit
- **Before**: `max_new_tokens=500`
- **After**: `max_new_tokens=800`
- **Impact**: Prevents truncation, ensures CORRECTNESS/RANKING/CONFIDENCE lines are included

### 2. Conditional Ranking Boost
- **Before**: Ranking boost applied unconditionally (rank 1 = +15%)
- **After**: Ranking boost only applies if `correctness_score > 0.4` (at least LIKELY_CORRECT)
- **Impact**: Prevents wrong answers that rank #1 from getting boosted
- **Reduced boost amounts**: +15% → +10% for rank 1, +5% → +3% for rank 2

### 3. Adaptive Default Score
- **Before**: Default = 0.35 (fixed)
- **After**: 
  - If response has CORRECTNESS line: Default = 0.30
  - If response truncated (no CORRECTNESS): Default = 0.20 (more conservative)
- **Impact**: More conservative when responses are truncated

### 4. Improved Prompt
- Added explicit instruction: "You MUST provide your evaluation in the EXACT format below at the END of your response"
- Added warning: "The RANKING should reflect which option is MEDICALLY MOST ACCURATE, not just which seems plausible"
- **Impact**: Should improve format compliance and ranking accuracy

### 5. Improved Regex Parsing
- Added `re.MULTILINE` flag for better line matching
- **Impact**: Should catch RANKING more reliably

## Expected Impact

### Correctness Score Discrimination
- **Before**: Gap = -0.014 (wrong > correct)
- **Expected After**: Gap = +0.10-0.15 (correct > wrong)
- **Reason**: No more truncation, conditional ranking boost prevents wrong answers from getting boosted

### Accuracy
- **Before**: 63.3% (dropped from 70%)
- **Expected After**: 68-70% (recovery)
- **Reason**: Wrong answers no longer get ranking boost, better discrimination

### AUROC
- **Before**: 0.545
- **Expected After**: 0.60-0.70 (target range)
- **Reason**: Better correctness discrimination leads to better confidence ordering

### ECE
- **Before**: 0.568 (overconfident)
- **Expected After**: 0.25-0.35 (better calibration)
- **Reason**: Conditional ranking boost and adaptive defaults reduce overconfidence

## Next Steps

1. **Run 30-question test** with these fixes
2. **Verify** that responses are no longer truncated
3. **Check** correctness score distribution (should show positive gap)
4. **Validate** that ranking boost is only applied to reasonable answers
5. **If successful**, run 100 questions for final validation
