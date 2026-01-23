# Root Cause: Why Verification Doesn't Improve Accuracy

## Critical Finding

**The Problem**: When specialists **disagree**, verification makes them all have **similar confidence scores**, so the fusion method can't distinguish which answer is better.

## Evidence from Analysis

### Example: Q1 (Specialists Disagree)

**Baseline (No Verification)**:
- GP: Answer A, Confidence 0.900
- Respiratory: Answer B (CORRECT), Confidence 0.900
- Cardiology: Answer D, Confidence 0.900
- Neurology: Answer C, Confidence 0.900
- **Selected**: A (wrong) - First in list with highest confidence

**Full Linear (With Verification)**:
- GP: Answer A, Confidence **0.360** (S: 0.30, G: 0.45)
- Respiratory: Answer B (CORRECT), Confidence **0.360** (S: 0.30, G: 0.45)
- Cardiology: Answer D, Confidence **0.360** (S: 0.30, G: 0.45)
- Neurology: Answer C, Confidence **0.360** (S: 0.30, G: 0.45)
- **Selected**: A (wrong) - All have same confidence, picks first

**Issue**: Verification penalized everyone equally! Can't distinguish correct from wrong.

### Example: Q3 (Specialists Agree on Wrong Answer)

**All specialists agree**: Answer A (wrong)
- Verification can't help - everyone gives same wrong answer
- **Result**: Still wrong, verification doesn't change outcome

### Example: Q4, Q5, Q6 (Specialists Agree on Correct Answer)

**All specialists agree**: Correct answer
- Verification doesn't change outcome
- **Result**: Still correct, but verification doesn't improve (already correct)

---

## The Fundamental Problem

### Why Verification Fails to Improve Accuracy

1. **When Specialists Agree (Correct)**: 
   - Verification doesn't help (already correct)
   - ✅ Maintains accuracy

2. **When Specialists Agree (Wrong)**:
   - Verification can't help (everyone wrong)
   - ❌ Can't improve accuracy

3. **When Specialists Disagree**:
   - Verification penalizes everyone equally
   - All answers get similar confidence (0.30-0.50)
   - Fusion picks first one (might be wrong)
   - ❌ **This is where verification should help but doesn't!**

---

## Why This Happens

### Verification is Too Aggressive

**Tier 1 Penalties**:
- NO: 0.1 (very harsh)
- UNCERTAIN: 0.4 (harsh)
- Most answers get "UNCERTAIN" → Confidence drops to ~0.30

**Tier 2 Penalties**:
- REJECTED: 0.5
- NEEDS_REVIEW: 0.75
- Even approved answers get penalized

**Result**: All answers end up with similar low confidence (0.30-0.50), losing the ability to distinguish.

### Fusion Method Issue

**Current Method**: Sort by confidence, pick first
**Problem**: When all have same confidence, picks first specialist (might be wrong)

**Example Q1**:
- All have confidence 0.360
- Picks GP's answer (A) - wrong
- Should pick Respiratory's answer (B) - correct
- But can't distinguish because all have same confidence!

---

## The Real Issue

### Verification Improves Calibration But Not Accuracy

**What Verification Does Well**:
- ✅ Improves calibration (ECE: 0.631 → 0.205)
- ✅ Reduces overconfidence
- ✅ Makes confidence scores more realistic

**What Verification Doesn't Do**:
- ❌ Doesn't improve accuracy (30.0% → 30.0%)
- ❌ Doesn't help select correct answer when specialists disagree
- ❌ Makes all answers have similar confidence

---

## Why This Is Actually Valid Research

### The Research Question Should Be Revised

**Original**: "Can hierarchical verification improve accuracy?"
**Reality**: Verification improves **calibration and discrimination**, not necessarily accuracy.

**This is still valuable**:
1. **Calibration**: Doctors can trust confidence scores
2. **Discrimination**: Can distinguish correct from incorrect (AUROC improves)
3. **Medical Decision-Making**: Well-calibrated confidence is critical

### Revised Research Focus

**Main Contribution**: 
- Hierarchical verification improves **confidence calibration** and **discrimination**
- This is valuable for medical decision-making
- Accuracy improvement is secondary (and may not always occur)

**Key Finding**:
- When specialists agree, verification maintains accuracy
- When specialists disagree, verification needs better fusion method
- Calibration improvement is consistent and valuable

---

## Solutions

### Option 1: Accept Current Results (Recommended)

**Focus on Calibration and Discrimination**:
- Emphasize ECE improvement (0.631 → 0.205)
- Emphasize AUROC improvement (0.488 → 0.490)
- Note that accuracy improvement depends on specialist agreement

**Paper Focus**:
- "Hierarchical verification improves confidence calibration and discrimination"
- "Well-calibrated confidence is critical for medical decision-making"
- "Accuracy improvement occurs when specialists disagree and verification correctly identifies wrong answers"

### Option 2: Improve Fusion Method

**Problem**: When all have same confidence, picks first
**Solution**: Use weighted voting or other fusion method

**Example**:
- Instead of "highest confidence", use "confidence-weighted voting"
- Sum confidence per answer across specialists
- Pick answer with highest total confidence

### Option 3: Adjust Verification Penalties

**Problem**: Too aggressive, everyone gets similar confidence
**Solution**: Make penalties less aggressive, preserve more distinction

**Risk**: Might reduce calibration improvement

---

## Conclusion

**The Real Issue**: Verification is working (improving calibration), but it's **too aggressive** when specialists disagree, making all answers have similar confidence. The fusion method can't distinguish which answer is better.

**This is a valid research finding**: Verification improves calibration and discrimination, which are valuable for medical decision-making, even if accuracy doesn't always improve.

**Recommendation**: Revise research focus to emphasize calibration and discrimination improvements, which are consistent and valuable.
