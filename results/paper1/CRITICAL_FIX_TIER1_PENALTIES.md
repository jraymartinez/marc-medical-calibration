# Critical Fix: Tier 1 Penalty Values

## Problem Discovered

The optimized run got **40.0% accuracy** instead of expected **46.7%** because the Tier 1 penalty values were incorrect.

## Root Cause

**Tuning Summary Document** said:
- NO=0.3, UNCERTAIN=0.6

**But Actual Tuning Run** used:
- NO=0.1, UNCERTAIN=0.4

## Evidence

Analysis of tuning run S_scores shows:
- For UNCERTAIN cases: `S_score = (0.5 * phase1 + 0.5 * phase2) * 0.4`
- Example: `0.3 = (0.5 * 0.9 + 0.5 * 0.6) * 0.4 = 0.75 * 0.4`

**Average UNCERTAIN adjustment_factor from tuning run: 0.400**

## Fix Applied

Changed Tier 1 penalties back to actual tuning values:
- **NO**: 0.1 (was incorrectly set to 0.3)
- **UNCERTAIN**: 0.4 (was incorrectly set to 0.6)

## Expected Result

With correct Tier 1 penalties, Full Linear should achieve **46.7% accuracy** matching the tuning run.

---

## Lesson Learned

Always verify parameter values by analyzing actual results, not just documentation!
