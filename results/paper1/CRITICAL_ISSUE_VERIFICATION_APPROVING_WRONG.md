# Critical Issue: Verification Approving Wrong Answers

## Date
2026-01-15

## Problem Summary

**Full Linear accuracy degraded from 53% to 48% (-5%)**
**Tier 1 improved slightly (48% → 50%) but still worse than baseline (53%)**

### Metrics Comparison

| Configuration | Previous | Latest | Change |
|--------------|----------|--------|--------|
| Baseline | 53.0% | 53.0% | +0.0% |
| Tier 1 | 48.0% | 50.0% | +2.0% ✅ (but still worse than baseline) |
| Full Linear | 53.0% | **48.0%** | **-5.0%** ❌ |

### Degradations

| Configuration | Previous | Latest | Change |
|--------------|----------|--------|--------|
| Tier 1 | 10 | 3 | -7 ✅ (improved) |
| Full Linear | 2 | **7** | **+5** ❌ (worse) |

## Root Cause Analysis

### The Problem: Verification Approving Wrong Answers

**Key Finding**: In Full Linear degradations, **Tier 1 gives YES status to wrong answers**, and **Tier 2 approves them**.

**Example (Q4 - Full Linear degradation)**:
- Correct: "Increase in length constant"
- Full Linear selected: "Decrease in transmembrane resistance" (WRONG)
- Respiratory specialist:
  - Tier 1: **YES**, S=0.848 (high confidence!)
  - Tier 2: **APPROVED**, G=0.850 (approved!)
- But this is the **WRONG answer**!

**Example (Q12 - Tier 1 degradation)**:
- Correct: "21-hydroxylase"
- Tier 1 selected: "17-hydroxylase" (WRONG)
- All specialists got **YES status** with high S scores (0.760-1.000)
- But the answer is **WRONG**!

### Why This Happens

**Wu et al. Two-Phase Verification measures internal consistency, not correctness:**

1. **Formulate verification questions** from the explanation
2. **Answer independently** (without reference)
3. **Answer with reference** (with reference to explanation)
4. **Measure inconsistencies** → low inconsistency = YES status

**The Problem**: A wrong answer can still have **low inconsistency** if:
- The explanation is internally consistent (even if wrong)
- Independent and reference answers match (even if both are wrong)
- The verification questions don't catch the error

**Example**: If a specialist says "17-hydroxylase" and gives a consistent explanation, the verification will find low inconsistency → YES status → high confidence → wrong answer selected.

### Tier 1 Status in Degradations

**Previous Run (before fixes)**:
- NO: 57.5% (too many, but at least catching some errors)
- UNCERTAIN: 15%
- YES: 27.5%

**Latest Run (with fixes)**:
- NO: 0% ❌ (not catching any errors!)
- UNCERTAIN: 8.3%
- **YES: 91.7%** ❌ (approving wrong answers!)

**The fixes made it worse**: More lenient thresholds → more YES status → approving wrong answers!

### Full Linear Issue

**Tier 2 is also approving wrong answers**:
- In Full Linear degradations, Tier 2 **APPROVED 7/8 wrong answers**
- Tier 2 validation is too lenient
- Combined with Tier 1 YES status → wrong answers get high confidence

## The Fundamental Problem

**Wu et al. Two-Phase Verification measures internal consistency, not correctness.**

This is a **fundamental limitation** of the method:
- ✅ Good at detecting when a model is uncertain (high inconsistency)
- ❌ Bad at detecting when a model is confidently wrong (low inconsistency but wrong answer)

**For medical QA, we need correctness checking, not just consistency checking.**

## Solutions

### Option 1: Add Correctness Checking (Recommended)

Modify Tier 1 to check if the answer is actually correct, not just consistent:

1. **Keep consistency checking** (Wu et al. method)
2. **Add correctness checking**: 
   - Ask: "Is this answer medically correct?"
   - Check against medical knowledge
   - Penalize if answer is wrong (even if consistent)

3. **Combine both**:
   - Low inconsistency + Correct → YES (high confidence)
   - Low inconsistency + Wrong → NO (low confidence)
   - High inconsistency → UNCERTAIN or NO

### Option 2: Make Thresholds More Strict Again

Revert to stricter thresholds:
- YES: < 0.4 (was 0.6)
- UNCERTAIN: < 0.6 (was 0.8)
- NO: >= 0.6 (was 0.8)

But this will bring back the original problem (too many NO status).

### Option 3: Hybrid Approach

1. **Use consistency for uncertainty detection** (Wu et al. method)
2. **Use correctness checking for answer validation**
3. **Combine**: 
   - Consistency score (0-1)
   - Correctness score (0-1)
   - Final confidence = f(consistency, correctness)

### Option 4: Improve Tier 2 Validation

Make Tier 2 more strict:
- Current: APPROVED 7/8 wrong answers
- Need: Reject wrong answers more aggressively
- Check Tier 2 prompt and validation logic

## Immediate Actions

1. **Analyze what Tier 1 is missing**: Why is it giving YES to wrong answers?
2. **Check Tier 2 validation**: Why is it approving wrong answers?
3. **Consider adding correctness checking** to Tier 1
4. **Or revert to stricter thresholds** and accept more NO status

## Expected Impact of Fixes

### If we add correctness checking:
- Tier 1: 50% → 52-54% (catch wrong answers)
- Full Linear: 48% → 53-55% (Tier 2 + correctness checking)

### If we revert thresholds:
- Tier 1: 50% → 48-50% (back to original)
- Full Linear: 48% → 50-52% (slight improvement)

## Conclusion

**The Wu et al. Two-Phase Verification method has a fundamental limitation**: It measures internal consistency, not correctness. Wrong answers can have low inconsistency if they're internally consistent.

**We need to add correctness checking** to catch wrong answers, not just rely on consistency.
