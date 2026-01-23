# Experiment Started with Root Cause Fixes

## Date: 2026-01-20

## Root Causes Identified and Fixed

### 1. **No Discrimination in Final Confidence**
- **Problem**: Final confidence for correct (0.304) vs wrong (0.312) almost identical
- **Fix**: Use 60% max S_score + 40% fusion result for final confidence
- **Expected**: AUROC 0.412 → 0.6+

### 2. **S_scores Have Better Discrimination**
- **Finding**: Max S_score has AUROC 0.590 vs final confidence 0.412
- **Fix**: Prefer high S_score specialists (>0.6) even if minority
- **Expected**: Better accuracy and discrimination

### 3. **ECE Gap**
- **Problem**: Confidence too low (0.28-0.32) relative to accuracy (0.65-0.70)
- **Fix**: Less aggressive temperature scaling (reduce by 0.1)
- **Expected**: ECE 0.24 → 0.15-0.18

### 4. **Two-Phase Too Strict**
- **Problem**: No specialists getting YES status
- **Fix**: Lowered thresholds (inconsistency < 0.65, correctness > 0.60)
- **Expected**: More correct answers get YES, fusion can use them

## Fixes Applied

1. ✅ Final confidence = 60% max S_score + 40% fusion result
2. ✅ Prefer max S_score specialist if S > 0.6 (even if minority)
3. ✅ Less aggressive temperature scaling for Multi-Agent + Two-Phase
4. ✅ Lowered Two-Phase YES thresholds
5. ✅ Increased YES boost (1.05 → 1.1)

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

**Max S_score has AUROC 0.590** - we're now using it directly (60% weight) combined with fusion result (40%) for better discrimination.

## Log File

`results/paper1/final_comparison_30q_root_cause_fixes.log`

## Expected Runtime

~2 hours (30 questions × 4 configurations)
