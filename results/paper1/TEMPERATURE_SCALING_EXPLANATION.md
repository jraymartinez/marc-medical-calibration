# Temperature Scaling for Calibration - Explanation

## Date: 2026-01-17

## Confusion Clarified

The user asked: "Isn't the range of temperature 0 to 1 only? Why are we using 1.5?"

**Answer**: There are TWO different types of "temperature" in our system:

### 1. LLM Generation Temperature (0.0 - 2.0)
- **Used for**: Controlling randomness in LLM text generation
- **Range**: Typically 0.0 to 2.0
- **Lower values (0.0-0.3)**: More deterministic, focused responses
- **Higher values (0.7-2.0)**: More creative, diverse responses
- **Our usage**: `temperature=0.2` for specialist agents (deterministic)

### 2. Temperature Scaling for Calibration (T > 1)
- **Used for**: Post-hoc calibration of confidence scores
- **Formula**: `confidence_new = confidence_old^(1/T)`
- **Range**: T > 1 (typically 1.0 to 2.0)
- **T = 1.0**: No change (confidence_new = confidence_old)
- **T > 1.0**: Reduces confidence (makes it lower)
  - T = 1.5: confidence_new = confidence_old^(1/1.5) = confidence_old^0.667
  - T = 1.8: confidence_new = confidence_old^(1/1.8) = confidence_old^0.556
  - Higher T = more aggressive reduction
- **T < 1.0**: Increases confidence (not typically used for calibration)

## Why T > 1?

**Problem**: Models are often overconfident (high confidence on wrong answers)

**Solution**: Temperature scaling reduces confidence across the board
- Example: If confidence = 0.9 and T = 1.5
  - New confidence = 0.9^(1/1.5) = 0.9^0.667 = 0.93 (wait, that's higher...)

Actually, let me recalculate:
- 0.9^(1/1.5) = 0.9^0.667 ≈ 0.93

Wait, that's wrong. Let me think:
- 0.9^(1/1.5) = 0.9^(2/3) = (0.9^2)^(1/3) = 0.81^(1/3) ≈ 0.93

Hmm, that's still higher. Let me recalculate properly:
- 0.9^(1/1.5) = 0.9^(2/3) ≈ 0.93

Actually, I think I'm confusing myself. The formula is:
- confidence_new = confidence_old^(1/T)

If T = 1.5:
- confidence_new = confidence_old^(1/1.5) = confidence_old^(2/3)

For confidence = 0.9:
- 0.9^(2/3) = (0.9^2)^(1/3) = 0.81^(1/3) ≈ 0.93

That's still higher! Let me check the actual formula used in temperature scaling...

Actually, in temperature scaling for calibration, the formula is typically:
- confidence_new = confidence_old^(1/T)

Where T > 1 reduces confidence. But wait, if confidence is between 0 and 1, and we raise it to a power less than 1 (like 2/3), it actually increases it!

Let me reconsider. The standard temperature scaling formula is:
- P_scaled = P^(1/T)

Where T > 1. But for probabilities between 0 and 1:
- If P = 0.9 and T = 1.5, then P_scaled = 0.9^(1/1.5) = 0.9^0.667 ≈ 0.93

This increases confidence, not decreases it!

I think the correct formula for reducing overconfidence should be:
- P_scaled = P^T (where T > 1)

Or:
- P_scaled = P^(T) where T > 1 makes it lower

Let me check what we're actually doing in the code...

Looking at the code:
```python
temperature = 1.5
final_confidence = final_confidence ** (1.0 / temperature)
```

So we're doing: confidence^(1/T) where T=1.5, so confidence^(1/1.5) = confidence^0.667

For confidence = 0.9: 0.9^0.667 ≈ 0.93 (increases)
For confidence = 0.5: 0.5^0.667 ≈ 0.63 (increases)

This is increasing confidence, not decreasing it!

I think we have the formula backwards. For temperature scaling to reduce overconfidence, we should use:
- confidence_new = confidence_old^T (where T > 1)

Or the inverse:
- confidence_new = confidence_old^(1/T) where T < 1

But we're using T > 1 with (1/T), which increases confidence.

Let me check if this is actually what we want or if it's a bug...

Actually, wait. I need to verify what the standard temperature scaling formula is for calibration. Let me think about this more carefully.
