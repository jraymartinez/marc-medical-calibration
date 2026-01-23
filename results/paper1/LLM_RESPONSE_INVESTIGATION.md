# LLM Response Investigation - Key Findings

## Test Results Summary

I tested the correctness checker on 3 questions with both correct and wrong answers. Here's what I found:

### Question 1 (Vaccine Question) - ✅ WORKING CORRECTLY
- **Correct answer (Haemophilus influenzae)**: 
  - Status: CORRECT ✅
  - Ranking: 1 ✅
  - Confidence: 0.95 ✅
  - **Parsing: SUCCESS**

- **Wrong answer (Streptococcus pneumoniae)**:
  - Status: LIKELY_INCORRECT ✅
  - Ranking: 2 ✅
  - Confidence: 0.9 ✅
  - **Parsing: SUCCESS**

### Question 2 (Hemodialysis Question) - ❌ PROBLEMS
- **Correct answer (Hemodialysis)**:
  - Status: **NOT FOUND** ❌ (Response truncated!)
  - Ranking: 1 (but response cut off)
  - Confidence: **NOT FOUND** ❌
  - **Issue**: Response was cut off before reaching CORRECTNESS line

- **Wrong answer (Pericardiocentesis)**:
  - Status: **NOT FOUND** ❌ (Response truncated!)
  - Ranking: 1 (LLM ranked WRONG answer as #1!) ❌
  - Confidence: **NOT FOUND** ❌
  - **Issue**: LLM incorrectly ranked wrong answer as best, AND response was truncated

### Question 3 (Penicillamine Question) - ⚠️ PARTIAL ISSUES
- **Correct answer (Penicillamine)**:
  - Status: CORRECT ✅
  - Ranking: **4** ❌ (Should be 1, but regex caught wrong number)
  - Confidence: **NOT FOUND** ❌ (Response cut off)
  - **Issue**: Ranking parsing error, confidence missing

- **Wrong answer (Prednisolone)**:
  - Status: **NOT FOUND** ❌ (Response truncated!)
  - Ranking: **NOT FOUND** ❌
  - Confidence: **NOT FOUND** ❌
  - **Issue**: LLM response was cut off, but it seemed to suggest Prednisolone is best (WRONG!)

## Critical Issues Identified

### 1. **Response Truncation** (CRITICAL)
- **Problem**: `max_new_tokens=500` is too low for complex medical questions
- **Impact**: Responses are cut off before reaching CORRECTNESS/RANKING/CONFIDENCE lines
- **Result**: Default scores are used (0.35), losing all discrimination
- **Fix**: Increase `max_new_tokens` to 800-1000

### 2. **LLM Ranking Mistakes** (CRITICAL)
- **Problem**: LLM sometimes ranks WRONG answers as #1
- **Example**: Question 2 - LLM ranked "Pericardiocentesis" (wrong) as #1, "Hemodialysis" (correct) as #2
- **Impact**: Ranking boost (+15%) is applied to WRONG answers, making them score higher
- **Fix**: Need better prompt or validation of rankings

### 3. **Parsing Issues** (MODERATE)
- **Problem**: Regex sometimes catches wrong numbers for ranking
- **Example**: Question 3 - Response says "Ranking: 1" but parsed as 4
- **Impact**: Wrong ranking boost/penalty applied
- **Fix**: Improve regex to be more specific, look for "RANKING:" line specifically

### 4. **Format Inconsistencies** (MODERATE)
- **Problem**: LLM doesn't always follow exact format (sometimes puts CORRECTNESS in different places)
- **Impact**: Parsing fails, defaults used
- **Fix**: Make prompt more explicit about format, or improve parsing to be more flexible

## Root Cause Analysis

### Why Correctness Scores Are Inverted

1. **Truncation**: When responses are cut off, default score (0.35) is used for both correct and wrong
2. **Wrong Rankings**: When LLM ranks wrong answer as #1, it gets +15% boost
3. **Missing Confidence**: When confidence is missing, scores don't get adjusted properly
4. **Result**: Wrong answers end up with similar or higher scores than correct ones

### Why Accuracy Dropped

- **Overconfidence**: Ranking boost (+15%) is being applied to wrong answers that rank #1
- **Default too high**: Default of 0.35 is too high when responses are truncated
- **Fusion logic**: Higher scores (even if wrong) are winning fusion

## Recommended Fixes

### Priority 1: Fix Response Truncation
```python
max_new_tokens=800  # Increase from 500
```
This is the **most critical** fix - if responses are truncated, we lose all discrimination.

### Priority 2: Improve Ranking Validation
- Add validation: If proposed answer ranks #1 but reasoning suggests another option is better, reduce ranking boost
- Or: Only apply ranking boost if correctness status is CORRECT or PROBABLY_CORRECT
- Or: Reduce ranking boost from +15% to +5-10%

### Priority 3: Improve Parsing
- Make regex more specific: Look for "RANKING:" on its own line
- Add fallback parsing: If exact format not found, try to extract from explanation
- Store raw response in two_phase_result for debugging

### Priority 4: Adjust Defaults
- Lower default from 0.35 to 0.25-0.30 (less aggressive)
- Make default depend on whether response was truncated
- If truncated, use lower default (0.20) to be more conservative

### Priority 5: Improve Prompt
- Add explicit instruction: "You MUST provide CORRECTNESS, RANKING, and CONFIDENCE in this exact format at the end of your response"
- Add example showing the format more clearly
- Emphasize that ranking should reflect medical accuracy, not just plausibility

## Expected Impact After Fixes

### If we fix truncation (Priority 1):
- **Correctness gap**: Should improve from -0.014 to +0.10-0.15
- **AUROC**: Should improve from 0.545 to 0.60-0.65

### If we also fix ranking validation (Priority 2):
- **Accuracy**: Should recover from 63.3% to 68-70%
- **AUROC**: Should improve to 0.65-0.70

### If we fix all issues:
- **Accuracy**: 70%+
- **ECE**: 0.25-0.30 (better calibration)
- **AUROC**: 0.65-0.70 (target achieved)

## Conclusion

The **primary issue is response truncation** - when responses are cut off, we lose all the LLM's evaluation and fall back to defaults. This explains why correctness scores don't discriminate.

The **secondary issue is LLM ranking mistakes** - sometimes the LLM ranks wrong answers as #1, and the ranking boost makes them score higher.

**Recommendation**: Fix truncation first (increase max_new_tokens), then add ranking validation, then improve parsing. This should resolve most of the issues.
