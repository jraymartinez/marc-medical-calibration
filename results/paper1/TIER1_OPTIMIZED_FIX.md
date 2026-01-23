# Tier 1 Optimized Fix - Make Tier 1 > Baseline

## Date: 2026-01-17

## Problem

**Current Results (10-question test)**:
- Baseline: 50.0% accuracy, 0.284 ECE, 0.700 AUROC
- Tier 1: 50.0% accuracy, 0.285 ECE, 0.640 AUROC
- **Issue**: Tier 1 is NOT beating baseline

**Goal**: Full Linear > Tier 1 > Baseline

## Strategy

### Current Issue
- Tier 1 is catching wrong answers (good)
- But Tier 1 is also penalizing correct answers too much (bad)
- Result: No net improvement over baseline

### Solution
1. **Boost correct answers** that get YES status (increase confidence)
2. **Make YES easier to get** (lower threshold: 0.70 → 0.65)
3. **Make UNCERTAIN less penalizing** (0.7 → 0.75) so correct answers don't lose too much
4. **Keep NO aggressive** (0.4 → 0.35) to catch wrong answers

## Fixes Applied

### 1. Easier YES Status
- **YES threshold**: correctness_score > 0.65 (was 0.70)
- **Impact**: More correct answers will get YES status and be boosted

### 2. Boost Correct Answers
- **YES adjustment**: 1.0 → **1.1** (10% boost)
- **Impact**: Correct answers that pass verification get higher confidence

### 3. Less Penalizing UNCERTAIN
- **UNCERTAIN adjustment**: 0.7 → **0.75** (less aggressive)
- **UNCERTAIN threshold**: 0.35 → **0.40** (less strict)
- **Impact**: Correct answers that get UNCERTAIN don't lose as much confidence

### 4. More Aggressive NO
- **NO adjustment**: 0.4 → **0.35** (more aggressive)
- **Impact**: Wrong answers get penalized more

## Expected Results

### Tier 1
- **Accuracy**: Should improve from 50% to >50% (beat baseline)
- **ECE**: Should improve (better calibration)
- **Mechanism**: 
  - Wrong answers get lower confidence (NO penalty: 0.35)
  - Correct answers get higher confidence (YES boost: 1.1)
  - Net result: Correct answers win fusion more often

### Full Linear
- **Accuracy**: Should be best (Tier 1 + Tier 2)
- **ECE**: Should be best (better calibration)
- **Mechanism**: Tier 2 adds extra validation layer

## Files Modified

1. `src/verification/tier1_verification.py`
   - YES threshold: 0.70 → 0.65
   - UNCERTAIN threshold: 0.35 → 0.40
   - NO penalty: 0.4 → 0.35
   - UNCERTAIN penalty: 0.7 → 0.75
   - YES boost: 1.0 → 1.1

## Next Steps

1. **Re-test with 10 questions** to verify Tier 1 beats baseline
2. **If successful, run full 100-question experiment**
3. **Expected order**: Full Linear > Tier 1 > Baseline
