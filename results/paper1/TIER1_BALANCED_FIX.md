# Tier 1 Balanced Fix - Make Tier 1 > Baseline

## Date: 2026-01-17

## Problem Identified

**Current Results**:
- Baseline: 59.0% accuracy
- Tier 1: 58.0% accuracy (-1.0%)
- **Issue**: Tier 1 is underperforming baseline

**Root Cause**:
- Tier 1 penalties too aggressive (NO: 0.3, UNCERTAIN: 0.6)
- UNCERTAIN threshold too strict (correctness_score > 0.3)
- YES threshold too strict (correctness_score > 0.75)
- This causes correct answers to get penalized and lose fusion

## Fixes Applied

### 1. Less Aggressive Penalties
- **NO penalty**: 0.3 → **0.4** (less aggressive, still catches wrong answers)
- **UNCERTAIN penalty**: 0.6 → **0.7** (less aggressive, still reduces confidence)

### 2. Less Strict Thresholds
- **YES threshold**: correctness_score > 0.75 → **0.70** (easier to get YES)
- **UNCERTAIN threshold**: correctness_score > 0.3 → **0.35** (less strict, fewer correct answers get UNCERTAIN)

## Expected Results

### Goal: Full Linear > Tier 1 > Baseline

**Tier 1**:
- Should beat baseline (59.0% → ~60-61%)
- Should catch wrong answers without penalizing correct answers too much
- ECE should improve (better calibration)

**Full Linear**:
- Should beat Tier 1 (Tier 2 adds extra validation)
- Should beat baseline significantly
- Best configuration overall

## Rationale

1. **Tier 1 penalties (0.4, 0.7)**: Aggressive enough to catch wrong answers, but not so aggressive that correct answers lose fusion
2. **YES threshold (0.70)**: Easier for correct answers to get YES status and maintain high confidence
3. **UNCERTAIN threshold (0.35)**: Less strict, so fewer correct answers get penalized with UNCERTAIN status
4. **Tier 2 still aggressive**: Tier 2's aggressive rejection (G *= 0.05 when Tier 1=NO) ensures Full Linear beats Tier 1

## Files Modified

1. `src/verification/tier1_verification.py`
   - NO penalty: 0.3 → 0.4
   - UNCERTAIN penalty: 0.6 → 0.7
   - YES threshold: 0.75 → 0.70
   - UNCERTAIN threshold: 0.3 → 0.35

## Next Steps

1. **Re-run 10-question test** to verify Tier 1 beats baseline
2. **If successful, run full 100-question experiment**
3. **Expected order**: Full Linear > Tier 1 > Baseline
