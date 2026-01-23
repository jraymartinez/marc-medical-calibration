# Critical Finding: Fusion Method Difference

## Problem Identified

**Tuning script** (`tune_full_linear.py`) achieved **46.7% accuracy** with Full Linear (α=0.6), but **optimized script** (`run_optimized_multi_specialist.py`) achieved only **43.3% accuracy**.

**Root Cause**: Different fusion methods!

---

## Fusion Method Comparison

### Tuning Script (46.7% accuracy) ✅
```python
# Sort specialists by confidence (highest first)
specialist_opinions.sort(key=lambda x: x['confidence'], reverse=True)

# Select answer from specialist with highest confidence
final_answer = specialist_opinions[0]['answer']
final_confidence = specialist_opinions[0]['confidence']
```

**Method**: **Highest Confidence Selection**
- Picks the answer from the specialist with the **highest individual confidence**
- If Respiratory specialist has confidence 0.5 and others have 0.3, Respiratory's answer wins

---

### Optimized Script (43.3% accuracy) ❌
```python
# Sum confidences per answer (weighted voting)
weighted_votes = defaultdict(float)
for spec_out in specialist_outputs:
    answer = spec_out['answer']
    confidence = spec_out['confidence']
    weighted_votes[answer] += confidence

# Select answer with highest sum
final_answer = max(weighted_votes, key=weighted_votes.get)
```

**Method**: **Weighted Voting (Sum of Confidences)**
- Sums confidences for each answer across all specialists
- If Answer A gets 0.3+0.3+0.3=0.9 and Answer B gets 0.5, Answer A wins (even if Answer B has higher individual confidence)

---

## Why This Matters

**Highest Confidence Selection**:
- Allows a single high-confidence specialist to override others
- Better when one specialist is clearly more confident and correct
- Achieved **46.7% accuracy** in tuning

**Weighted Voting**:
- Requires multiple specialists to agree (sum of confidences)
- Better when multiple specialists agree on the same answer
- Achieved **43.3% accuracy** in optimized run

---

## Fix Applied

Updated `run_optimized_multi_specialist.py` to use **highest confidence selection** (matching tuning script).

This should restore the **46.7% accuracy** from the tuning run.

---

## Next Steps

1. ✅ **Fixed fusion method** in optimized script
2. ⏳ **Re-run experiment** with corrected fusion method
3. ⏳ **Verify accuracy** matches tuning results (46.7%)
4. ⏳ **Generate updated tables and visualizations**
