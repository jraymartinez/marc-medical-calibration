# Terminal Results Analysis - Latest Run

## Date
2026-01-12

## Source
Terminal output from latest run (with Tier 1 penalty fix)

## Results Summary

| Configuration | Accuracy | ECE | AUROC | Avg Confidence |
|--------------|----------|-----|-------|----------------|
| Multi (No Verification) | 43.3% | 0.502 | 0.468 | 0.935 |
| Multi + Tier 1 | 43.3% | 0.123 | 0.491 | 0.310 |
| **Multi + Full Linear (Optimized)** | **43.3%** | **0.057** | 0.554 | 0.490 |
| Multi + Bayesian | In progress (stopped at Q10/30) | - | - | - |

## Key Findings

### 1. Full Linear Improvement!
- **Previous Run**: 40.0% accuracy, ECE: 0.190
- **Current Run**: 43.3% accuracy, ECE: 0.057
- **Improvement**: +3.3% accuracy, ECE improved by 70%!

### 2. Comparison with Tuning Run

| Metric | Tuning Run | Current Run | Difference |
|--------|-----------|-------------|------------|
| **Accuracy** | 46.7% | 43.3% | -3.4% |
| **ECE** | 0.035 | 0.057 | +0.022 |
| **AUROC** | 0.569 | 0.554 | -0.015 |

### 3. Progress Analysis

**Positive Signs**:
- ✅ Accuracy improved from 40.0% to 43.3% (+3.3%)
- ✅ ECE dramatically improved from 0.190 to 0.057 (70% better)
- ✅ Much closer to tuning run ECE (0.057 vs 0.035)

**Remaining Gap**:
- ⚠️ Still 3.4% below expected 46.7% accuracy
- ⚠️ ECE slightly worse than tuning (0.057 vs 0.035)

## Possible Reasons for Remaining Gap

1. **Non-determinism**: LLM outputs may vary between runs
2. **Parameter Verification**: Need to double-check all parameters are correct
3. **Question Sampling**: Same seed (42) but need to verify same questions
4. **Model State**: Model may be in different state between runs

## Next Steps

1. ✅ **Tier 1 fix is working** - Clear improvement seen
2. 🔍 **Investigate remaining 3.4% gap** - Check all parameters
3. 📊 **Complete Bayesian run** - See if it still achieves 46.7%
4. 🔄 **Consider re-running** - To verify consistency

## Conclusion

The Tier 1 penalty fix (NO=0.1, UNCERTAIN=0.4) is **working**! Full Linear improved from 40.0% to 43.3% accuracy and ECE improved dramatically. However, there's still a 3.4% gap to the expected 46.7%. This could be due to non-determinism or other factors that need investigation.
