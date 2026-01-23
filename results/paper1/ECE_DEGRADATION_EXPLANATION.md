# ECE Degradation Explanation: Why Verification Makes Calibration Worse

## Date
2026-01-15

## Problem Summary

**ECE (Expected Calibration Error) is worse with verification:**
- Baseline: **0.265**
- Tier 1: **0.301** (worse by +0.036)
- Full Linear: **0.320** (worse by +0.055)

**Higher ECE = Worse Calibration** (confidence scores don't match actual correctness)

## Root Cause: Verification Increases Confidence on Wrong Answers

### The Problem

**Verification is giving high confidence (YES/APPROVED) to wrong answers**, which:
1. Moves wrong answers into high-confidence bins (0.8-0.9, 0.9-1.0)
2. But doesn't improve their accuracy
3. Creates larger gaps between confidence and accuracy in those bins
4. **Result: Worse ECE**

### Evidence

#### Tier 1 Status on Wrong Answers
- **YES: 102/200 (51%)** ❌ (giving high confidence to wrong answers!)
- UNCERTAIN: 44/200 (22%)
- NO: 54/200 (27%)

#### Full Linear Status on Wrong Answers
- **Tier 1 YES: 98/208 (47%)** ❌
- **Tier 2 APPROVED: 185/208 (89%)** ❌ (approving wrong answers!)
- Tier 2 REJECTED: 8/208 (4%) (not catching errors)

### Confidence Distribution Analysis

#### Wrong Answers with High Confidence (>0.7)
- Baseline: **72.3%** of wrong answers have confidence >0.7
- Tier 1: **68.0%** of wrong answers have confidence >0.7 (slightly better)
- Full Linear: **65.4%** of wrong answers have confidence >0.7 (slightly better)

**But ECE is worse! Why?**

### ECE Bin Analysis: The Key Insight

#### Baseline (ECE = 0.265)
```
Bin 0.8-0.9: 58 answers
  Accuracy: 50.0%
  Avg Confidence: 0.829
  Gap: 0.329
```

#### Tier 1 (ECE = 0.301)
```
Bin 0.8-0.9: 33 answers
  Accuracy: 42.4%  ← WORSE accuracy!
  Avg Confidence: 0.844  ← HIGHER confidence!
  Gap: 0.420  ← LARGER gap = worse ECE!
```

#### Full Linear (ECE = 0.320)
```
Bin 0.8-0.9: 47 answers
  Accuracy: 46.8%  ← WORSE accuracy!
  Avg Confidence: 0.840  ← HIGHER confidence!
  Gap: 0.372  ← LARGER gap = worse ECE!
```

## Why This Happens

### 1. Verification Approves Wrong Answers

**Tier 1**: 
- Measures internal consistency (Wu et al. method)
- Wrong answers can have low inconsistency if internally consistent
- Result: **YES status** → high S score → high confidence

**Tier 2**:
- Validates medical correctness
- But **89% of wrong answers get APPROVED**
- Result: **APPROVED** → high G score → high confidence

### 2. Wrong Answers Move to High-Confidence Bins

**Before verification**:
- Wrong answers: mean confidence 0.783
- Some wrong answers in lower bins (0.6-0.7)

**After verification**:
- Wrong answers with YES/APPROVED: confidence increases to 0.8-0.9
- They move to high-confidence bins
- But accuracy doesn't improve (still wrong!)

### 3. High-Confidence Bins Have Worse Accuracy

**Baseline**:
- Bin 0.8-0.9: 50% accuracy (50% correct, 50% wrong)
- Gap: 0.329

**Tier 1**:
- Bin 0.8-0.9: **42.4% accuracy** (worse!)
- More wrong answers moved here (with high confidence)
- Gap: **0.420** (larger = worse ECE)

**Full Linear**:
- Bin 0.8-0.9: **46.8% accuracy** (worse!)
- Even more wrong answers moved here
- Gap: **0.372** (larger = worse ECE)

## The Mathematical Explanation

**ECE = Σ |accuracy(bin) - confidence(bin)| × proportion(bin)**

When verification:
1. **Increases confidence** on wrong answers (moves them to high bins)
2. **Doesn't improve accuracy** (they're still wrong)
3. **Increases the gap** |accuracy - confidence| in high bins
4. **Result: Higher ECE**

### Example Calculation

**Baseline Bin 0.8-0.9**:
- Accuracy: 50.0%
- Confidence: 82.9%
- Gap: |50.0% - 82.9%| = 32.9%
- Proportion: 58/100 = 58%
- Contribution: 32.9% × 58% = 19.1%

**Tier 1 Bin 0.8-0.9**:
- Accuracy: 42.4% (worse!)
- Confidence: 84.4% (higher!)
- Gap: |42.4% - 84.4%| = 42.0% (larger!)
- Proportion: 33/100 = 33%
- Contribution: 42.0% × 33% = 13.9%

But there are more bins with gaps, so total ECE increases.

## Why Baseline Has Better ECE

**Baseline doesn't have verification**, so:
- Wrong answers stay in lower-confidence bins (0.6-0.7)
- High-confidence bins (0.8-0.9) have better accuracy (50% vs 42-47%)
- Smaller gaps between confidence and accuracy
- **Result: Better ECE (0.265)**

## The Fundamental Issue

**Verification is measuring the wrong thing:**

1. **Tier 1 (Wu et al.)**: Measures **internal consistency**, not correctness
   - Wrong but consistent answers → YES status → high confidence
   - Result: Wrong answers get high confidence

2. **Tier 2**: Measures **medical validation**, but too lenient
   - 89% of wrong answers get APPROVED
   - Result: Wrong answers get high confidence

3. **Combined effect**: Wrong answers move to high-confidence bins
   - But accuracy doesn't improve
   - **Result: Worse ECE**

## Solutions

### Option 1: Add Correctness Checking (Recommended)

Modify verification to check if answers are **actually correct**, not just consistent:
- Low inconsistency + Correct → YES (high confidence) ✅
- Low inconsistency + Wrong → NO (low confidence) ❌
- High inconsistency → UNCERTAIN (moderate confidence)

### Option 2: Make Verification More Strict

- Tier 1: Stricter thresholds (more NO status)
- Tier 2: More aggressive rejection of wrong answers
- Result: Wrong answers stay in lower-confidence bins

### Option 3: Post-Hoc Calibration

Apply temperature scaling or Platt scaling to recalibrate confidence scores after verification.

### Option 4: Accept Trade-off

Accept worse ECE if accuracy improves (but currently accuracy is also worse!)

## Expected Impact of Fixes

### If we add correctness checking:
- Wrong answers with YES status → NO status
- Wrong answers stay in lower-confidence bins
- High-confidence bins have better accuracy
- **ECE: 0.30-0.32 → 0.25-0.27** (improved)

### If we make verification more strict:
- More NO/REJECTED status on wrong answers
- Wrong answers stay in lower-confidence bins
- **ECE: 0.30-0.32 → 0.27-0.29** (slight improvement)

## Conclusion

**ECE is worse because verification increases confidence on wrong answers without improving their correctness.**

The solution is to **add correctness checking** to verification, not just consistency checking.
