# Answer Parsing Fix - Strip Letter Prefixes

## Date: 2026-01-16

## Problem Identified

**Question 7 Analysis**:
- Final Answer: "D. Mi-2 protein"
- Correct Answer: "Mi-2 protein"
- Marked as: **WRONG** ❌

**Root Cause**:
- The code converts single-letter answers (like "D") to full text
- But it doesn't strip letter prefixes from answers that already have full text with a prefix (like "D. Mi-2 protein")
- Comparison: "d. mi-2 protein" != "mi-2 protein" → WRONG

**This is a parsing/normalization bug, not a verification issue!**

## Fix Applied

### Updated Answer Comparison Logic

**Files Modified**:
1. `scripts/run_optimized_multi_specialist.py` (line 238-244)
2. `scripts/test_tier1_tier2_improvements.py` (line 270-273)

**Before**:
```python
# Convert letter answer (A/B/C/D) to full text if needed
final_answer_text = final_answer.strip()
if isinstance(options, dict) and len(final_answer_text) == 1 and final_answer_text.upper() in options:
    final_answer_text = options[final_answer_text.upper()]

# Check if correct
is_correct = (final_answer_text.strip().lower() == correct_answer.strip().lower())
```

**After**:
```python
# Convert letter answer (A/B/C/D) to full text if needed
final_answer_text = final_answer.strip()
if isinstance(options, dict) and len(final_answer_text) == 1 and final_answer_text.upper() in options:
    final_answer_text = options[final_answer_text.upper()]

# Strip letter prefixes (e.g., "D. Mi-2 protein" -> "Mi-2 protein")
import re
final_answer_text = re.sub(r'^[A-Z]\.\s*', '', final_answer_text, flags=re.IGNORECASE).strip()
correct_answer_normalized = re.sub(r'^[A-Z]\.\s*', '', correct_answer, flags=re.IGNORECASE).strip()

# Check if correct (case-insensitive comparison)
is_correct = (final_answer_text.lower() == correct_answer_normalized.lower())
```

## Expected Impact

### Question 7 (After Fix)

**Before Fix**:
- Final Answer: "D. Mi-2 protein"
- Correct Answer: "Mi-2 protein"
- Comparison: "d. mi-2 protein" != "mi-2 protein" → **WRONG** ❌

**After Fix**:
- Final Answer: "D. Mi-2 protein" → "Mi-2 protein" (after stripping)
- Correct Answer: "Mi-2 protein" → "Mi-2 protein" (after stripping)
- Comparison: "mi-2 protein" == "mi-2 protein" → **CORRECT** ✅

**This should improve accuracy by correctly identifying answers that match the correct answer but have letter prefixes.**

## Files Modified

1. `scripts/run_optimized_multi_specialist.py`
   - Added letter prefix stripping before answer comparison
   - Strips prefixes from both `final_answer_text` and `correct_answer`

2. `scripts/test_tier1_tier2_improvements.py`
   - Added letter prefix stripping for all three configurations (baseline, tier1, full_linear)
   - Normalizes answers before comparison

## Next Steps

1. **Re-test with 10 questions** to verify fix works
2. **Check if Question 7 is now marked as CORRECT**
3. **Check overall accuracy improvement** - should increase if this was a common issue
4. **If successful, run full 100-question experiment**

## Note

This fix is separate from the Tier 1 NO penalty fix. Both fixes should be applied together:
- **Tier 1 NO penalty fix**: Prevents wrong answers from winning fusion
- **Answer parsing fix**: Correctly identifies answers that match the correct answer but have letter prefixes
