# Tier 2 Aggressive Fix V2 - Make Full Linear Best Configuration

## Date: 2026-01-17

## Problem Identified

**Analysis of 100-question experiment**:
- Full Linear underperformed: 57.0% accuracy (vs 59.0% baseline)
- Tier 2 approved 3 wrong answers with high G scores (0.380 average)
- All 3 wrong answers had Tier 1 status = UNCERTAIN (not NO)
- Tier 1 correctness scores too high (0.558 average) for wrong answers

**Root Cause**:
1. Tier 2 not aggressive enough when Tier 1 says UNCERTAIN
2. Tier 1 giving too high correctness scores for wrong answers (0.558)
3. Tier 2 approving wrong answers despite Tier 1 UNCERTAIN status

## Fixes Applied

### 1. Tier 2 Penalties - More Aggressive for UNCERTAIN

**File**: `src/verification/tier2_validation.py`

**Changes**:
- When Tier 1 says UNCERTAIN and Tier 2 says APPROVED: G_score *= 0.25 (was 0.4)
- When Tier 1 says UNCERTAIN and Tier 2 says NEEDS_REVIEW: G_score *= 0.35 (was 0.5)

**Expected Impact**:
- G scores on wrong answers should drop from 0.380 to ~0.095 (0.380 × 0.25)
- This should prevent wrong answers from winning fusion

### 2. Tier 1 UNCERTAIN Threshold - More Aggressive

**File**: `src/verification/tier1_verification.py`

**Changes**:
- UNCERTAIN threshold: correctness_score > 0.3 (was 0.4)
- Correctness score range for INCORRECT/UNCERTAIN: 0.10-0.15 (was 0.10-0.18)

**Expected Impact**:
- More answers will get NO status instead of UNCERTAIN
- Lower correctness scores for uncertain answers
- Better alignment with Tier 2 penalties

### 3. Tier 2 Prompt - More Aggressive for UNCERTAIN

**File**: `src/agents/prompts.py`

**Changes**:
- "If Tier 1 says UNCERTAIN → ALMOST ALWAYS REJECT" (was "STRONGLY CONSIDER REJECTING")
- "ONLY APPROVE if you are ABSOLUTELY CERTAIN AND can explain why Tier 1 was wrong"

**Expected Impact**:
- Tier 2 will be more skeptical of UNCERTAIN answers
- Fewer wrong answers will be APPROVED
- Better alignment with penalties

## Expected Results After Fix

### Before Fix
- Wrong answers approved: 3/5 (60%)
- Average G score on wrong answers: 0.380
- Full Linear accuracy: 57.0%

### After Fix (Expected)
- Wrong answers approved: 0-1/5 (0-20%)
- Average G score on wrong answers: <0.15
- Full Linear accuracy: >59.0% (should beat baseline)

## Files Modified

1. `src/verification/tier2_validation.py`
   - UNCERTAIN + APPROVED: 0.4 → 0.25
   - UNCERTAIN + NEEDS_REVIEW: 0.5 → 0.35

2. `src/verification/tier1_verification.py`
   - UNCERTAIN threshold: 0.4 → 0.3
   - INCORRECT/UNCERTAIN score range: 0.10-0.18 → 0.10-0.15

3. `src/agents/prompts.py`
   - Tier 2 prompt: More aggressive for UNCERTAIN status

## Next Steps

1. **Re-run 10-question test** to verify fixes work
2. **Check if wrong answers still get approved** - should be rare
3. **Check G scores on wrong answers** - should be <0.15
4. **If successful, re-run full 100-question experiment**

## Success Criteria

- ✅ Wrong answers approved: <20% (currently 60%)
- ✅ Average G score on wrong answers: <0.15 (currently 0.380)
- ✅ Full Linear accuracy: >59.0% (currently 57.0%)
- ✅ Full Linear ECE: <0.20 (currently 0.217)
