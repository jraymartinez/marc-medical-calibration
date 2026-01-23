# Root Cause Analysis: Multi-Agent + Two-Phase Verification Accuracy Decline

## Executive Summary

**Problem**: Multi-Agent + Two-Phase Verification has **60% accuracy** vs **70%** for all other configurations (10% drop).

**Root Causes Identified**:
1. **Two-Phase Verification giving YES to wrong answers** (inconsistency=0.0 doesn't mean correctness)
2. **Fusion logic too aggressive** ("strong_yes_shortcut" trusts single verified answer without validation)
3. **Specialist agents giving wrong answers** (11/12 wrong cases had NO specialist with correct answer)
4. **Poor S_score discrimination** (Formula 1: 0.047 gap, Formula 2: -0.077 gap)

---

## 1. Overall Metrics Comparison

| Configuration | Formula 1 | Formula 2 |
|--------------|-----------|-----------|
| Single Specialist | 70.0% | 70.0% |
| Single Specialist + Two-Phase | 70.0% | 70.0% |
| Multi-Agent (No Verification) | 70.0% | 70.0% |
| **Multi-Agent + Two-Phase** | **60.0%** | **60.0%** |

**Key Finding**: Both formulas perform identically (60% accuracy), suggesting the problem is in fusion logic, not S_score formula.

---

## 2. Critical Issues Identified

### 2.1 Two-Phase Verification False Positives

**Problem**: Two-Phase Verification is giving `verified_status='YES'` (inconsistency < 0.15) to **wrong answers**.

**Examples**:
- **Q3**: Cardiology got `YES` (inconsistency=0.0) but gave **wrong answer B** (correct is A)
- **Q4**: Neurology got `YES` (inconsistency=0.0) but gave **wrong answer B** (correct is C)  
- **Q29**: Respiratory + Gastroenterology both got `YES` (inconsistency=0.0) but gave **wrong answer B**

**Root Cause**: **Consistency ≠ Correctness**. A model can be perfectly consistent in being wrong. Inconsistency=0.0 means the model's independent and reference answers agree, but doesn't guarantee medical correctness.

### 2.2 Fusion Logic "strong_yes_shortcut" Too Aggressive

**Current Logic** (lines 192-197 in `run_final_comparison.py`):
```python
if len(strong_yes_specialists) == 1:
    best = strong_yes_specialists[0]
    final_answer = best['answer']
    final_confidence = min(1.0, best['confidence'] * 1.4)  # 40% boost!
    fusion_reason = "strong_yes_shortcut"
```

**Problem**: This immediately picks a single verified answer without:
- Checking if other specialists disagree
- Validating the answer makes medical sense
- Considering that verified_status='YES' can be wrong

**Impact**: 
- Q3: Picked Cardiology's wrong answer B (got YES) over correct answer A from Neurology+GP
- Q4: Picked Neurology's wrong answer B (got YES) over correct answer C

### 2.3 Specialist Agents Giving Wrong Answers

**Finding**: **11 out of 12 wrong answers** had **NO specialist giving the correct answer**.

**Examples**:
- Q2: All 5 specialists gave C (correct is "Normal heart tissue" - not in options?)
- Q3: Correct answer A only given by Neurology (0.450 S_score) and GP (0.617 S_score), but Cardiology's wrong B (0.950 S_score, YES) was chosen
- Q6: All specialists gave wrong answers (correct is "Sensorineural hearing loss")
- Q7: All specialists gave wrong answers (correct is "Administer intravenous fluids")

**Root Cause**: The specialist agents themselves are making errors. Two-Phase Verification can't fix wrong answers if no specialist has the correct answer.

### 2.4 Poor S_score Discrimination

**Formula 1 (Weighted Average)**:
- Correct answers: Mean S_score = 0.867
- Wrong answers: Mean S_score = 0.819
- **Discrimination gap: 0.047** (very small)

**Formula 2 (Multiplicative)**:
- Correct answers: Mean S_score = 0.689
- Wrong answers: Mean S_score = 0.766
- **Discrimination gap: -0.077** (WRONG DIRECTION - worse than random!)

**Root Cause**: 
- Formula 1: S_scores are too high for both correct and wrong answers (ceiling effect)
- Formula 2: Multiplicative formula penalizes correct answers more than wrong answers (inconsistency scores are misleading)

---

## 3. Detailed Question Analysis

### 3.1 Questions Where Multi-Agent + Two-Phase Got Wrong But Others Got Right

**Q3**: "Increase in length constant"
- **Correct**: A
- **MA+TP Selected**: B (Conf: 0.950) - **WRONG**
- **MA (No Verif) Selected**: A (Conf: 0.891) - **CORRECT**
- **Fusion Reason**: `strong_yes_shortcut`
- **Problem**: Cardiology got `YES` (inconsistency=0.0) for wrong answer B, fusion logic trusted it blindly

**Q8**: "Type III hypersensitivity"
- **Correct**: C
- **MA+TP Selected**: D (Conf: 0.700) - **WRONG**
- **MA (No Verif) Selected**: C (Conf: 0.891) - **CORRECT**
- **Fusion Reason**: `max_s_override_majority`
- **Problem**: Respiratory had highest S_score (0.700) for wrong answer D, but correct answer C had lower S_scores (0.450)

**Q26**: "Shingles vaccine"
- **Correct**: D
- **MA+TP Selected**: B (Conf: 0.575) - **WRONG**
- **MA (No Verif) Selected**: D (Conf: 0.891) - **CORRECT**
- **Fusion Reason**: `max_s_no_majority`
- **Problem**: Respiratory had highest S_score (0.575) for wrong answer B, but correct answer D had same S_score (0.575) from Neurology and GP

### 3.2 Fusion Reason Distribution

**Wrong Answers**:
- `max_s_override_majority`: 5 cases (42%)
- `gp_fallback`: 4 cases (33%)
- `strong_yes_shortcut`: 2 cases (17%)
- `max_s_no_majority`: 1 case (8%)

**Correct Answers**:
- `gp_fallback`: 10 cases (56%)
- `strong_yes_shortcut`: 4 cases (22%)
- `max_s_override_majority`: 4 cases (22%)

**Key Finding**: `max_s_override_majority` is causing 5 wrong answers but only 4 correct answers (net negative).

---

## 4. What We're Doing Wrong

### 4.1 Misunderstanding Two-Phase Verification

**Our Assumption**: `verified_status='YES'` means the answer is correct.

**Reality**: `verified_status='YES'` only means the model is **consistent** (low inconsistency), not that it's **correct**.

**Wu et al. 2024 Method**: Two-Phase Verification measures **uncertainty** (inconsistency), not correctness. A model can be:
- Consistent and correct (good)
- Consistent and wrong (bad - our problem)
- Inconsistent and correct (uncertain)
- Inconsistent and wrong (uncertain and wrong)

### 4.2 Over-Trusting Single Verified Answers

**Problem**: The `strong_yes_shortcut` trusts a single specialist's verified answer without:
1. Checking if other specialists disagree
2. Validating medical plausibility
3. Considering that consistency ≠ correctness

**Solution Needed**: Require **consensus** or **majority** even for verified answers, or add additional validation.

### 4.3 S_score Formula Issues

**Formula 1 (Weighted Average)**: `S = 0.5 * initial + 0.5 * verification`
- **Problem**: Both correct and wrong answers get high S_scores (ceiling effect)
- **Why**: Initial confidence is often high (0.7-0.95), and verification confidence is also high for consistent (but wrong) answers

**Formula 2 (Multiplicative)**: `S = initial * (1 - inconsistency)`
- **Problem**: Wrong answers get HIGHER S_scores than correct answers (negative discrimination)
- **Why**: Correct answers may have higher inconsistency (model is uncertain), while wrong answers have low inconsistency (model is confidently wrong)

### 4.4 Specialist Knowledge Limitations

**Finding**: Many questions have **no specialist giving the correct answer**.

**Possible Causes**:
1. **Model knowledge gaps**: Llama 3.1 8B may not have sufficient medical knowledge
2. **Prompt design**: Specialist prompts may not be guiding the model correctly
3. **Temperature settings**: Current temperature (0.3) may be too low, reducing exploration

---

## 5. Recommendations

### 5.1 Fix Fusion Logic

**Remove or Modify "strong_yes_shortcut"**:
- **Option A**: Remove it entirely - require consensus even for verified answers
- **Option B**: Require at least 2 specialists with verified_status='YES' for the same answer
- **Option C**: Add a "medical plausibility check" before trusting verified answers

**Modify "max_s_override_majority"**:
- **Current**: Overrides majority if max S_score > 0.35 and gap > 0.03
- **Problem**: Wrong answers can have high S_scores
- **Solution**: Require larger gap (0.10+) or require verified_status='YES' for override

### 5.2 Improve Two-Phase Verification

**Current Thresholds**:
- `YES`: inconsistency < 0.15
- `UNCERTAIN`: inconsistency < 0.5
- `NO`: inconsistency >= 0.5

**Problem**: Too lenient - many wrong answers get `YES`.

**Proposed Fix**:
- **Stricter thresholds**: `YES` only if inconsistency < 0.10 AND initial confidence > 0.8
- **Add medical validation**: Even if consistent, check if answer makes medical sense
- **Consider answer diversity**: If all specialists give same wrong answer with low inconsistency, that's a red flag

### 5.3 Fix S_score Formula

**Formula 1 Issues**: Too high for both correct and wrong (ceiling effect)

**Formula 2 Issues**: Negative discrimination (wrong > correct)

**Proposed Solutions**:
1. **Hybrid approach**: Use Formula 1 but with stricter inconsistency penalties
2. **Calibration**: Apply temperature scaling or Platt scaling to S_scores
3. **New formula**: `S = initial * (1 - inconsistency)^2` (quadratic penalty for inconsistency)

### 5.4 Improve Specialist Agents

**Options**:
1. **Better prompts**: More explicit instructions about medical reasoning
2. **Higher temperature**: Increase from 0.3 to 0.4-0.5 for more exploration
3. **Chain-of-thought**: Require explicit reasoning before giving answer
4. **Larger model**: Consider Llama 3.1 70B if available (better knowledge)

### 5.5 Add Answer Validation

**Before final selection, validate**:
1. **Medical plausibility**: Does the answer make sense for the symptoms?
2. **Consensus check**: Do multiple specialists agree (even if not verified)?
3. **Confidence threshold**: Require minimum confidence (e.g., 0.6) before selecting

---

## 6. Immediate Action Items

### Priority 1: Fix Fusion Logic
1. **Remove or modify "strong_yes_shortcut"** - it's causing 2 wrong answers
2. **Require consensus for verified answers** - don't trust single verified specialist
3. **Increase gap threshold for "max_s_override_majority"** - from 0.03 to 0.10

### Priority 2: Improve S_score Discrimination
1. **Test hybrid S_score formula**: `S = initial * (1 - inconsistency)^1.5`
2. **Apply calibration**: Temperature scaling to S_scores
3. **Stricter inconsistency thresholds**: YES only if < 0.10

### Priority 3: Validate Specialist Answers
1. **Add medical plausibility check** before final selection
2. **Require minimum 2 specialists agreeing** for verified answers
3. **Check answer diversity** - if all specialists give same answer with low inconsistency, investigate

---

## 7. Expected Impact

**If we fix fusion logic**:
- Remove "strong_yes_shortcut" → +2 correct answers (Q3, Q4) → **62% → 67% accuracy**
- Fix "max_s_override_majority" → +2-3 correct answers → **67% → 70-73% accuracy**

**If we improve S_score discrimination**:
- Better separation between correct/wrong → Higher AUROC (0.6-0.7 target)
- Lower ECE (better calibration)

**If we improve specialist agents**:
- More correct answers at source → Higher overall accuracy
- Better foundation for Two-Phase Verification to work on

---

## 8. Conclusion

**Main Problem**: We're treating **consistency** (Two-Phase Verification) as a proxy for **correctness**, but they're different concepts. A model can be consistently wrong.

**Solution**: 
1. **Don't trust single verified answers** - require consensus
2. **Improve S_score discrimination** - current formulas don't separate correct/wrong well
3. **Add validation layers** - medical plausibility, consensus checks
4. **Fix specialist agents** - they're the source of many wrong answers

**Target**: Get Multi-Agent + Two-Phase Verification to **70%+ accuracy** and **AUROC 0.6-0.7**.
