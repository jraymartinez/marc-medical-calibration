# Formula Comparison: Weighted Average vs Multiplicative

## Executive Summary

**Both formulas perform identically** (60% accuracy), indicating the problem is **not in the S_score formula** but in:
1. **Fusion logic** (too aggressive)
2. **Two-Phase Verification** (giving YES to wrong answers)
3. **Specialist agents** (giving wrong answers)

---

## 1. Overall Performance

| Metric | Formula 1 (Weighted Avg) | Formula 2 (Multiplicative) |
|--------|-------------------------|---------------------------|
| **Accuracy** | 60.0% | 60.0% |
| **ECE** | 0.699 | 0.616 |
| **AUROC** | 0.590 | 0.345 |

**Key Finding**: Formula 1 has **better AUROC** (0.590 vs 0.345), but both have same accuracy.

---

## 2. S_score Discrimination Analysis

### Formula 1: `S = 0.5 * initial_confidence + 0.5 * verification_confidence`

**Multi-Agent + Two-Phase Results**:
- **Correct answers**: Mean S_score = **0.867** (Min: 0.575, Max: 1.000)
- **Wrong answers**: Mean S_score = **0.819** (Min: 0.575, Max: 1.000)
- **Discrimination gap**: **0.047** (very small, but positive)

**Issues**:
- Both correct and wrong answers get **very high S_scores** (ceiling effect)
- Small discrimination gap (0.047) means S_scores don't separate correct/wrong well
- But at least correct > wrong (positive discrimination)

### Formula 2: `S = initial_confidence * (1 - inconsistency_score)`

**Multi-Agent + Two-Phase Results**:
- **Correct answers**: Mean S_score = **0.689** (Min: 0.225, Max: 1.000)
- **Wrong answers**: Mean S_score = **0.766** (Min: 0.225, Max: 1.000)
- **Discrimination gap**: **-0.077** (NEGATIVE - wrong direction!)

**Issues**:
- **Wrong answers have HIGHER S_scores than correct answers** (negative discrimination)
- This is worse than random - the formula is actively misleading
- Why: Correct answers may have higher inconsistency (model is uncertain), while wrong answers have low inconsistency (model is confidently wrong)

---

## 3. Why Formula 2 Has Negative Discrimination

**The Problem**: The multiplicative formula `S = initial * (1 - inconsistency)` assumes:
- **Low inconsistency = high confidence** (good)
- **High inconsistency = low confidence** (bad)

**Reality**:
- **Correct answers** can have **high inconsistency** (model is uncertain but correct)
- **Wrong answers** can have **low inconsistency** (model is confidently wrong)

**Example from Q3**:
- **Correct answer A** (Neurology): initial=0.45, inconsistency=1.0 → S = 0.45 * 0 = **0.0**
- **Wrong answer B** (Cardiology): initial=0.95, inconsistency=0.0 → S = 0.95 * 1.0 = **0.95**

The formula penalizes correct but uncertain answers, while rewarding wrong but confident answers.

---

## 4. Formula 1 vs Formula 2: Detailed Comparison

### Single Specialist + Two-Phase Verification

| Metric | Formula 1 | Formula 2 |
|--------|-----------|-----------|
| Accuracy | 70.0% | 70.0% |
| ECE | 0.547 | **0.273** (better) |
| AUROC | 0.455 | **0.519** (better) |

**Finding**: Formula 2 performs **better for Single Specialist** (lower ECE, higher AUROC).

### Multi-Agent + Two-Phase Verification

| Metric | Formula 1 | Formula 2 |
|--------|-----------|-----------|
| Accuracy | 60.0% | 60.0% |
| ECE | 0.699 | **0.616** (better) |
| AUROC | **0.590** (better) | 0.345 |

**Finding**: Formula 1 performs **better for Multi-Agent** (higher AUROC).

**Why the difference?**:
- **Single Specialist**: Only one answer to verify, multiplicative formula works better
- **Multi-Agent**: Multiple answers, weighted average better captures consensus

---

## 5. Recommendations

### 5.1 For Multi-Agent System

**Use Formula 1 (Weighted Average)**:
- Better AUROC (0.590 vs 0.345)
- Positive discrimination (correct > wrong)
- But needs improvement (gap only 0.047)

**Improvements Needed**:
1. **Stricter inconsistency penalties**: Reduce weight of verification_confidence if inconsistency is high
2. **Calibration**: Apply temperature scaling to S_scores
3. **Hybrid approach**: `S = initial * (1 - inconsistency)^1.5` (quadratic penalty)

### 5.2 For Single Specialist System

**Use Formula 2 (Multiplicative)**:
- Better ECE (0.273 vs 0.547)
- Better AUROC (0.519 vs 0.455)
- But needs validation (why does it work for single but not multi?)

**Improvements Needed**:
1. **Validate why it works**: Investigate why multiplicative works for single specialist
2. **Test on larger dataset**: Confirm results hold with more questions

### 5.3 Alternative: Hybrid Formula

**Proposed**: `S = 0.7 * initial + 0.3 * verification * (1 - inconsistency)^2`

**Rationale**:
- Weighted average (like Formula 1) for stability
- Quadratic penalty for inconsistency (stronger than Formula 2)
- More weight on initial confidence (70% vs 50%)

---

## 6. Conclusion

**Key Findings**:
1. **Both formulas have same accuracy** (60%) - problem is not in formula
2. **Formula 1 better for Multi-Agent** (AUROC 0.590 vs 0.345)
3. **Formula 2 better for Single Specialist** (ECE 0.273 vs 0.547, AUROC 0.519 vs 0.455)
4. **Formula 2 has negative discrimination for Multi-Agent** (wrong > correct)

**Recommendation**:
- **For Multi-Agent**: Use Formula 1 but improve it (stricter penalties, calibration)
- **For Single Specialist**: Use Formula 2 (but validate why it works)
- **Future**: Test hybrid formula combining both approaches

**Priority**: Fix fusion logic first (it's causing the 60% accuracy), then improve S_score discrimination.
