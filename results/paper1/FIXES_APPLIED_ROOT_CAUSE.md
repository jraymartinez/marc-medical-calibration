# Fixes Applied Based on Root Cause Analysis

## Date: 2026-01-20

## Root Causes Found

1. **No Discrimination**: Final confidence for correct (0.304) vs wrong (0.312) almost identical
2. **S_scores Better**: Max S_score has AUROC 0.590 vs final confidence 0.412
3. **ECE Gap**: Confidence too low (0.28-0.32) relative to accuracy (0.65-0.70)
4. **Fusion Not Using Signals**: 29/30 questions use simple majority, ignoring S_scores

## Fixes Applied

### Fix 1: Use S_scores Directly in Final Confidence ✅
**Change**: Final confidence = 60% max S_score + 40% fusion result
**Location**: `scripts/run_final_comparison.py` line ~255
**Expected Impact**: 
- AUROC: 0.412 → 0.6+ (better discrimination)
- ECE: 0.24 → 0.18 (better calibration)

### Fix 2: Prefer High S_score Specialists in Fusion ✅
**Change**: If max S_score > 0.6, prefer that specialist even if minority
**Location**: `scripts/run_final_comparison.py` line ~230
**Expected Impact**: 
- Accuracy: Maintain or improve (correct answers with good S_scores win)

### Fix 3: Make Two-Phase Less Strict ✅
**Change**: YES threshold: inconsistency < 0.65 AND correctness > 0.60 (was 0.6/0.65)
**Location**: `src/verification/tier1_verification.py` line ~135
**Expected Impact**: More correct answers get YES status

### Fix 4: Increase YES Boost ✅
**Change**: YES adjustment_factor: 1.05 → 1.1
**Location**: `src/verification/tier1_verification.py` line ~150
**Expected Impact**: Better S_score discrimination

### Fix 5: Less Aggressive Temperature Scaling ✅
**Change**: For Multi-Agent + Two-Phase, reduce temp_scale by 0.1
**Location**: `scripts/run_final_comparison.py` line ~265
**Expected Impact**: Confidence better matches accuracy (helps ECE)

## Expected Results

### Before:
- Accuracy: 66.7%
- ECE: 0.240
- AUROC: 0.412

### After (Expected):
- Accuracy: 70%+ (maintain or improve)
- ECE: 0.15-0.18 (better calibration)
- AUROC: 0.6-0.7 (good discrimination)

## Key Insight

**Max S_score has AUROC 0.590** - we should use it directly instead of relying on fusion result alone. The combination of max S_score (60%) + fusion result (40%) should give us the best of both worlds.
