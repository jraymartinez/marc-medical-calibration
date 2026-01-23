# Improvements Impact Analysis

## Date: January 22, 2025

---

## Executive Summary

**Results After All Improvements**:
- ✅ **Accuracy**: 60.0% → 63.3% (+3.3%, +1 question)
- ✅✅ **ECE**: 0.771 → 0.375 (-0.396, **HUGE improvement!**)
- ❌ **AUROC**: 0.604 → 0.426 (-0.178, worse)
- ❌ **S_score Discrimination**: Gap 0.048 → -0.041 (negative, worse!)

**Key Finding**: **Calibration improved dramatically (ECE), but discrimination got worse (AUROC, S_score gap)**.

---

## 1. Overall Metrics Comparison

| Metric | Previous (No GP) | Current (All Improvements) | Change |
|--------|------------------|----------------------------|--------|
| **Accuracy** | 60.0% (18/30) | 63.3% (19/30) | **+3.3%** ✅ |
| **ECE** | 0.771 | 0.375 | **-0.396** ✅✅ |
| **AUROC** | 0.604 | 0.426 | **-0.178** ❌ |
| **S_score Gap** | 0.048 | -0.041 | **-0.089** ❌ |

**Net Result**: 
- ✅ Calibration dramatically improved (ECE)
- ✅ Accuracy slightly improved
- ❌ Discrimination worsened (AUROC, S_score gap)

---

## 2. Questions That Changed

### Improved (Wrong → Correct): 7 questions
- **Q4, Q8, Q9, Q12, Q17, Q21, Q24**

### Worsened (Correct → Wrong): 6 questions
- **Q6, Q10, Q13, Q16, Q19, Q28**

**Net**: +7 improved, -6 worsened = +1 net improvement

---

## 3. What Helped (Improved Questions)

### Q4: "Meningioma"
- **Previous**: Wrong (B), Fusion: `max_s_yield_to_majority`
- **Current**: Correct (Meningioma), Fusion: `max_s_no_majority`
- **Key**: Cardiology and Gastroenterology got correct answer with S_scores 0.565 and 0.597
- **What Helped**: Lowered S_score threshold (0.45 → 0.40) allowed minority correct answer to be selected

### Q8: "Type III hypersensitivity"
- **Previous**: Wrong (D), Fusion: `max_s_yield_to_majority`
- **Current**: Correct (Type III hypersensitivity), Fusion: `max_s_no_majority`
- **Key**: Neurology got correct answer with S_score 0.635
- **What Helped**: Lowered S_score threshold allowed minority correct answer

### Q9: "Decreased physiologic dead space"
- **Previous**: Wrong (C), Fusion: `max_s_no_majority`
- **Current**: Correct (B), Fusion: `max_s_no_majority`
- **Key**: Respiratory got verified_status='YES' (inconsistency=0.0) for correct answer B
- **What Helped**: Stricter thresholds (YES requires inconsistency < 0.10 AND initial confidence > 0.8) - Respiratory met both

### Q12: "21-hydroxylase"
- **Previous**: Wrong (A), Fusion: `max_s_yield_to_majority`
- **Current**: Correct (21-hydroxylase), Fusion: `max_s_yield_to_majority`
- **Key**: All 4 specialists got correct answer! (consensus)
- **What Helped**: Improved specialist prompts/knowledge bases - all specialists now correct

### Q17: "Herpes simplex virus"
- **Previous**: Wrong (B), Fusion: `max_s_yield_to_majority`
- **Current**: Correct (Herpes simplex virus), Fusion: `max_s_no_majority`
- **Key**: Respiratory and Neurology got correct answer
- **What Helped**: Lowered S_score threshold allowed minority correct answer

### Q21: "Urinary tract infection"
- **Previous**: Wrong (B), Fusion: `max_s_no_majority`
- **Current**: Correct (A), Fusion: `max_s_override_majority`
- **Key**: Cardiology got verified_status='YES' (inconsistency=0.0) for correct answer A
- **What Helped**: Stricter thresholds + improved override logic - Cardiology's verified answer overrode

### Q24: "Renal failure"
- **Previous**: Wrong (D), Fusion: `max_s_yield_to_majority`
- **Current**: Correct (C), Fusion: `max_s_override_majority`
- **Key**: Respiratory got verified_status='YES' (inconsistency=0.0) for correct answer C
- **What Helped**: Stricter thresholds + improved override logic

**Pattern**: 
- **Lowered S_score threshold** helped catch minority correct answers (Q4, Q8, Q17)
- **Stricter verification thresholds** helped identify correct verified answers (Q9, Q21, Q24)
- **Improved specialist prompts/knowledge** helped all specialists get correct (Q12)

---

## 4. What Hurt (Worsened Questions)

### Q6: "Sensorineural hearing loss"
- **Previous**: Correct (C), Fusion: `max_s_yield_to_majority`
- **Current**: Wrong (A), Fusion: `max_s_no_majority`
- **Key**: All specialists gave wrong answers, Neurology gave correct C but with low S_score (0.630)
- **What Hurt**: Lowered S_score threshold allowed wrong answer A (S_score 0.630) to be selected over correct C

### Q10: "Expulsion by the mucociliary escalator"
- **Previous**: Correct (B), Fusion: `max_s_override_majority`
- **Current**: Wrong (C), Fusion: `max_s_no_majority`
- **Key**: Respiratory gave wrong answer C with S_score 0.719 (UNCERTAIN)
- **What Hurt**: Fusion logic selected wrong answer C instead of correct B

### Q13: "Perform colonoscopy"
- **Previous**: Correct (A), Fusion: `max_s_yield_to_majority`
- **Current**: Wrong (Perform 24-hour ECG), Fusion: `max_s_no_majority`
- **Key**: Cardiology got verified_status='YES' for **wrong answer** (24-hour ECG)
- **What Hurt**: Stricter thresholds still gave YES to wrong answer - Cardiology got YES but was wrong!

### Q16: "Rifampin"
- **Previous**: Correct (A), Fusion: `max_s_yield_to_majority`
- **Current**: Wrong (B), Fusion: `max_s_yield_to_majority`
- **Key**: All specialists gave wrong answer B
- **What Hurt**: Improved prompts/knowledge didn't help - all specialists still wrong

### Q19: "Decreasing the physiologic dead space"
- **Previous**: Correct (C), Fusion: `max_s_override_majority`
- **Current**: Wrong (Decreasing the physiologic dead space), Fusion: `max_s_no_majority`
- **Key**: Neurology got verified_status='YES' for wrong answer (text format issue?)
- **What Hurt**: Answer format mismatch - specialists gave text, correct is letter C

### Q28: "Skeletal muscle"
- **Previous**: Correct (C), Fusion: `max_s_yield_to_majority`
- **Current**: Wrong (A), Fusion: `max_s_override_majority`
- **Key**: Gastroenterology got wrong answer A with S_score 0.757 (UNCERTAIN)
- **What Hurt**: Override logic selected wrong answer A

**Pattern**:
- **Lowered S_score threshold** sometimes selected wrong answers (Q6)
- **Stricter thresholds still gave YES to wrong answers** (Q13, Q19)
- **Answer format issues** (Q19 - text vs letter)
- **All specialists wrong** (Q16)

---

## 5. Critical Issues Identified

### 5.1 S_score Discrimination Got Worse

**Previous**: 
- Correct: Mean=0.869, Wrong: Mean=0.821, Gap=0.048

**Current**:
- Correct: Mean=0.746, Wrong: Mean=0.787, Gap=-0.041

**Problem**: **Wrong answers now have HIGHER S_scores than correct answers!**

**Root Cause**: **Hybrid formula is hurting discrimination**
- Formula: `S = 0.7 * initial + 0.3 * verification * (1 - inconsistency)^2`
- The quadratic penalty `(1 - inconsistency)^2` might be too aggressive
- Correct answers with moderate inconsistency get penalized more than wrong answers with low inconsistency

### 5.2 AUROC Got Worse

**Previous**: 0.604
**Current**: 0.426

**Problem**: Discrimination ability decreased.

**Root Cause**: S_score discrimination got worse (negative gap), so AUROC decreased.

### 5.3 ECE Dramatically Improved

**Previous**: 0.771
**Current**: 0.375

**What Helped**: 
- **Calibration** (temperature scaling `S_score^0.9`)
- **Better confidence estimates** (75% calibrated S_score + 25% fusion)
- **Stricter thresholds** (fewer false positives)

**This is a HUGE win!** ECE improvement of 0.396 is massive.

### 5.4 Verified Status Distribution

**Previous**: YES=15, UNCERTAIN=26, NO=79
**Current**: YES=8, UNCERTAIN=26, NO=86

**What Changed**:
- **Stricter thresholds** reduced YES from 15 to 8 (47% reduction)
- This is good - fewer false positives
- But some wrong answers still get YES (Q13, Q19)

---

## 6. What Actually Helped

### ✅ 1. Lowered S_score Threshold (0.45 → 0.40)
- **Helped**: Q4, Q8, Q17 (minority correct answers selected)
- **Hurt**: Q6 (wrong answer selected)
- **Net**: Positive (3 helped, 1 hurt)

### ✅ 2. Stricter Verification Thresholds
- **Helped**: Q9, Q21, Q24 (correct verified answers identified)
- **Hurt**: Q13, Q19 (wrong answers still got YES)
- **Net**: Positive (3 helped, 2 hurt, but fewer false positives overall)

### ✅ 3. Improved Specialist Prompts/Knowledge Bases
- **Helped**: Q12 (all specialists got correct)
- **Hurt**: Q16 (all specialists still wrong)
- **Net**: Mixed (1 helped, 1 hurt, but overall better reasoning)

### ✅✅ 4. Calibration (Temperature Scaling)
- **Helped**: ECE dramatically improved (0.771 → 0.375)
- **Net**: **HUGE win!**

### ❌ 5. Hybrid S_score Formula
- **Hurt**: S_score discrimination got worse (gap 0.048 → -0.041)
- **Hurt**: AUROC got worse (0.604 → 0.426)
- **Net**: **Negative** - formula is hurting discrimination

### ✅ 6. Improved Fusion Logic
- **Helped**: Better handling of disagreements (Q4, Q8, Q17, Q21, Q24)
- **Net**: Positive

---

## 7. Recommendations

### Priority 1: Fix Hybrid S_score Formula

**Problem**: Hybrid formula is hurting discrimination (negative gap).

**Options**:
1. **Revert to weighted average**: `S = 0.5 * initial + 0.5 * verification`
2. **Less aggressive penalty**: `S = 0.7 * initial + 0.3 * verification * (1 - inconsistency)` (linear, not quadratic)
3. **Different weights**: `S = 0.8 * initial + 0.2 * verification * (1 - inconsistency)^1.5` (less aggressive)

**Recommendation**: Try option 2 (linear penalty) or revert to weighted average.

### Priority 2: Fix Answer Format Issues

**Problem**: Q19 had text vs letter mismatch.

**Solution**: Improve answer parsing to handle both formats.

### Priority 3: Further Improve Specialist Prompts

**Problem**: Some questions still have all specialists wrong (Q16).

**Solution**: 
- More explicit chain-of-thought
- Better examples in prompts
- More detailed knowledge bases

### Priority 4: Keep Calibration

**Success**: ECE dramatically improved (0.771 → 0.375).

**Action**: Keep temperature scaling and calibration approach.

---

## 8. Conclusion

**What Worked**:
1. ✅ **Calibration** - ECE dramatically improved (0.771 → 0.375)
2. ✅ **Lowered S_score threshold** - Caught more minority correct answers
3. ✅ **Stricter verification thresholds** - Fewer false positives (YES: 15 → 8)
4. ✅ **Improved fusion logic** - Better handling of disagreements
5. ✅ **Improved specialist prompts** - Better reasoning (Q12 all correct)

**What Didn't Work**:
1. ❌ **Hybrid S_score formula** - Hurting discrimination (negative gap)
2. ❌ **Answer format handling** - Text vs letter mismatches
3. ❌ **Stricter thresholds still allow wrong YES** - Q13, Q19 got YES but wrong

**Next Steps**:
1. **Fix hybrid formula** - Revert to weighted average or use linear penalty
2. **Fix answer parsing** - Handle text/letter formats better
3. **Test again** - See if discrimination improves

**Target**: Get AUROC to 0.6-0.7 while maintaining ECE improvement.
