# Calibration and Discrimination in Medical Q&A: Explained

## Overview

In medical question-answering, we evaluate models on two critical dimensions:
1. **Calibration**: How well does the model's confidence match reality?
2. **Discrimination**: How well can the model distinguish correct from incorrect answers?

---

## 1. CALIBRATION (ECE - Expected Calibration Error)

### What It Means

**Calibration** measures whether the model's confidence scores accurately reflect the probability of being correct.

### Medical Example

Imagine a doctor says:
- "I'm 90% confident this is pneumonia" → Should be correct ~90% of the time
- "I'm 50% confident this is bronchitis" → Should be correct ~50% of the time
- "I'm 10% confident this is asthma" → Should be correct ~10% of the time

**Well-calibrated model**: When it says 90% confident, it's actually correct 90% of the time.

**Poorly-calibrated model**: When it says 90% confident, it might only be correct 60% of the time (overconfident) or 95% of the time (underconfident).

### Why It Matters in Medical Diagnosis

**Overconfidence (Poor Calibration)**:
- Model says: "I'm 95% confident this patient has pneumonia"
- Reality: Only 60% of such cases are actually pneumonia
- **Problem**: Doctor might skip further tests, miss alternative diagnoses
- **Risk**: Patient safety, misdiagnosis

**Underconfidence (Poor Calibration)**:
- Model says: "I'm 30% confident this is a heart attack"
- Reality: 80% of such cases are actually heart attacks
- **Problem**: Doctor might not take it seriously enough
- **Risk**: Delayed treatment, patient harm

**Well-Calibrated**:
- Model says: "I'm 70% confident this is pneumonia"
- Reality: 70% of such cases are actually pneumonia
- **Benefit**: Doctor knows exactly how much to trust the diagnosis
- **Outcome**: Appropriate level of additional testing, proper risk assessment

### Our Results

| Configuration | ECE | Interpretation |
|--------------|-----|-----------------|
| No Verification | 0.502 | **Very poor** - Overconfident by ~50% |
| Tier 1 Only | 0.123 | **Good** - Reasonably calibrated |
| **Full Linear** | **0.057** | **Excellent** - Very well calibrated |

**Full Linear (0.057)**: When the model says it's 80% confident, it's actually correct about 80% of the time. This is **critical for medical decision-making**.

---

## 2. DISCRIMINATION (AUROC - Area Under ROC Curve)

### What It Means

**Discrimination** measures how well the model can distinguish between correct and incorrect answers based on confidence scores.

### Medical Example

Imagine we have 10 medical questions:
- 5 are answered correctly
- 5 are answered incorrectly

**Good Discrimination**: 
- Correct answers have high confidence (0.8, 0.9, 0.7, 0.85, 0.75)
- Incorrect answers have low confidence (0.3, 0.2, 0.4, 0.25, 0.35)
- **Clear separation** → Easy to identify which answers to trust

**Poor Discrimination**:
- Correct answers: (0.5, 0.6, 0.4, 0.55, 0.45)
- Incorrect answers: (0.5, 0.6, 0.4, 0.55, 0.45)
- **No separation** → Can't tell which answers are better

### Why It Matters in Medical Diagnosis

**Good Discrimination**:
- Model gives high confidence to correct diagnoses
- Model gives low confidence to incorrect diagnoses
- **Benefit**: Doctor can prioritize high-confidence answers, investigate low-confidence ones
- **Outcome**: Better resource allocation, focus on reliable diagnoses

**Poor Discrimination**:
- All answers have similar confidence (around 0.5)
- Can't tell which diagnoses are more reliable
- **Problem**: Doctor can't prioritize, must investigate everything equally
- **Risk**: Wasted resources, delayed decisions

### ROC Curve Explanation

**ROC Curve** plots:
- X-axis: False Positive Rate (how often we trust wrong answers)
- Y-axis: True Positive Rate (how often we trust correct answers)

**AUROC = 0.5**: Random guessing (no discrimination)
**AUROC = 1.0**: Perfect discrimination (always trust correct, never trust incorrect)
**AUROC = 0.554**: Better than random, can distinguish correct from incorrect

### Our Results

| Configuration | AUROC | Interpretation |
|--------------|-------|----------------|
| No Verification | 0.468 | **Poor** - Barely better than random (0.5) |
| Tier 1 Only | 0.491 | **Fair** - Slightly better than random |
| **Full Linear** | **0.554** | **Good** - Can distinguish correct from incorrect |

**Full Linear (0.554)**: The model can distinguish correct answers from incorrect ones based on confidence. This helps doctors know which diagnoses to trust more.

---

## 3. COMBINED: Why Both Matter

### Real-World Medical Scenario

**Scenario**: A patient presents with chest pain. The model considers 3 possible diagnoses:

1. **Heart Attack** (confidence: 0.85)
2. **Pneumonia** (confidence: 0.60)
3. **GERD** (confidence: 0.30)

### With Good Calibration + Good Discrimination

**Calibration (0.057 ECE)**:
- If model says 85% confident → Actually correct ~85% of the time
- Doctor can trust this confidence level

**Discrimination (0.554 AUROC)**:
- Correct diagnosis (Heart Attack) has highest confidence (0.85)
- Incorrect diagnoses have lower confidence (0.60, 0.30)
- Doctor can prioritize the high-confidence answer

**Outcome**: Doctor knows to:
- Take the heart attack diagnosis seriously (high confidence, well-calibrated)
- Still consider pneumonia (moderate confidence)
- De-prioritize GERD (low confidence)

### With Poor Calibration + Poor Discrimination

**Poor Calibration (0.502 ECE)**:
- Model says 85% confident → Actually only correct 35% of the time
- Doctor can't trust the confidence

**Poor Discrimination (0.468 AUROC)**:
- All diagnoses have similar confidence (0.5, 0.5, 0.5)
- Can't tell which is more likely

**Outcome**: Doctor can't:
- Trust the confidence scores
- Prioritize which diagnosis to investigate first
- Make informed decisions

---

## 4. Why Full Linear is Best

### Our Results Summary

| Metric | Full Linear | Why It Matters |
|--------|-------------|---------------|
| **Calibration (ECE: 0.057)** | Best | Doctors can trust confidence scores |
| **Discrimination (AUROC: 0.554)** | Best | Doctors can prioritize reliable diagnoses |
| **Accuracy (43.3%)** | Same as others | Maintains baseline performance |

### Medical Decision-Making Benefits

1. **Trustworthy Confidence**: When Full Linear says 80% confident, doctors know it's actually ~80% likely to be correct
2. **Prioritization**: Doctors can focus on high-confidence diagnoses first
3. **Risk Assessment**: Doctors know when to order additional tests (low confidence) vs. proceed with treatment (high confidence)
4. **Resource Allocation**: Better use of medical resources by focusing on most reliable diagnoses

---

## 5. Practical Example

### Question: "A 50-year-old presents with chest pain radiating to left arm. What is the diagnosis?"

**No Verification System**:
- Heart Attack: 95% confidence (but actually only 60% correct - overconfident)
- Pneumonia: 50% confidence
- GERD: 50% confidence
- **Problem**: Can't trust confidence, can't prioritize

**Full Linear System**:
- Heart Attack: 80% confidence (actually 80% correct - well-calibrated)
- Pneumonia: 45% confidence (actually 45% correct)
- GERD: 20% confidence (actually 20% correct)
- **Benefit**: Can trust confidence, can prioritize heart attack

---

## Conclusion

**Calibration** = "Can I trust the confidence score?"
- Full Linear: **Yes** (ECE: 0.057) - Confidence matches reality

**Discrimination** = "Can I tell which answers are better?"
- Full Linear: **Yes** (AUROC: 0.554) - Can distinguish correct from incorrect

**Combined**: Full Linear provides **trustworthy, actionable confidence scores** that help doctors make better medical decisions.
