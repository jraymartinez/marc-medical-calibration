# Critical Temperature Scaling Formula Fix

## Date: 2026-01-17

## Critical Bug Found!

**User Question**: "Isn't the range of temperature 0 to 1 only? Why are we using 1.5?"

**Answer**: Temperature scaling for calibration uses T > 1, BUT we had the **WRONG FORMULA**!

## The Bug

### What We Were Doing (WRONG):
```python
temperature = 1.5
final_confidence = final_confidence ** (1.0 / temperature)  # WRONG!
# This gives: confidence^(1/1.5) = confidence^0.667
```

### What This Actually Does:
- For confidence = 0.9: 0.9^0.667 = **0.932** (INCREASES by +0.032)
- For confidence = 0.8: 0.8^0.667 = **0.862** (INCREASES by +0.062)
- **This INCREASES confidence, making overconfidence WORSE!**

### What We Should Do (CORRECT):
```python
temperature = 1.5
final_confidence = final_confidence ** temperature  # CORRECT!
# This gives: confidence^1.5
```

### What This Actually Does:
- For confidence = 0.9: 0.9^1.5 = **0.854** (DECREASES by -0.046)
- For confidence = 0.8: 0.8^1.5 = **0.716** (DECREASES by -0.084)
- **This DECREASES confidence, reducing overconfidence!**

## Mathematical Explanation

For values between 0 and 1:
- **Raising to power < 1** (like 0.667): **INCREASES** the value
- **Raising to power > 1** (like 1.5): **DECREASES** the value

**To reduce overconfidence, we need to DECREASE confidence, so we use:**
- `confidence^T` where T > 1

**NOT:**
- `confidence^(1/T)` where T > 1 (this increases confidence!)

## Impact

This bug explains why:
1. **ECE was getting worse** - we were making the model MORE overconfident
2. **Full Linear ECE was worse than baseline** - wrong formula was increasing confidence
3. **Temperature scaling wasn't working** - we were doing the opposite of what we wanted

## Fix Applied

### Files Fixed:
1. `scripts/run_optimized_multi_specialist.py`
   - Changed: `final_confidence ** (1.0 / temperature)` → `final_confidence ** temperature`
   - Temperature: 1.5 (T > 1 reduces confidence)

2. `scripts/test_tier1_tier2_improvements.py`
   - Changed: `conf ** (1.0 / 1.5)` → `conf ** 1.5`
   - Temperature: 1.5

## Expected Results After Fix

- **ECE should improve significantly** (we're now actually reducing overconfidence)
- **Full Linear ECE should be better than baseline** (correct formula)
- **Confidence scores should be more calibrated**

## Next Steps

1. **Re-test with 10 questions** to verify the fix works
2. **Expected**: ECE should improve for both Tier 1 and Full Linear
3. **If successful, run full 100-question experiment**
