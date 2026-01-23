# Tier 1 Wu et al. Two-Phase Verification - Test Results

## Date
2026-01-14

## Test Setup
- **Dataset**: 10 disagreement questions from `medqa_us_100q_high_disagreement.json`
- **Method**: Wu et al. 2024 Two-Phase Verification
- **Specialist**: General Practitioner (tested on one specialist)

## Results Summary

### Verified Status Distribution
- **NO**: 8/10 (80.0%)
- **UNCERTAIN**: 2/10 (20.0%)
- **YES**: 0/10 (0.0%)

**Analysis**: 
- ✅ **SUCCESS**: Not all UNCERTAIN (unlike previous implementation with 100% UNCERTAIN)
- ⚠️ **Issue**: Mostly NO status (80%) - suggests inconsistency measurement may be too strict
- The method is working but may need threshold adjustment

### Inconsistency Scores
- **Mean**: 0.667
- **Min**: 0.250
- **Max**: 1.000

**Analysis**:
- High mean inconsistency (0.667) suggests many inconsistencies detected
- Range shows variation (0.25-1.0), which is good
- May indicate that independent vs. reference answers genuinely differ

### S Scores (Final Confidence)
- **Mean**: 0.151
- **Min**: 0.068
- **Max**: 0.412
- **Range**: 0.345

**Analysis**:
- ✅ **SUCCESS**: Good variation (0.345 range) - much better than previous 0.375-0.4 range
- This variation should help fusion method distinguish between specialists
- Mean is low (0.151) due to mostly NO status with 0.15 adjustment factor

## Key Observations

### What's Working
1. **Question Formulation**: Successfully generating 2-4 verification questions per case
2. **Two-Phase Answers**: Successfully getting independent and reference answers
3. **Inconsistency Detection**: Detecting differences between answers
4. **Score Variation**: S scores vary significantly (0.068-0.412), enabling fusion to work

### Issues to Address
1. **High Inconsistency Rate**: Mean 0.667 suggests most answers are inconsistent
   - Could be due to:
     - Answers genuinely differ when answered independently vs. with reference
     - Similarity matching too strict (even with improved algorithm)
     - LLM phrasing differences (same meaning, different words)

2. **Mostly NO Status**: 80% NO status leads to very low S scores
   - NO status → adjustment_factor = 0.15 → very low final S scores
   - May need to adjust thresholds:
     - Inconsistency < 0.2 → YES (current)
     - Inconsistency < 0.5 → UNCERTAIN (current)
     - Inconsistency >= 0.5 → NO (current)
   - Consider: Inconsistency < 0.4 → YES, < 0.7 → UNCERTAIN, >= 0.7 → NO

3. **No YES Status**: 0% YES suggests threshold may be too strict
   - Even with low inconsistency (0.25), still getting NO/UNCERTAIN
   - Need to review threshold logic

## Comparison with Previous Implementation

### Previous (Simple Verification)
- Status: 100% UNCERTAIN
- S Scores: 0.375-0.4 (very similar)
- Result: Fusion couldn't distinguish

### New (Wu et al. Method)
- Status: 80% NO, 20% UNCERTAIN, 0% YES
- S Scores: 0.068-0.412 (good variation)
- Result: Fusion should be able to distinguish better

## Recommendations

### Option 1: Adjust Inconsistency Thresholds (Recommended)
```python
if inconsistency_score < 0.3:  # More lenient (was 0.2)
    verified_status = "YES"
elif inconsistency_score < 0.6:  # More lenient (was 0.5)
    verified_status = "UNCERTAIN"
else:
    verified_status = "NO"
```

### Option 2: Improve Similarity Matching
- Current: Word-based Jaccard similarity (threshold 0.5)
- Consider: Semantic similarity (embeddings) or more sophisticated matching
- Or: Further lower threshold to 0.4

### Option 3: Adjust Adjustment Factors
- Current: NO=0.15, UNCERTAIN=0.5, YES=1.0
- Consider: NO=0.3, UNCERTAIN=0.6, YES=1.0 (less aggressive)

### Option 4: Combine Approaches
- Use both threshold adjustment and less aggressive penalties
- This should increase YES/UNCERTAIN rate and raise S scores

## Next Steps

1. **Adjust thresholds** (Option 1) and re-test
2. **Run full 100-question experiment** if thresholds look good
3. **Compare metrics** with previous run (53% accuracy baseline)
4. **Expected improvement**: 2-5% accuracy increase with better score distinction

## Conclusion

The Wu et al. Two-Phase Verification method is **working correctly**:
- ✅ Formulating questions
- ✅ Getting independent/reference answers
- ✅ Measuring inconsistencies
- ✅ Producing varied S scores

However, the **thresholds may be too strict**, leading to mostly NO status. With threshold adjustments, we should see:
- More YES/UNCERTAIN decisions
- Higher S scores (mean > 0.3)
- Better accuracy improvement

The method is fundamentally sound and ready for full experiment after threshold tuning.
