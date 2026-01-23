# Tier 2 Validation Improvements for Full Linear

## Date
2026-01-15

## Current Problem

**Tier 2 is approving 89% of wrong answers (185/208)** ❌

This is a critical issue causing:
- Wrong answers getting high confidence
- Full Linear accuracy degradation (53% → 48%)
- Worse ECE (0.320 vs baseline 0.265)

## Root Cause Analysis

### Current Tier 2 Prompt Issues

The prompt is **too lenient**:

1. **"APPROVE if the answer is medically correct and well-reasoned (even if other options might also be valid)"**
   - Problem: Too easy to approve
   - Should be more strict

2. **"Be fair and balanced - don't reject just because other options exist"**
   - Problem: Encourages approval even when uncertain
   - Should be more skeptical

3. **"Focus on validating correctness, not finding flaws"**
   - Problem: Backwards! Should find flaws!
   - Should actively check for errors

4. **No explicit correctness checking**
   - Problem: Relies on LLM's general validation
   - Should explicitly check if answer is correct

## Proposed Improvements

### Improvement 1: Make Tier 2 Prompt More Strict

**Current prompt**: Too lenient, encourages approval

**New prompt**: More strict, actively checks for errors

Key changes:
- "Be skeptical and look for errors"
- "REJECT if you have ANY doubts about correctness"
- "Compare answer against all options to ensure it's the BEST answer"
- "Focus on finding medical errors or incorrect reasoning"

### Improvement 2: Use Tier 1 Correctness Score

**New**: Tier 2 should consider Tier 1's correctness score:

```python
# If Tier 1 found answer is wrong (correctness_score < 0.4)
# Tier 2 should be more likely to REJECT
if tier1_result.get('correctness_score', 0.5) < 0.4:
    # Increase skepticism in Tier 2 prompt
    # Or directly influence validation status
```

### Improvement 3: Add Explicit Correctness Check

Similar to Tier 1, Tier 2 should explicitly check:
- "Is this answer the CORRECT answer to the question?"
- "Are there better alternatives?"
- "Does this answer accurately address the clinical scenario?"

### Improvement 4: Make Penalties More Aggressive

**Current**:
- REJECTED penalty: 0.4
- NEEDS_REVIEW penalty: 0.7

**Proposed**:
- REJECTED penalty: 0.3 (more aggressive)
- NEEDS_REVIEW penalty: 0.6 (more aggressive)

Or make penalties depend on Tier 1 correctness:
- If Tier 1 correctness < 0.4: REJECTED penalty = 0.2 (very aggressive)
- If Tier 1 correctness > 0.6: REJECTED penalty = 0.4 (normal)

### Improvement 5: Compare Against All Options

Tier 2 should:
1. Check if the answer is correct
2. Compare against ALL options
3. Verify it's the BEST answer (not just valid)
4. Reject if a better option exists

## Implementation Plan

### Option A: Improve Tier 2 Prompt (Recommended)

Make the prompt more strict and add explicit correctness checking.

### Option B: Use Tier 1 Correctness Score

Pass Tier 1's correctness score to Tier 2 and use it to influence validation.

### Option C: Add Tier 2 Correctness Check

Add a separate correctness check in Tier 2 (similar to Tier 1).

### Option D: Combine All

Implement all improvements for maximum effectiveness.

## Expected Impact

### Before Improvements
- Tier 2 APPROVED: 89% of wrong answers
- Full Linear accuracy: 48%
- Full Linear ECE: 0.320

### After Improvements
- Tier 2 APPROVED: ~30-40% of wrong answers (reduced)
- Tier 2 REJECTED: ~40-50% of wrong answers (increased)
- Full Linear accuracy: Expected 53-55% (+5-7%)
- Full Linear ECE: Expected 0.25-0.27 (improved)
