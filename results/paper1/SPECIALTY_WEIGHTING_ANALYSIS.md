# Analysis: Specialty Weighting vs Confidence-Weighted Voting

## Your Questions:

1. **Should we give more weight to respiratory specialist?**
2. **Are we expecting better accuracy and lower ECE in Full Linear?**
3. **Is this a small sample size issue (30 questions)?**

---

## Question 1: Specialty-Based Weighting

### Current Implementation (Confidence-Weighted Voting):

```python
# All specialists weighted equally by confidence
weighted_votes = defaultdict(float)
for spec_out in specialist_outputs:
    answer = spec_out['answer']
    confidence = spec_out['final_confidence']
    weighted_votes[answer] += confidence  # Equal weight per specialist
```

**Problem**: For respiratory questions:
- **Respiratory specialist**: Relevant expertise ✅
- **Cardiology specialist**: Less relevant ⚠️
- **Neurology specialist**: Less relevant ⚠️
- **Gastroenterology specialist**: Less relevant ⚠️

**All get equal weight in voting!**

### Proposed: Specialty-Based Weighting

```python
# Weight by specialty relevance
specialty_weights = {
    'respiratory': 2.0,      # 2x weight (relevant)
    'cardiology': 0.5,        # 0.5x weight (less relevant)
    'neurology': 0.5,         # 0.5x weight (less relevant)
    'gastroenterology': 0.5   # 0.5x weight (less relevant)
}

weighted_votes = defaultdict(float)
for spec_out in specialist_outputs:
    answer = spec_out['answer']
    confidence = spec_out['final_confidence']
    specialty = spec_out['specialty']
    weight = specialty_weights.get(specialty, 1.0)
    weighted_votes[answer] += confidence * weight  # Weighted by specialty!
```

### Expected Impact:

**Current (Equal Weight)**:
```
Respiratory: Answer B, conf=0.8 → vote = 0.8
Cardiology: Answer A, conf=0.9 → vote = 0.9
Neurology: Answer A, conf=0.7 → vote = 0.7
Gastroenterology: Answer A, conf=0.8 → vote = 0.8
Total: B=0.8, A=2.4 → Winner: A (wrong!)
```

**With Specialty Weighting**:
```
Respiratory: Answer B, conf=0.8 → vote = 0.8 * 2.0 = 1.6
Cardiology: Answer A, conf=0.9 → vote = 0.9 * 0.5 = 0.45
Neurology: Answer A, conf=0.7 → vote = 0.7 * 0.5 = 0.35
Gastroenterology: Answer A, conf=0.8 → vote = 0.8 * 0.5 = 0.4
Total: B=1.6, A=1.2 → Winner: B (correct!)
```

**This could significantly improve multi-specialist accuracy!**

---

## Question 2: Expected Results for Full Linear

### What We SHOULD Expect:

**If Tier 2 is working correctly:**
- ✅ Better accuracy than Tier 1 alone (GP catches errors Tier 1 misses)
- ✅ Better calibration (lower ECE)
- ✅ Better uncertainty discrimination (higher AUROC)

### What We're Actually Seeing:

**Single-Specialist:**
- Tier 1: 46.7% accuracy, ECE=0.161
- Full Linear: 43.3% accuracy, ECE=0.156
- **Accuracy: -3.4% ❌, ECE: -3.1% ✅ (minimal)**

**Multi-Specialist:**
- Tier 1: 46.7% accuracy, ECE=0.163
- Full Linear: 43.3% accuracy, ECE=0.164
- **Accuracy: -3.4% ❌, ECE: +0.6% ❌ (worse!)**

### Why This Might Be Happening:

1. **GP validation is too conservative**
   - Rejecting correct answers
   - Lowering confidence on correct diagnoses

2. **Integration method (α=0.5) not optimal**
   - Linear combination might not be best
   - Equal weight to S and G might be wrong

3. **Tier 2 temperature (0.15) might be too low**
   - Too deterministic
   - Can't make nuanced judgments

4. **GP prompts might need improvement**
   - Not giving GP enough context
   - GP making poor validation decisions

---

## Question 3: Small Sample Size Issue?

### Statistical Power Analysis:

**30 questions is indeed small!**

For medical QA with ~45% accuracy:
- **30 questions**: High variance, low statistical power
- **100 questions**: Better, but still moderate
- **300+ questions**: Good statistical power

### Variance in Results:

With 30 questions:
- **±1 question** = ±3.3% accuracy change
- **±2 questions** = ±6.7% accuracy change

**The -3.4% difference could be:**
- Real effect (Tier 2 hurts)
- Statistical noise (small sample)
- Combination of both

### Expected with Larger Sample:

**If we run 100 questions:**

**Scenario A: Pattern Holds (Real Effect)**
- Tier 1: ~46-47% accuracy
- Full Linear: ~43-44% accuracy
- Consistent -3% difference
- **Conclusion**: Tier 2 genuinely hurts accuracy

**Scenario B: Pattern Reverses (Statistical Noise)**
- Tier 1: ~46-47% accuracy
- Full Linear: ~47-48% accuracy
- Tier 2 actually helps!
- **Conclusion**: 30 questions was too small

**Scenario C: No Difference (Null Effect)**
- Tier 1: ~46-47% accuracy
- Full Linear: ~46-47% accuracy
- No significant difference
- **Conclusion**: Tier 2 doesn't affect accuracy

---

## Recommendations

### 1. Implement Specialty-Based Weighting

**Why**: Makes sense for domain-specific questions
- Respiratory questions → Respiratory specialist gets more weight
- Should improve multi-specialist accuracy
- More realistic (real doctors weight by expertise)

**Implementation**: See code changes below

### 2. Run with Larger Sample (100+ questions)

**Why**: 30 questions is too small for reliable conclusions
- Statistical significance
- Reduce variance
- More reliable patterns

**Timeline**: ~3-4 hours for 100 questions × 7 configs

### 3. Investigate Tier 2 Quality

**Why**: GP validation might be making poor judgments
- Check GP validation decisions
- Analyze what GP is rejecting/approving
- Tune GP prompts or parameters

---

## Expected Impact of Specialty Weighting

### Current Multi-Specialist Results:
- No Verification: 43.3%
- Tier 1: 46.7%
- Full Linear: 43.3%

### With Specialty Weighting (Estimated):
- No Verification: 46-48% (respiratory specialist weighted more)
- Tier 1: 48-50% (better consensus)
- Full Linear: 46-48% (might still have Tier 2 issues)

**Potential improvement: +3-5% accuracy for multi-specialist!**

---

## Action Plan

### Option 1: Implement Specialty Weighting First
1. Add specialty-based weights
2. Re-run 7 configs with 30 questions (quick test)
3. If promising, run 100 questions

### Option 2: Run 100 Questions First
1. Keep current implementation
2. Run 100 questions to check if pattern holds
3. Then implement specialty weighting

### Option 3: Both (Recommended)
1. Implement specialty weighting
2. Run 100 questions with weighted voting
3. Compare to current results

---

## Summary

### Your Questions Answered:

1. **Specialty weighting**: ✅ YES, should help! Respiratory specialist should have more weight
2. **Expected Full Linear**: ✅ YES, should be better, but we're seeing worse (needs investigation)
3. **Sample size**: ✅ YES, 30 is small! 100+ would be more reliable

### Next Steps:
1. ✅ Implement specialty-based weighting
2. ⏳ Run with 100 questions for statistical power
3. ⏳ Investigate why Tier 2 hurts accuracy
