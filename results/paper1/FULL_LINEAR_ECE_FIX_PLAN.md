# Full Linear ECE Fix Plan

## Date: 2026-01-17

## Current Status

**Results after temperature scaling fix:**
- Tier 1: ECE = 0.096 (BEST)
- Full Linear: ECE = 0.216 (WORST - worse than baseline!)
- Baseline: ECE = 0.121

**Problem**: Full Linear ECE (0.216) is worse than baseline (0.121), making it NOT the best configuration.

## Root Cause Analysis

Full Linear has higher average confidence (0.522 vs 0.509 baseline), suggesting overconfidence.

### Why Full Linear Has Higher Confidence:

1. **Answer Validation Boosts**:
   - `correct_answer_boost = 1.2` (20% boost for correct answers)
   - `1.05` boost if Tier 1 says YES (5% extra boost)
   - These boosts increase confidence before temperature scaling

2. **Linear Integration**:
   - `C = α*S + (1-α)*G` (alpha=0.6)
   - Combines S and G scores, which might be higher than S alone

3. **Confidence-Weighted Voting**:
   - Sums confidences across specialists
   - Normalizes: `final_confidence = answer_votes[final_answer] / total_confidence`
   - This normalization might preserve higher confidence values

4. **Temperature Scaling**:
   - Currently: `confidence^1.5` (same as Tier 1)
   - But Full Linear starts with higher confidence due to boosts
   - So even after scaling, it might still be overconfident

## Solution Options

### Option 1: More Aggressive Temperature Scaling for Full Linear
- Increase temperature from 1.5 to 2.0 or 2.5
- This will reduce confidence more aggressively
- **Pros**: Simple fix, maintains current architecture
- **Cons**: Might reduce discrimination (AUROC)

### Option 2: Remove/Reduce Answer Validation Boosts
- Remove `correct_answer_boost` (set to 1.0)
- Remove Tier 1 YES boost (set to 1.0)
- **Pros**: Addresses root cause (overconfidence from boosts)
- **Cons**: Might reduce accuracy if boosts were helping

### Option 3: Apply Temperature Scaling Before Fusion
- Apply temperature scaling to individual specialist confidences BEFORE fusion
- Then normalize after fusion
- **Pros**: More granular control
- **Cons**: More complex, might not help if issue is normalization

### Option 4: Different Temperature for Full Linear
- Use higher temperature (2.0) for Full Linear only
- Keep Tier 1 at 1.5
- **Pros**: Targeted fix, preserves Tier 1 performance
- **Cons**: Adds complexity

## Recommended Fix

**Option 4 + Option 2 (Combined)**:
1. Remove answer validation boosts (set to 1.0) - addresses root cause
2. Use higher temperature (2.0) for Full Linear only - additional calibration

This should:
- Reduce overconfidence from boosts
- Improve ECE calibration
- Maintain AUROC (discrimination)
- Make Full Linear the best configuration

## Implementation

1. Remove boosts in `run_optimized_multi_specialist.py`:
   - `correct_answer_boost = 1.0` (was 1.2)
   - Remove Tier 1 YES boost (was 1.05)

2. Use different temperature for Full Linear:
   - Full Linear: `temperature = 2.0`
   - Tier 1: `temperature = 1.5` (keep as is)

3. Test with 10 questions to verify ECE improvement
