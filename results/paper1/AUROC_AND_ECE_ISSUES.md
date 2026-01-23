# AUROC and ECE Issues Analysis

## Date: 2026-01-19

## Issue 1: AUROC = 0.5 (No Discrimination)

### Root Cause

**Confidence scores for correct and wrong answers are almost identical**:
- Multi-Agent + Two-Phase Verification:
  - Correct answers: Mean confidence = 0.279
  - Wrong answers: Mean confidence = 0.238
  - **Mean difference: 0.041** (very small!)

### Why This Happens

1. **Temperature scaling is too aggressive**: `temperature_scale = 1.5` reduces all confidences to similar low values
2. **Two-Phase Verification doesn't discriminate well**: Similar confidence for correct/wrong answers
3. **Confidence range is too narrow**: All confidences between 0.2-0.4

### Evidence

From debug analysis:
- Top 50% (high confidence) accuracy: 80.0%
- Bottom 50% (low confidence) accuracy: 60.0%
- **There IS some discrimination**, but mean difference is too small
- AUROC = 0.579 (not exactly 0.5, but close - indicates weak discrimination)

### Fix Needed

1. **Reduce temperature scaling**: From 1.5 to 1.2-1.3
2. **Increase confidence for correct answers**: Boost Two-Phase YES status more (1.3x instead of 1.2x)
3. **Better S score calculation**: Two-Phase should give higher scores for correct answers

**Expected Impact**: 
- Correct answers: Mean confidence → 0.4-0.5
- Wrong answers: Mean confidence → 0.2-0.3
- **Gap increases**: 0.041 → 0.2+ (better discrimination)
- **AUROC improves**: 0.579 → 0.65-0.75

## Issue 2: ECE Calculation Bug

### Root Cause

**Answer matching in metrics.py doesn't handle letter vs full text**:
- Predictions are letters ("C", "B", etc.)
- Ground truth is full text ("Isolate patient...", etc.)
- Simple string comparison fails: "C" != "Isolate patient..."

### Fix Applied

Updated `calculate_accuracy()`, `calculate_confidence_metrics()`, and `calculate_auroc()` to:
1. Accept `options` parameter
2. Convert letter answers to full text before comparison
3. Normalize (strip prefixes, lowercase) before comparing

**Expected Impact**: ECE and AUROC calculations will be accurate

## Issue 3: ECE = 0.267 (Can Be Improved)

### Current Status

- Multi-Agent + Two-Phase Verification: ECE = 0.267
- This is **good** (much better than baseline 0.869)
- But can be improved to < 0.15 (excellent calibration)

### Problems

1. **Underconfidence for correct answers**: 20/21 correct answers have confidence < 0.5
2. **Overconfidence in some bins**: Bin [0.2-0.3] has accuracy 69.2% but avg confidence 0.239 (gap = 0.453)

### Fix Needed

1. **Increase confidence for correct answers**: Reduce temperature scaling, boost YES status
2. **Better calibration**: Match confidence to actual accuracy
3. **Reduce gap in bins**: Especially [0.2-0.3] bin which has large gap

**Expected Impact**: ECE improves from 0.267 to 0.15-0.20

## Summary of Fixes

### Fix 1: Answer Matching ✅
- Updated metrics.py to handle letter-to-text conversion
- Pass options to metrics functions

### Fix 2: Improve Discrimination (Next)
- Reduce temperature scaling: 1.5 → 1.2
- Increase Two-Phase boost: 1.2x → 1.3x for YES status
- Expected: AUROC 0.579 → 0.65-0.75

### Fix 3: Improve ECE (Next)
- Increase confidence for correct answers
- Better calibration
- Expected: ECE 0.267 → 0.15-0.20
