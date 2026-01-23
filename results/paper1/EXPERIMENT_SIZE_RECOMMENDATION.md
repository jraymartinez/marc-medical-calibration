# Experiment Size Recommendation

## Date: 2026-01-17

## Current Plan: **100 Questions**

### Why 100 Questions?

1. **Dataset Size**: The curated dataset (`medqa_us_100q_high_disagreement.json`) contains exactly 100 questions
   - 80 questions with specialist disagreement (80%)
   - 20 questions with specialist agreement (20%)
   - Perfect for showcasing verification benefits

2. **Statistical Power**: 
   - 100 questions provides reasonable statistical power for comparing 4 configurations
   - Can detect meaningful differences in accuracy, ECE, and AUROC
   - Standard sample size for medical Q&A evaluation

3. **Runtime Considerations**:
   - 4 configurations × 100 questions = 400 total runs
   - Each run: ~1-2 minutes (specialist diagnosis + verification)
   - **Estimated total time**: ~6-8 hours
   - Reasonable for a full experiment

4. **Paper Standards**:
   - 100 questions is a standard evaluation size for medical Q&A papers
   - Sufficient for statistical significance testing
   - Good balance between thoroughness and feasibility

## Alternative Options

### Option 1: Full Dataset (100 questions) ✅ **RECOMMENDED**
- **Size**: 100 questions
- **Runtime**: ~6-8 hours
- **Pros**: Complete evaluation, uses full curated dataset
- **Cons**: Longer runtime

### Option 2: Reduced Size (50 questions)
- **Size**: 50 questions
- **Runtime**: ~3-4 hours
- **Pros**: Faster, still reasonable sample size
- **Cons**: Less statistical power, might miss some patterns

### Option 3: Quick Test (10 questions)
- **Size**: 10 questions
- **Runtime**: ~30-60 minutes
- **Pros**: Very fast, good for debugging
- **Cons**: Not sufficient for final results, low statistical power

## Recommendation: **100 Questions**

### Rationale:
1. **Uses full curated dataset**: 100 questions specifically curated for this experiment
2. **Statistical power**: Sufficient for meaningful comparisons
3. **Paper-ready**: Standard size for medical Q&A evaluation
4. **Reasonable runtime**: 6-8 hours is acceptable for a full experiment

### Expected Runtime Breakdown:

| Configuration | Questions | Est. Time per Question | Total Time |
|--------------|-----------|----------------------|------------|
| Single Specialist | 100 | ~30 seconds | ~50 minutes |
| Single Specialist + Tier 1 | 100 | ~1.5 minutes | ~2.5 hours |
| Multi-Agent (No Verification) | 100 | ~1 minute | ~1.7 hours |
| Multi-Agent + Tier 1 | 100 | ~2 minutes | ~3.3 hours |
| **TOTAL** | **400 runs** | | **~8 hours** |

*Note: Times are estimates. Actual runtime depends on GPU speed and model loading.*

## If You Want to Adjust:

The script can easily be modified:

```python
# In scripts/run_final_comparison.py, line 257:
num_questions = 100  # Change to 50, 30, or 10 for smaller experiments
```

## Final Recommendation

**Use 100 questions** for the final comparison experiment:
- Complete evaluation of curated dataset
- Sufficient statistical power
- Standard for paper submission
- Reasonable runtime (~8 hours)
