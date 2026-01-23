# ECE Analysis and Improvement Plan

## Date
2026-01-13

## Current ECE Performance

### Multi + Full Linear (Optimized)
- **ECE: 0.564** (Target: <0.1 for good calibration)
- **Accuracy: 32.0%**
- **Avg Confidence: 0.884**

### Critical Issue: Severe Overconfidence

**65 predictions with confidence = 1.0, but only 32.3% accuracy!**

- High confidence bin (0.9-1.0): 65 predictions
  - Confidence: 1.000
  - Accuracy: 32.3%
  - **Calibration Error: 0.677** (huge!)

- This bin contributes **0.440** to total ECE (78% of total error!)

## Root Causes

1. **Confidence Saturation**: Many predictions hit max confidence (1.0)
2. **Verification Not Penalizing Enough**: Wrong answers still get high confidence
3. **No Calibration**: Direct confidence scores without calibration
4. **Binary Confidence**: Many confidences are exactly 1.0 (no granularity)

## Proposed Solutions

### 1. Temperature Scaling (Easiest - Start Here)

**Implementation**: Apply temperature scaling to final confidence
```python
def temperature_scale(confidence, temperature=1.5):
    """Scale confidence to reduce overconfidence."""
    # Higher temperature -> lower confidence
    return confidence ** (1.0 / temperature)
```

**Expected Impact**: 
- Reduce confidence=1.0 to ~0.87 (with T=1.5)
- Better match confidence with accuracy
- ECE reduction: ~0.2-0.3

### 2. Increase Verification Penalties for Wrong Answers

**Current Penalties**:
- Tier 1: NO=0.2, UNCERTAIN=0.6
- Tier 2: REJECTED=0.6, NEEDS_REVIEW=0.85

**Proposed**:
- Tier 1: NO=0.15 (more aggressive), UNCERTAIN=0.5 (more aggressive)
- Tier 2: REJECTED=0.4 (more aggressive), NEEDS_REVIEW=0.7 (more aggressive)

**Rationale**: Wrong answers should have lower confidence

### 3. Add Confidence Calibration Layer

**Platt Scaling** (Logistic Regression):
```python
from sklearn.linear_model import LogisticRegression

# Train on validation set
calibrator = LogisticRegression()
calibrator.fit(confidences.reshape(-1, 1), is_correct)

# Apply to predictions
calibrated_confidence = calibrator.predict_proba(confidences.reshape(-1, 1))[:, 1]
```

**Histogram Binning**:
- Map raw confidence to calibrated bins
- Each bin's confidence = accuracy in that bin

### 4. Prevent Confidence Saturation

**Current**: Many confidences = 1.0
**Solution**: Cap maximum confidence at 0.95
```python
final_confidence = min(final_confidence, 0.95)
```

### 5. Improve Tier 1 Verification Granularity

**Current**: Binary YES/NO/UNCERTAIN
**Proposed**: Add confidence levels
- HIGH_CONFIDENCE: No penalty (confidence * 1.0)
- MEDIUM_CONFIDENCE: Small penalty (confidence * 0.9)
- LOW_CONFIDENCE: Medium penalty (confidence * 0.7)
- UNCERTAIN: Large penalty (confidence * 0.5)
- NO: Maximum penalty (confidence * 0.2)

### 6. Add Post-Processing Calibration

**After all verification**, apply calibration:
```python
# Option 1: Temperature scaling
calibrated = confidence ** (1.0 / 1.5)

# Option 2: Linear scaling
calibrated = 0.3 + 0.5 * confidence  # Map [0,1] to [0.3, 0.8]

# Option 3: Sigmoid scaling
calibrated = 1 / (1 + exp(-5 * (confidence - 0.5)))
```

## Implementation Priority

### Phase 1: Quick Wins (Immediate)
1. ✅ **Temperature Scaling** (5 min implementation)
2. ✅ **Cap max confidence at 0.95** (1 min)
3. ✅ **Increase penalties for wrong answers** (2 min)

**Expected ECE**: 0.564 → **0.35-0.40**

### Phase 2: Medium Term (1-2 hours)
4. ✅ **Platt Scaling** (requires validation set)
5. ✅ **Improve Tier 1 granularity**

**Expected ECE**: 0.35 → **0.20-0.25**

### Phase 3: Long Term (Research)
6. ✅ **Histogram Binning**
7. ✅ **Ensemble Calibration**

**Expected ECE**: 0.20 → **<0.1**

## Recommended Immediate Actions

1. **Implement temperature scaling** with T=1.5
2. **Cap confidence at 0.95**
3. **Increase Tier 1 NO penalty to 0.15**
4. **Re-run experiment** and measure ECE improvement

## Expected Results

- **ECE**: 0.564 → **0.35-0.40** (38-44% reduction)
- **Confidence Distribution**: More spread out, less saturation
- **Calibration Error**: Reduced from 0.677 to ~0.4 in high-confidence bin
