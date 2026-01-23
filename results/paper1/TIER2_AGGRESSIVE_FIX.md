# Tier 2 Aggressive Fix - When Tier 1 Says NO

## Date: 2026-01-16

## Summary

Made Tier 2 even more aggressive when Tier 1 says NO or UNCERTAIN, to reduce wrong answer approvals.

## Problem

- Tier 2 was still approving wrong answers even when Tier 1 said NO
- Question 7: Tier 1=NO, Tier 2=APPROVED (wrong answer)
- Need Tier 2 to REJECT more often when Tier 1 says NO

## Fix Applied

### 1. Updated Tier 2 Penalty Logic (`src/verification/tier2_validation.py`)

**NEEDS_REVIEW with Tier 1 NO**:
- Before: 0.4 penalty
- After: **0.3 penalty** (more aggressive)

**APPROVED with Tier 1 NO**:
- Before: 0.3 penalty
- After: **0.2 penalty** (very aggressive)

**Rationale**: When Tier 1 says NO, Tier 2 should REJECT, not APPROVE or NEEDS_REVIEW.

### 2. Updated Tier 2 Prompt (`src/agents/prompts.py`)

**Added Explicit Decision Priority**:
1. If Tier 1 says NO → STRONGLY CONSIDER REJECTING (very high priority)
2. If Tier 1 says UNCERTAIN → STRONGLY CONSIDER REJECTING (high priority)
3. Only APPROVE if you are ABSOLUTELY CERTAIN despite Tier 1's concerns

**Added Separate Instructions**:
- "If Tier 1 says NO, you should STRONGLY CONSIDER REJECTING"
- "Tier 1 NO means the answer is likely wrong - you should be very skeptical and likely REJECT"
- "Only APPROVE if you are ABSOLUTELY CERTAIN the answer is correct despite Tier 1 saying NO"

## Expected Impact

- Tier 2 will REJECT more often when Tier 1 says NO
- Wrong answers won't get APPROVED when Tier 1 says NO
- Better validation when Tier 1 identifies wrong answers

## Files Modified

1. `src/verification/tier2_validation.py`
   - NEEDS_REVIEW with Tier 1 NO: 0.3 penalty (was 0.4)
   - APPROVED with Tier 1 NO: 0.2 penalty (was 0.3)

2. `src/agents/prompts.py`
   - Added explicit decision priority for Tier 1 NO/UNCERTAIN
   - Added separate instructions for each case

## Expected Results

- Tier 2 should REJECT 80%+ of wrong answers when Tier 1 says NO
- Wrong answers should rarely get APPROVED when Tier 1 says NO
- Better overall validation accuracy
