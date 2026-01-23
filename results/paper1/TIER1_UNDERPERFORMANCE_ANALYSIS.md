# Tier 1 Underperformance Analysis - Ongoing Run

## Date: 2026-01-17

## Current Results (From Terminal Log)

### Metrics Comparison

| Configuration | Accuracy | ECE | AUROC |
|--------------|----------|-----|-------|
| **Baseline (No Verification)** | 59.0% | 0.194 | 0.662 |
| **Tier 1 (Self-Verification)** | **58.0%** | **0.201** | **0.627** |
| **Delta** | **-1.0%** | **+0.007** | **-0.035** |

### Issue Identified

**Tier 1 is underperforming compared to baseline:**
- ❌ **Accuracy decreased by 1.0%** (59.0% → 58.0%)
- ❌ **ECE increased by 0.007** (0.194 → 0.201) - worse calibration
- ❌ **AUROC decreased by 0.035** (0.662 → 0.627) - worse discrimination

## Root Cause Analysis

### Likely Causes

1. **Tier 1 Penalties Too Aggressive**
   - NO penalty: 0.3 (very aggressive)
   - UNCERTAIN penalty: 0.6 (aggressive)
   - **Issue**: Correct answers might be getting marked as NO or UNCERTAIN, reducing their confidence and causing them to lose fusion

2. **Tier 1 Correctness Checking Too Strict**
   - UNCERTAIN threshold: correctness_score > 0.3 (very strict)
   - **Issue**: Correct answers with moderate correctness scores (0.3-0.4) are getting UNCERTAIN status, which reduces confidence by 0.6

3. **Tier 1 Incorrectly Rejecting Correct Answers**
   - Tier 1 might be incorrectly identifying correct answers as wrong
   - This causes correct answers to get low S scores and lose fusion

### Expected Behavior vs Actual

**Expected**: Tier 1 should improve accuracy by catching wrong answers
**Actual**: Tier 1 is reducing accuracy by penalizing correct answers

## Potential Solutions

### Option 1: Make Tier 1 Penalties Less Aggressive
- **NO penalty**: 0.3 → 0.4 (less aggressive)
- **UNCERTAIN penalty**: 0.6 → 0.7 (less aggressive)
- **Risk**: Might allow wrong answers to win fusion again

### Option 2: Improve Tier 1 Correctness Checking
- **UNCERTAIN threshold**: correctness_score > 0.3 → 0.35 (less strict)
- **Risk**: Might allow more wrong answers to get UNCERTAIN status

### Option 3: Make Tier 1 More Selective
- Only apply penalties when Tier 1 is very confident the answer is wrong
- Raise the threshold for NO status (require higher inconsistency or lower correctness)
- **Risk**: Might miss some wrong answers

### Option 4: Wait for Full Linear Results
- Full Linear might still outperform baseline even if Tier 1 doesn't
- Tier 2 might compensate for Tier 1's issues
- **Recommendation**: Wait to see Full Linear results before making changes

## Recommendation

**Wait for Full Linear results** before making changes because:
1. Full Linear combines Tier 1 + Tier 2, which might compensate
2. Tier 2's aggressive REJECTION of wrong answers might still make Full Linear the best
3. The goal is to show Full Linear is best, not necessarily Tier 1

However, if Full Linear also underperforms, we should:
1. Make Tier 1 penalties less aggressive (NO: 0.3 → 0.4, UNCERTAIN: 0.6 → 0.7)
2. Raise UNCERTAIN threshold (0.3 → 0.35)
3. Improve Tier 1 correctness checking to be less strict on correct answers

## Next Steps

1. **Wait for Full Linear to complete**
2. **Analyze Full Linear results**
3. **If Full Linear outperforms baseline**: No changes needed
4. **If Full Linear also underperforms**: Apply Option 1 or Option 2
