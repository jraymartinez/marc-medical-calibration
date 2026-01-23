# Tier 2 Validation Improvements Applied

## Date
2026-01-15

## Improvements Applied

### 1. More Strict Tier 2 Prompt

**Changed from lenient to strict validation:**

**Before**:
- "APPROVE if the answer is medically correct and well-reasoned (even if other options might also be valid)"
- "Be fair and balanced - don't reject just because other options exist"
- "Focus on validating correctness, not finding flaws"

**After**:
- "APPROVE ONLY if you are confident this is the CORRECT and BEST answer"
- "Be SKEPTICAL - actively look for errors and better alternatives"
- "Compare the answer against ALL options to ensure it's the best choice"
- "If Tier 1 found the answer is wrong (correctness_score < 0.4), be more likely to REJECT"

### 2. Use Tier 1 Correctness Score

**New logic**: Tier 2 now considers Tier 1's correctness score:

```python
tier1_correctness = tier1_result.get('correctness_score', 0.5)

if validation_status == "REJECTED":
    if tier1_correctness < 0.4:
        G_score *= 0.2  # Very aggressive (Tier 1 found it wrong)
    else:
        G_score *= 0.4  # Normal penalty

elif validation_status == "NEEDS_REVIEW":
    if tier1_correctness < 0.4:
        G_score *= 0.5  # More aggressive (Tier 1 found it wrong)
    else:
        G_score *= 0.7  # Normal penalty

elif validation_status == "APPROVED" and tier1_correctness < 0.4:
    # Tier 1 found it wrong but Tier 2 approved → reduce confidence
    G_score *= 0.6  # Moderate penalty even for APPROVED
```

**Impact**: 
- If Tier 1 found answer is wrong (correctness < 0.4), Tier 2 penalties are more aggressive
- Even if Tier 2 approves a wrong answer, confidence is reduced if Tier 1 found it wrong

### 3. Explicit Correctness Checking

**New prompt instructions**:
- "Is this answer the CORRECT answer? (Not just valid, but actually correct)"
- "Is this the BEST answer? (Compare against all options)"
- "A wrong answer can be well-reasoned but still incorrect. Your job is to catch these errors."

## Expected Impact

### Before Improvements
- Tier 2 APPROVED: 89% of wrong answers (185/208)
- Tier 2 REJECTED: 4% of wrong answers (8/208)
- Full Linear accuracy: 48%
- Full Linear ECE: 0.320

### After Improvements (Expected)
- Tier 2 APPROVED: ~30-40% of wrong answers (reduced from 89%)
- Tier 2 REJECTED: ~40-50% of wrong answers (increased from 4%)
- Full Linear accuracy: Expected 53-55% (+5-7%)
- Full Linear ECE: Expected 0.25-0.27 (improved from 0.320)

## How It Works

### Example: Wrong Answer with Tier 1 Correctness Check

**Scenario**: Specialist says "17-hydroxylase" (wrong, should be "21-hydroxylase")

1. **Tier 1**:
   - Consistency: Low inconsistency (0.3) → consistent
   - Correctness: Checks → "INCORRECT" → correctness_score = 0.2
   - Status: NO (correctness < 0.6)
   - S score: Low (0.2-0.3)

2. **Tier 2** (with improvements):
   - Sees Tier 1 correctness_score = 0.2 (< 0.4)
   - Prompt: "If Tier 1 found answer is wrong, be more likely to REJECT"
   - Validation: Checks correctness → "INCORRECT"
   - Status: **REJECTED** (more likely due to Tier 1 signal)
   - G score: 0.85 × 0.2 = 0.17 (very aggressive penalty)

3. **Result**:
   - Wrong answer gets low confidence (0.17)
   - Not selected by fusion
   - Correct answer selected instead

### Example: Correct Answer

**Scenario**: Specialist says "21-hydroxylase" (correct)

1. **Tier 1**:
   - Consistency: Low inconsistency (0.3)
   - Correctness: Checks → "CORRECT" → correctness_score = 0.9
   - Status: YES (both good)
   - S score: High (0.8-0.9)

2. **Tier 2**:
   - Sees Tier 1 correctness_score = 0.9 (> 0.4)
   - Validation: Checks correctness → "CORRECT"
   - Status: **APPROVED**
   - G score: 0.85 (no penalty)

3. **Result**:
   - Correct answer gets high confidence
   - Selected by fusion
   - Accuracy improves

## Key Improvements Summary

1. ✅ **Stricter prompt** - Actively looks for errors
2. ✅ **Uses Tier 1 correctness** - More aggressive penalties if Tier 1 found it wrong
3. ✅ **Explicit correctness check** - Compares against all options
4. ✅ **Better rejection logic** - Catches wrong answers more effectively

## Next Steps

1. ✅ **Improvements applied** - Tier 2 prompt and logic updated
2. **Test on 10 questions** - Verify Tier 2 rejects wrong answers
3. **Run full experiment** - Test on 100 questions
4. **Verify improvements** - Check accuracy, ECE, Tier 2 approval rate
