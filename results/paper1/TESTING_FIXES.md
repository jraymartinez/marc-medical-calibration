# Testing Verification Fixes

## Date
2026-01-13

## Fixes Being Tested

### 1. Less Aggressive Tier 1 Penalties ✅
- NO: 0.1 → **0.2**
- UNCERTAIN: 0.4 → **0.6**

### 2. Less Aggressive Tier 2 Penalties ✅
- REJECTED: 0.5 → **0.6**
- NEEDS_REVIEW: 0.75 → **0.85**

### 3. Confidence-Weighted Voting ✅
- Changed from "highest confidence selection"
- To "sum confidence per answer across specialists"

## Expected Improvements

### Before Fixes:
- All answers: Similar confidence (0.30-0.50)
- Can't distinguish correct from wrong
- Accuracy: 30.0% (same as baseline)

### After Fixes:
- Answers: More distinct confidence scores
- Can distinguish correct from wrong
- Accuracy: Should improve (target: 32-35%)

## Test Configuration

- Questions: 100 (current sample)
- Configurations: 3 (No Verification, Tier 1, Full Linear)
- Random Seed: 42 (same as before)

## Status

🔄 **Starting experiment with fixes...**
