# Parameter Tuning for Tier 1 Verification

## Objective

Find optimal verification parameters that balance **accuracy** and **calibration** (ECE).

## Problem Statement

Current settings show an accuracy-calibration trade-off:
- **No Verification**: 36.7% accuracy, 0.607 ECE (overconfident)
- **Tier 1 Only**: 33.3% accuracy, 0.142 ECE (well-calibrated but lower accuracy)
- **Full Linear**: 40.0% accuracy, 0.168 ECE (best of both)

**Goal**: Optimize Tier 1 parameters to improve accuracy while maintaining good calibration.

## Parameters Being Tuned

### 1. Temperature (T)
**Current**: 0.1  
**Range**: 0.1 - 0.3

**Effect**:
- **Lower (0.1)**: More deterministic, conservative, critical judgments
- **Higher (0.3)**: More diverse, less harsh, allows more variation

**Expected Impact**:
- Higher T → Higher accuracy (less aggressive penalties)
- Higher T → Slightly worse calibration (less conservative)

### 2. NO Penalty Factor
**Current**: 0.1 (90% penalty)  
**Range**: 0.1 - 0.3

**Effect**:
- Applied when verification says "NO" (answer is wrong)
- **0.1**: Very harsh (reduces confidence to ~10% of original)
- **0.3**: Moderate (reduces to ~30% of original)

**Expected Impact**:
- Higher penalty → Lower accuracy (penalizes correct answers too)
- Higher penalty → Better calibration (reduces overconfidence)

### 3. UNCERTAIN Penalty Factor
**Current**: 0.4 (60% penalty)  
**Range**: 0.4 - 0.6

**Effect**:
- Applied when verification says "UNCERTAIN" (not sure)
- **0.4**: Significant penalty
- **0.6**: Moderate penalty

**Expected Impact**:
- Higher penalty → More conservative confidence
- Lower penalty → Maintains more confidence on uncertain cases

### 4. Consistency Weight (α)
**Current**: 0.5 (equal weight)  
**Range**: 0.5 - 0.6

**Effect**:
- Weight for initial diagnosis confidence vs verification confidence
- **0.5**: Equal weight (S = 0.5 × initial + 0.5 × verification)
- **0.6**: Trust initial more (S = 0.6 × initial + 0.4 × verification)

**Expected Impact**:
- Higher weight → Trust specialist's initial judgment more
- Lower weight → Trust verification judgment more

## Configurations Being Tested

| Config | Temp | NO Penalty | UNCERTAIN Penalty | Consistency Wt | Notes |
|--------|------|------------|-------------------|----------------|-------|
| 1 | 0.1 | 0.1 | 0.4 | 0.5 | **Current** (aggressive) |
| 2 | 0.2 | 0.1 | 0.4 | 0.5 | Higher temp only |
| 3 | 0.3 | 0.1 | 0.4 | 0.5 | Even higher temp |
| 4 | 0.1 | 0.3 | 0.6 | 0.5 | Moderate penalties |
| 5 | 0.2 | 0.3 | 0.6 | 0.5 | **Moderate all** |
| 6 | 0.1 | 0.1 | 0.4 | 0.6 | Trust initial more |

## Expected Outcomes

### Best for Accuracy
**Hypothesis**: Config 5 (moderate all)
- Higher temperature allows more flexibility
- Moderate penalties reduce over-penalization
- Should increase accuracy from 33.3% to ~37-39%

### Best for Calibration
**Hypothesis**: Config 1 (current)
- Already achieving 0.142 ECE (excellent)
- Most conservative settings

### Best Overall Balance
**Hypothesis**: Config 5 or Config 4
- Should achieve ~37-38% accuracy
- Maintain ECE < 0.20
- Better trade-off than current settings

## Evaluation Metrics

For each configuration, we measure:

1. **Accuracy**: Percentage of correct predictions
2. **ECE** (Expected Calibration Error): Calibration quality (lower is better)
   - Target: < 0.20 (current Tier 1: 0.142)
   - Baseline: 0.607 (very poor)
3. **AUROC**: Confidence discrimination ability (higher is better)
   - Target: > 0.60
4. **Avg Confidence**: Mean confidence score
   - Should align with accuracy for good calibration

## Decision Criteria

### Primary Goal: Maximize Accuracy-Calibration Score
**Score = Accuracy - (ECE × 0.5)**

This balances both metrics:
- Rewards higher accuracy
- Penalizes poor calibration (but less heavily than accuracy)

### Secondary Goals:
1. **Accuracy ≥ Baseline** (36.7%)
2. **ECE ≤ 0.25** (much better than baseline 0.607)
3. **AUROC ≥ 0.55** (better than random)

## Implementation After Tuning

Once optimal parameters are found:

1. Update `src/verification/tier1_verification.py`:
   ```python
   def __init__(
       self,
       llm_client: Optional[LocalLLMClient] = None,
       temperature: float = 0.X,  # Optimal value
       consistency_weight: float = 0.X
   ):
       # ...
   ```

2. Update penalty factors in `verify_specialist` method:
   ```python
   if verified_status == "NO":
       adjustment_factor = 0.X  # Optimal NO penalty
   elif verified_status == "UNCERTAIN":
       adjustment_factor = 0.X  # Optimal UNCERTAIN penalty
   ```

3. Re-run 4-config comparison with optimized settings

4. Compare results to validate improvement

## Expected Runtime

- **6 configurations** × 30 questions each
- Each question: ~4 specialists + Tier 1 verification
- Estimated: **3-4 hours total**

## Success Criteria

**Improvement Target**:
- Tier 1 accuracy: 33.3% → **37-39%** (+3.7-5.7 percentage points)
- ECE: Maintain < 0.20 (allow slight increase from 0.142)
- Overall: Better than baseline (36.7% accuracy, 0.607 ECE)

**Full System Impact**:
- If Tier 1 improves, Full Linear should also improve
- Expected Full Linear: 40% → **42-44%**
- Better foundation for the hierarchical system

## Post-Tuning Analysis

After results are available:

1. **Identify optimal configuration**
2. **Analyze trade-offs** (accuracy vs calibration)
3. **Validate improvements** (bootstrap confidence intervals)
4. **Update implementation** with optimal parameters
5. **Re-run full 4-config comparison** to validate
6. **Update visualizations** with improved results

## References

- Wu et al. 2024: Two-phase self-verification methodology
- Guo et al. 2017: On Calibration of Modern Neural Networks (ECE metric)
- Your Paper 1: Hierarchical verification framework

## Notes

- Results saved to: `results/paper1/verification_tuning_[timestamp].json`
- All configurations use same 30 questions for fair comparison
- Same LLM (Mistral 7B), same specialists, only verification params change
- This is a grid search over key parameters (not exhaustive)
- Further fine-tuning possible if needed

## Visualization After Tuning

Generate comparison plots:
```bash
# After tuning completes
python scripts/visualize_tuning_results.py results/paper1/verification_tuning_*.json
```

This will show:
- Accuracy vs ECE scatter plot
- Parameter sensitivity analysis
- Recommended optimal settings
