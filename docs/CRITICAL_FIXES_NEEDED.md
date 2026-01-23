# Critical Fixes Needed for Paper 1 Implementation

## Issue 1: Verification Doesn't Affect Answer Selection ⚠️

### Current Problem
All configurations achieve same 36.7% accuracy because verification only changes **confidence**, not **answers**.

### Analysis
- 80% of questions: All configs select SAME answer
- 87% of questions: All configs have SAME correctness
- Verification is working as a **calibration tool**, not a **correction mechanism**

### Why This Happens
```python
# Current implementation (compare_4_configs.py)
# Step 4: Select final answer (majority vote among specialists)
answers = [s['answer'] for s in specialist_outputs]
answer_counts = Counter(answers)
final_answer = answer_counts.most_common(1)[0][0]  # IGNORES confidence!
```

### What Should Happen
Verification scores should **influence** answer selection:

**Option A: Confidence-Weighted Voting**
```python
# Weight each specialist's vote by their verification score
weighted_votes = {}
for spec_out in specialist_outputs:
    answer = spec_out['answer']
    confidence = spec_out['final_confidence']  # Includes verification
    weighted_votes[answer] = weighted_votes.get(answer, 0) + confidence

final_answer = max(weighted_votes, key=weighted_votes.get)
```

**Option B: Threshold-Based Filtering**
```python
# Only consider specialists with confidence above threshold
threshold = 0.5
confident_specialists = [s for s in specialist_outputs 
                         if s['final_confidence'] >= threshold]

if confident_specialists:
    # Vote only among confident specialists
    final_answer = most_common([s['answer'] for s in confident_specialists])
else:
    # Fall back to highest confidence
    final_answer = max(specialist_outputs, 
                       key=lambda s: s['final_confidence'])['answer']
```

**Option C: Re-ranking with Verification**
```python
# For MCQA: Get probabilities for each option, adjust by verification
# Then select option with highest verified probability
```

### Recommended Approach
**Use Option A (Confidence-Weighted Voting)** because:
1. Utilizes verification scores directly
2. Doesn't discard specialist opinions
3. Natural integration with hierarchical confidence
4. Aligns with Paper 1 framework

## Issue 2: Tier 2 Over-Confident on Wrong Answers ⚠️

### Current Problem
- Tier 1 Only: ECE = 0.122 (best calibration)
- Full Linear: ECE = 0.172 (worse with Tier 2!)
- Tier 2 sometimes **validates wrong answers**, boosting confidence

### Why This Happens
1. Tier 2 temperature (0.05) might be too low → overconfident
2. GP validation prompt may not be critical enough
3. Linear integration (α=0.5) gives equal weight to Tier 1 and Tier 2

### Solutions

**Short-term: Tune Tier 2 Temperature**
```python
# src/verification/tier2_validation.py
temperature: float = 0.2  # Currently 0.05, try 0.1-0.2
```

**Medium-term: Adjust Integration Weights**
```python
# Give more weight to Tier 1 (specialist self-verification)
# Linear: C = 0.7*S + 0.3*G  # Trust specialist more than GP
```

**Long-term: Train GP to Be More Skeptical**
```python
# Add more critical examples to GP prompt
# Penalize GP more heavily for over-confidence on wrong answers
```

## Issue 3: Small Sample Size Limits Conclusions

### Problem
- Only 30 questions tested
- 36.7% = 11/30 correct
- Limited statistical power
- High variance between runs

### Solution
**Scale to full dataset (1,200+ questions)** before final conclusions

## Recommended Action Plan

### Phase 1: Fix Answer Selection (CRITICAL - Do First!)
1. Implement confidence-weighted voting in `compare_4_configs.py`
2. Re-run 4-config experiment (30 questions)
3. Verify that configurations now differ in accuracy

**Expected Results:**
- No Verification: ~36-37% (baseline)
- Tier 1 Only: ~38-40% (conservative but correct)
- Full Linear: ~40-42% (best balance)
- Bayesian: ~37-39% (very conservative)

### Phase 2: Tune Tier 2 Parameters
1. Run Tier 2 temperature tuning (similar to Tier 1)
2. Test temperatures: 0.05, 0.1, 0.15, 0.2
3. Find optimal that doesn't over-validate

### Phase 3: Optimize Integration Weights
1. Test different α values for Linear: 0.4, 0.5, 0.6, 0.7
2. Find optimal balance between Tier 1 and Tier 2
3. May find that Tier 1 should have higher weight

### Phase 4: Scale to Full Dataset
1. Run optimized system on 1,200+ questions
2. Compute confidence intervals
3. Perform statistical significance tests
4. Generate final publication figures

## Expected Outcomes After Fixes

### Before Fixes (Current)
| Config | Accuracy | ECE | Note |
|--------|----------|-----|------|
| No Verification | 36.7% | 0.608 | High confidence, poor calibration |
| Tier 1 Only | 36.7% | 0.122 | Good calibration, no answer change |
| Full Linear | 36.7% | 0.172 | Tier 2 hurts calibration |

### After Fixes (Expected)
| Config | Accuracy | ECE | Note |
|--------|----------|-----|------|
| No Verification | 36.7% | 0.608 | Baseline |
| Tier 1 Only | ~39% | ~0.13 | Verification improves answers |
| Full Linear | ~42% | ~0.14 | Hierarchical improvement |
| Bayesian | ~40% | ~0.15 | Conservative but effective |

## Impact on Paper 1

### Current State
- ⚠️ Results show calibration improvement but **no accuracy gain**
- ⚠️ Hierarchical system doesn't outperform simple verification
- ⚠️ Limited evidence for "verification corrects errors"

### After Fixes
- ✅ Clear accuracy improvement from verification
- ✅ Hierarchical system shows compounding benefits
- ✅ Strong evidence that verification both calibrates AND corrects
- ✅ Publishable results with clear contributions

## Timeline Estimate

- **Phase 1 (Fix answer selection)**: 4-5 hours (1 hour code + 3-4 hours re-run)
- **Phase 2 (Tune Tier 2)**: 3-4 hours
- **Phase 3 (Optimize weights)**: 2-3 hours  
- **Phase 4 (Scale to full dataset)**: 8-12 hours

**Total**: ~20-24 hours of computation time

## Conclusion

The current implementation is **fundamentally limited** because verification doesn't affect answer selection. This is a **design issue**, not a parameter issue.

**Priority**: Fix answer selection logic FIRST, then tune remaining parameters.

The good news: The verification system IS working (it's improving calibration). We just need to **use those confidence scores to select better answers**.
