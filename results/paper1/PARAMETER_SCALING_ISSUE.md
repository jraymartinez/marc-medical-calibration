# Parameter Scaling Issue: Optimized Parameters Don't Generalize

## Date
2026-01-13

## The Problem

**Optimized parameters that achieved 46.7% on 30 questions only achieve 30.0% on 100 questions.**

## Evidence

### Accuracy Progression

| Run | Questions | Full Linear Accuracy | Baseline Accuracy |
|-----|-----------|----------------------|------------------|
| **Tuning Run** | 30 | **46.7%** ✅ | 43.3% |
| **Optimized (30-Q)** | 30 | **40.0%** ❌ | 43.3% |
| **Optimized (100-Q)** | 100 | **30.0%** ❌ | 30.0% |

### Key Findings

1. **Parameters Don't Replicate**: Even on same 30 questions, optimized run got 40.0% vs tuning's 46.7%
2. **Accuracy Drops with Scale**: 30-Q: 40.0% → 100-Q: 30.0% (-10%)
3. **Baseline Also Drops**: 30-Q: 43.3% → 100-Q: 30.0% (-13.3%)

---

## Root Causes

### 1. Parameter Overfitting

**Problem**: Parameters optimized for specific 30-question sample don't generalize.

**Evidence**:
- Tuning run: 46.7% (found optimal parameters)
- Optimized 30-Q: 40.0% (same questions, same parameters, worse result!)
- **Even on same questions, parameters don't replicate!**

**Why This Happens**:
- 30 questions is too small for reliable parameter tuning
- Parameters may have worked by chance on specific question mix
- Non-determinism: Different LLM outputs between runs
- High variance with small sample

### 2. Dataset Hardness

**Problem**: 100-question dataset may have harder questions.

**Evidence**:
- Baseline accuracy: 43.3% (30-Q) → 30.0% (100-Q)
- **13.3% drop in baseline accuracy!**
- This suggests questions are fundamentally harder

**Possible Reasons**:
- 100-Q sample includes more difficult questions
- Different question distribution
- More ambiguous cases

### 3. Statistical Variance

**Problem**: 30-question results have high variance.

**Evidence**:
- Tuning run: 46.7% (may have been lucky)
- Optimized 30-Q: 40.0% (more realistic)
- 100-Q: 30.0% (true performance with larger sample)

**Interpretation**:
- 30-Q results may have been optimistic
- 100-Q results are more stable and reliable
- True performance is lower than tuning suggested

### 4. Parameter Sensitivity

**Problem**: Parameters are too sensitive to question characteristics.

**Evidence**:
- Work well on some question types
- Work poorly on others
- Don't generalize across question diversity

---

## Why Parameters Don't Scale

### The Overfitting Problem

**30-Question Tuning**:
- Small sample → High variance
- Parameters may optimize for specific question mix
- Results may not be reproducible

**100-Question Reality**:
- Larger sample → More stable
- True performance emerges
- Parameters don't generalize

### The Baseline Drop

**Critical Finding**: Baseline accuracy dropped 13.3% (43.3% → 30.0%)

**This means**:
- It's not just about parameters
- The 100-Q dataset is fundamentally harder
- Even without verification, performance is lower

**Implication**: 
- Parameters may still be "optimal" for their context
- But the context (dataset difficulty) changed
- Need to re-tune on larger, more representative sample

---

## Solutions

### Option 1: Re-Tune on Larger Sample (Recommended)

**Approach**:
- Tune parameters on 100-question sample
- Use cross-validation or hold-out set
- Find parameters that generalize better

**Pros**: More reliable, generalizable parameters
**Cons**: Time-consuming, may not find better parameters

### Option 2: Accept Current Results

**Approach**:
- Accept that parameters don't scale perfectly
- Focus on calibration and discrimination (which do scale)
- Report both 30-Q and 100-Q results

**Pros**: Honest reporting, shows limitations
**Cons**: Doesn't solve the problem

### Option 3: Use Tier 1 (Best Configuration)

**Approach**:
- Focus on Tier 1 (best overall performance)
- Tier 1 has excellent calibration (ECE: 0.025)
- Simpler, more robust than Full Linear

**Pros**: Tier 1 is actually best configuration
**Cons**: Abandons Full Linear goal

---

## Implications for Paper 1

### The Real Issue

**We can't claim Full Linear is best because**:
1. ❌ Parameters don't replicate (40.0% vs 46.7% on same 30-Q)
2. ❌ Parameters don't scale (30.0% on 100-Q)
3. ❌ Tier 1 is actually better overall

### Revised Research Focus

**Option 1: Focus on Tier 1**
- Tier 1 is best configuration (weighted score: 0.557)
- Excellent calibration (ECE: 0.025)
- More robust, less parameter-dependent

**Option 2: Report Both Results**
- Show 30-Q tuning results (46.7%)
- Show 100-Q validation results (30.0%)
- Discuss parameter scaling limitations
- Emphasize calibration improvements (which do scale)

**Option 3: Re-Tune on Larger Sample**
- Tune parameters on 100-question sample
- Find parameters that work on larger scale
- More reliable but time-consuming

---

## Conclusion

**The optimized parameters don't scale to larger datasets.**

**Key Issues**:
1. Parameter overfitting to 30-question sample
2. Dataset hardness (baseline dropped 13.3%)
3. High variance in small samples
4. Parameters too sensitive to question characteristics

**Recommendation**: 
- Focus on **Tier 1** (best overall configuration)
- OR re-tune on larger sample
- OR report both results honestly

**This is a valid research finding**: Parameter optimization on small samples doesn't always generalize to larger datasets.
