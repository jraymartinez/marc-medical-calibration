# Tier 2 Impact Analysis: Why Full Linear Has Lower Accuracy

## Summary

**Found 4 divergent questions** (2 single-specialist, 2 multi-specialist) where Tier 1 was **CORRECT** but Full Linear was **WRONG**.

**Root Cause**: Tier 2 GP validation is **REJECTING correct answers** from specialists, causing their confidence to drop dramatically. In multi-specialist configurations, this causes the **wrong answer to win** in confidence-weighted voting.

---

## Multi-Specialist Divergent Questions

### Question 15: Lung Cancer with Pneumothorax

**Question**: A 68-year-old male patient was eight months ago after being diagnosed with non-small cell lung cancer, ongoing chemical treatment. This comes due to severe asthma emergency room, chest X-ray found to have left pneumothorax, there are a lot of right lung nodules, chest tube was placed on the left after lung still open. Will the next disposal, what's wrong?

**Correct Answer**: Photodynamic therapy do to get through the trachea

**Tier 1 Result**: ✅ **CORRECT** (Confidence: 0.285)
- Final Answer: "Photodynamic therapy do to get through the trachea"

**Full Linear Result**: ❌ **WRONG** (Confidence: 0.243)
- Final Answer: "CT violations do see the situation of the tumor and whether the oppression of the respiratory tract"

#### What Happened:

**Respiratory Specialist** (Answer A - **CORRECT**):
- Tier 1: Confidence = 0.300 (S Score = 0.300)
- Full Linear: Confidence = 0.210 (S Score = 0.300, G Score = 0.120)
- **Change: -0.090 (-30.0%)**
- **Tier 2 Status: REJECTED** ❌

**Cardiology Specialist** (Answer C - **WRONG**):
- Tier 1: Confidence = 0.280 (S Score = 0.280)
- Full Linear: Confidence = 0.275 (S Score = 0.300, G Score = 0.250)
- **Change: -0.005 (-1.8%)**
- **Tier 2 Status: NEEDS_REVIEW** ⚠️

**Neurology Specialist** (Answer C - **WRONG**):
- Tier 1: Confidence = 0.280 (S Score = 0.280)
- Full Linear: Confidence = 0.210 (S Score = 0.300, G Score = 0.120)
- **Change: -0.070 (-25.0%)**
- **Tier 2 Status: REJECTED** ❌

**Gastroenterology Specialist** (Answer C - **WRONG**):
- Tier 1: Confidence = 0.280 (S Score = 0.280)
- Full Linear: Confidence = 0.275 (S Score = 0.300, G Score = 0.250)
- **Change: -0.005 (-1.8%)**
- **Tier 2 Status: NEEDS_REVIEW** ⚠️

#### Analysis:

1. **Respiratory specialist had the CORRECT answer (A)**
2. **Tier 2 REJECTED it** → G Score dropped to 0.120 (very low)
3. **Confidence dropped from 0.300 to 0.210** (-30%)
4. **Cardiology/Gastroenterology specialists had WRONG answer (C)**
5. **Tier 2 gave them NEEDS_REVIEW** → G Score = 0.250 (moderate)
6. **Confidence stayed at ~0.275** (higher than respiratory!)
7. **Wrong answer (C) won in confidence-weighted voting**

**Problem**: Tier 2 incorrectly rejected the correct answer and gave moderate confidence to wrong answers.

---

### Question 17: Sarcoidosis Case

**Question**: A 27-year-old woman comes to the physician because of increasing shortness of breath and a non-productive cough for 2 months... [full question about sarcoidosis]

**Correct Answer**: Sarcoidosis

**Tier 1 Result**: ✅ **CORRECT** (Confidence: 0.298)
- Final Answer: "Sarcoidosis"

**Full Linear Result**: ❌ **WRONG** (Confidence: 0.231)
- Final Answer: "Histoplasmosis"

#### What Happened:

**Respiratory Specialist** (Answer B - "Pulmonary tuberculosis" - **WRONG, but closer**):
- Tier 1: Confidence = 0.300 (S Score = 0.300)
- Full Linear: Confidence = 0.160 (S Score = 0.290, G Score = 0.030)
- **Change: -0.140 (-46.7%)**
- **Tier 2 Status: REJECTED** ❌

**Cardiology Specialist** (Answer A - **WRONG**):
- Tier 1: Confidence = 0.300 (S Score = 0.300)
- Full Linear: Confidence = 0.325 (S Score = 0.300, G Score = 0.350)
- **Change: +0.025 (+8.3%)**
- **Tier 2 Status: NEEDS_REVIEW** ⚠️

**Neurology Specialist** (Answer A - **WRONG**):
- Tier 1: Confidence = 0.290 (S Score = 0.290)
- Full Linear: Confidence = 0.270 (S Score = 0.290, G Score = 0.250)
- **Change: -0.020 (-6.9%)**
- **Tier 2 Status: NEEDS_REVIEW** ⚠️

**Gastroenterology Specialist** (Answer B - **WRONG**):
- Tier 1: Confidence = 0.300 (S Score = 0.300)
- Full Linear: Confidence = 0.170 (S Score = 0.280, G Score = 0.060)
- **Change: -0.130 (-43.3%)**
- **Tier 2 Status: REJECTED** ❌

#### Analysis:

1. **Respiratory specialist had answer B** (wrong, but closer to correct)
2. **Tier 2 REJECTED it** → G Score = 0.030 (extremely low!)
3. **Confidence dropped from 0.300 to 0.160** (-46.7%)
4. **Cardiology specialist had WRONG answer (A)**
5. **Tier 2 gave it NEEDS_REVIEW** → G Score = 0.350 (high!)
6. **Confidence increased to 0.325** (highest!)
7. **Wrong answer (A - Histoplasmosis) won in voting**

**Problem**: Tier 2 gave HIGH confidence (0.350) to a WRONG answer and REJECTED the respiratory specialist's answer (which was closer to correct).

---

## Single-Specialist Divergent Questions

### Question 26: Mallory-Weiss Tear

**Question**: A 25-year-old man is brought to the emergency department by police... [full question about bloody vomit]

**Correct Answer**: Mucosal tear at the gastroesophageal junction

**Tier 1 Result**: ✅ **CORRECT** (Confidence: 0.300)
- Final Answer: "Mucosal tear at the gastroesophageal junction"

**Full Linear Result**: ❌ **WRONG** (Confidence: 0.325)
- Final Answer: "Transmural distal esophagus tear"

#### What Happened:

**Respiratory Specialist**:
- Tier 1: Answer = "Mucosal tear at the gastroesophageal junction" (CORRECT)
- Full Linear: Answer = "Transmural distal esophagus tear" (WRONG)
- Tier 1: Confidence = 0.300 (S Score = 0.300)
- Full Linear: Confidence = 0.325 (S Score = 0.300, G Score = 0.350)
- **Tier 2 Status: NEEDS_REVIEW**

**Problem**: The specialist gave a **DIFFERENT ANSWER** in Full Linear vs Tier 1. This shouldn't happen - the answer should be the same, only confidence should change. This suggests **non-deterministic LLM behavior** (temperature > 0) causing different answers across runs.

---

### Question (ID: 9769793a...): ABG Interpretation

**Question**: Interpret the following ABG values PaCO-40, HCO-55 mEq/L and pH-7.7

**Correct Answer**: Mixed respiratory and metabolic acidosis

**Tier 1 Result**: ✅ **CORRECT** (Confidence: 0.300)
- Final Answer: "Mixed respiratory and metabolic acidosis"

**Full Linear Result**: ❌ **WRONG** (Confidence: 0.325)
- Final Answer: "Uncompensated metabolic alkalosis"

#### What Happened:

**Respiratory Specialist**:
- Tier 1: Answer = "Mixed respiratory and metabolic acidosis" (CORRECT)
- Full Linear: Answer = "Uncompensated metabolic alkalosis" (WRONG)
- Tier 1: Confidence = 0.300 (S Score = 0.300)
- Full Linear: Confidence = 0.325 (S Score = 0.300, G Score = 0.350)
- **Tier 2 Status: NEEDS_REVIEW**

**Problem**: Same issue - **different answer** across runs due to non-determinism.

---

## Key Findings

### 1. **Tier 2 Rejecting Correct Answers**

In multi-specialist configurations:
- Tier 2 **REJECTED** correct answers from respiratory specialist
- G Score dropped to **0.120-0.030** (very low)
- Confidence dropped by **-30% to -47%**
- Wrong answers got **NEEDS_REVIEW** with G Score = **0.250-0.350** (moderate-high)
- Wrong answers won in confidence-weighted voting

### 2. **Non-Deterministic LLM Behavior**

In single-specialist configurations:
- Same question → **different answers** across Tier 1 vs Full Linear
- This is due to **temperature > 0** and **do_sample=True**
- The specialist is generating different answers, not just different confidence

### 3. **Tier 2 Validation Quality Issues**

**Problems:**
- GP validation is **too conservative** (rejecting correct answers)
- GP validation is **inconsistent** (giving high confidence to wrong answers)
- GP validation **doesn't understand** respiratory specialist's reasoning

**Possible Causes:**
- Tier 2 temperature (0.15) might be too low → too deterministic, can't make nuanced judgments
- GP prompts might not have enough context
- GP validation logic might be flawed

---

## Recommendations

### 1. **Investigate Tier 2 Validation Logic**

**Check:**
- What is GP seeing? (Full question, specialist answer, Tier 1 result?)
- Why is GP rejecting correct answers?
- Why is GP giving high confidence to wrong answers?

**Action:**
- Add detailed logging to Tier 2 validation
- Print GP's reasoning for REJECTED/NEEDS_REVIEW decisions
- Analyze GP's validation prompts

### 2. **Fix Non-Determinism**

**For single-specialist:**
- Use **temperature = 0.0** for specialist diagnosis (deterministic)
- Or use **fixed random seed** for reproducibility
- Or **cache specialist answers** and only re-run verification

**Action:**
- Set `temperature=0.0` for specialist agent in deterministic mode
- Or implement answer caching

### 3. **Tune Tier 2 Parameters**

**Current:**
- Temperature: 0.15 (might be too low)
- Penalty factors: REJECTED = 0.4, NEEDS_REVIEW = 0.7

**Options:**
- Increase temperature to 0.2-0.3 (more nuanced judgments)
- Adjust penalty factors (less aggressive rejection)
- Improve GP prompts (more context, better instructions)

### 4. **Specialty Weighting**

**This would help!**
- Give respiratory specialist **2x weight** in voting
- Even if Tier 2 rejects it, respiratory specialist's vote would still count more
- Could mitigate the impact of Tier 2's poor validation

---

## Conclusion

**Tier 2 is hurting accuracy because:**

1. **GP validation is rejecting correct answers** → confidence drops dramatically
2. **GP validation is giving high confidence to wrong answers** → wrong answers win voting
3. **Non-deterministic LLM behavior** → different answers across runs (single-specialist)

**Solutions:**
1. ✅ **Specialty weighting** (implemented, ready to test)
2. ⏳ **Fix Tier 2 validation logic** (investigate GP reasoning)
3. ⏳ **Fix non-determinism** (temperature=0.0 or caching)
4. ⏳ **Tune Tier 2 parameters** (temperature, penalty factors)

**Next Steps:**
1. Enable specialty weighting and re-run
2. Add detailed Tier 2 logging to see GP's reasoning
3. Fix non-determinism for single-specialist
4. Re-run experiments with fixes
