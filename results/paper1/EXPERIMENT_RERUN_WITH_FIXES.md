# Experiment Rerun with Fixes

## Date: 2026-01-17

## Fixes Applied Before Rerun

### Fix 1: Fusion Method ✅
**Changed**: From summing confidences to highest confidence selection
- **Before**: `answer_votes[answer] += confidence` (summing)
- **After**: `specialist_outputs.sort(key=lambda x: x['confidence'], reverse=True)` (highest confidence)

**Expected Impact**: 
- Multi-Agent accuracy should improve (closer to/better than Single Specialist)
- Better handling when specialists disagree

### Fix 2: Multi-Specialist Team ✅
**Changed**: Removed GP from multi-specialist team
- **Before**: GP, Respiratory, Cardiology, Neurology
- **After**: Respiratory, Cardiology, Neurology, Gastroenterology
- **Matches**: Wang et al. 2024 (no GP in specialist team)

### Fix 3: Temperature Scaling Formula ✅
**Changed**: Corrected formula to reduce overconfidence
- **Before**: `confidence^(1/T)` (was increasing confidence!)
- **After**: `confidence^T` (correctly reduces confidence)

## Experiment Configuration

- **Questions**: 30 (from 100-question curated dataset)
- **Random Seed**: 42 (for reproducibility)
- **Configurations**: 4
  1. Single Specialist (GP)
  2. Single Specialist + Tier 1
  3. Multi-Agent (No Verification)
  4. Multi-Agent + Tier 1 (Two-Phase Verification) ⭐

## Expected Results After Fixes

### Expected Ranking:
1. **Multi-Agent + Tier 1** (best) ⭐
2. Multi-Agent (No Verification) or Single Specialist + Tier 1
3. Single Specialist (baseline)

### Expected Metrics:
- **Multi-Agent + Tier 1**: Accuracy > 65%, ECE < 0.15, AUROC > 0.6
- **Multi-Agent**: Accuracy > 60%, better than Single Specialist
- **Single Specialist + Tier 1**: Accuracy = 70%, ECE < 0.2

## Status

✅ **Experiment running** with all fixes applied
- Log: `results/paper1/final_comparison_30q_fixed_fusion.log`
- Estimated runtime: ~2.5 hours
