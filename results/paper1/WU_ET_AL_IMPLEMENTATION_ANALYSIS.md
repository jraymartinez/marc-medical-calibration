# Wu et al. Implementation Analysis: Why Performance is Worst

## Results Summary

**Multi-Agent + Two-Phase Verification (Pure Wu et al. method)**:
- Accuracy: **56.7%** (WORST - down from 66.7% and 53.3%)
- ECE: **0.760** (very high, worse than baseline 0.759)
- AUROC: **0.561** (slightly better, but still poor)

## Key Findings from Analysis

### 1. **Wrong Answers Have Perfect Consistency**
- Q2: Wrong answer with **inconsistency=0.000** (perfect consistency) → **confidence=0.950**
- Q4: Wrong answer with **inconsistency=0.250** → **confidence=0.847**
- **Problem**: Wrong answers can be internally consistent but still wrong!

### 2. **Inconsistency Score Distribution**
- Mean inconsistency: **0.538**
- <0.3 (YES): **47** cases
- 0.3-0.6 (UNCERTAIN): **38** cases  
- >=0.6 (NO): **65** cases
- **Problem**: Many wrong answers have low inconsistency (perfectly consistent but wrong)

### 3. **Confidence Gap is Small**
- Correct answers: mean conf = **0.848**
- Wrong answers: mean conf = **0.799**
- Gap: **0.048** (essentially no discrimination!)

### 4. **S_score Distribution**
- Mean S_score: **0.533**
- Range: 0.234 - 1.000
- **Problem**: Wrong answers getting high S_scores (up to 1.000)

## Root Cause: Fundamental Limitation of Wu et al.'s Method

**Wu et al.'s method only checks CONSISTENCY, not CORRECTNESS.**

From the paper:
> "The inconsistencies between the two sets of answers serve as a measure of uncertainty in the answer."

**The problem**: A wrong answer can be:
- **Internally consistent** (no contradictions in reasoning)
- **But still medically wrong** (doesn't match the correct answer)

**Example from our results**:
- Q2: Wrong answer "C" has inconsistency=0.000 (perfectly consistent)
- But it's the wrong answer!
- Wu et al.'s method gives it high confidence (0.950) because it's consistent

## Issues with Our Implementation

### 1. **Adjustment Factor Too Lenient**
```python
if verified_status == "YES":
    adjustment_factor = 1.0  # No penalty for consistent wrong answers!
```
**Problem**: Wrong answers that are internally consistent get no penalty.

### 2. **Inconsistency Thresholds Too Lenient**
```python
if inconsistency_score < 0.3:  # Very low inconsistency
    verified_status = "YES"
```
**Problem**: 0.3 threshold is too low. Many wrong answers pass this.

### 3. **Combination Formula**
```python
S_score = (
    self.consistency_weight * initial_confidence +
    (1 - self.consistency_weight) * verification_confidence
) * adjustment_factor
```
**Problem**: `consistency_weight = 0.65` means we're giving 65% weight to initial confidence, which might be wrong for wrong answers.

### 4. **No Penalty for Wrong but Consistent Answers**
Wu et al.'s method doesn't distinguish between:
- Consistent + Correct → Should have high confidence ✓
- Consistent + Wrong → Should have low confidence ✗

But our implementation treats both the same!

## What Wu et al. Actually Do

From the paper:
1. Generate explanation + answer
2. Formulate verification questions
3. Answer independently (without reference)
4. Answer again with reference to explanation
5. **Measure inconsistencies** → uncertainty score
6. **Use inconsistency as uncertainty measure** (not correctness!)

**Key insight**: Wu et al. acknowledge this limitation:
> "However, this method falls short as the retrieved results frequently have low relevance scores to the verification queries and fail to provide the necessary knowledge."

They suggest using external knowledge bases, but we're not doing that.

## Recommendations

### Option 1: **Hybrid Approach** (Recommended)
- Use Wu et al.'s inconsistency score
- **But also check correctness** (what we removed!)
- Combine: `uncertainty = inconsistency_weight * inconsistency + correctness_weight * (1 - correctness)`

### Option 2: **Stricter Inconsistency Thresholds**
- Make YES threshold stricter: `inconsistency_score < 0.15` (was 0.3)
- Make adjustment factors more aggressive: YES=0.9 (was 1.0), UNCERTAIN=0.6 (was 0.7)

### Option 3: **Different Combination Formula**
- Don't use weighted average
- Use: `S_score = initial_confidence * (1 - inconsistency_score)` (multiplicative, not additive)

### Option 4: **Accept the Limitation**
- Wu et al.'s method is designed for uncertainty estimation, not correctness checking
- It works when answers are inconsistent (detects hallucinations)
- But fails when wrong answers are internally consistent

## Conclusion

**The fundamental issue**: Wu et al.'s method is designed to detect **inconsistencies/hallucinations**, not **correctness**. Wrong answers can be perfectly consistent, leading to high confidence scores.

**Our implementation is correct** according to Wu et al., but the method itself has this limitation for medical QA where correctness matters more than consistency.

**Best solution**: Go back to hybrid approach (consistency + correctness), but fix the correctness checker to be less conservative.
