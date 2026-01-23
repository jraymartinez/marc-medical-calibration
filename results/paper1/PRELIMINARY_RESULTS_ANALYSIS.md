# Preliminary Results Analysis: Tier 2 Improvements + GP

## Results So Far (Partial)

### Completed Configurations:

#### 1. **Multi (No Verification)**
- Accuracy: **43.3%**
- ECE: **0.482** (very high - poor calibration)
- AUROC: **0.536** (moderate)

#### 2. **Multi + Tier 1**
- Accuracy: **43.3%** (same as No Verification)
- ECE: **0.130** ✅ (much better - improved calibration!)
- AUROC: **0.507** (slightly lower)

---

## Key Observations

### 1. **Tier 1 Improves Calibration Significantly** ✅

**ECE Improvement**:
- No Verification: 0.482 (very poor calibration)
- Tier 1: 0.130 (much better calibration)
- **Improvement: -0.352** (73% reduction in ECE!)

**This is excellent!** Tier 1 verification significantly improves calibration.

### 2. **Accuracy Unchanged**

- No Verification: 43.3%
- Tier 1: 43.3%
- **No change** - Tier 1 doesn't improve accuracy, but improves calibration

### 3. **AUROC Slightly Lower**

- No Verification: 0.536
- Tier 1: 0.507
- **Slight decrease** - but still moderate discrimination

---

## Comparison to Previous Results

### Previous Run (Respiratory Specialist, Old Tier 2):
- Multi (No Verification): 43.3% accuracy
- Multi + Tier 1: 46.7% accuracy
- Multi + Full Linear: 43.3% accuracy

### Current Run (GP, Improved Tier 2):
- Multi (No Verification): 43.3% accuracy (same)
- Multi + Tier 1: 43.3% accuracy (lower than previous 46.7%)

**Observation**: GP might not be performing better than respiratory specialist yet, OR the deterministic mode is affecting results.

---

## What to Watch For

### 1. **Single Specialist Results** (GP)
- Is GP better than respiratory specialist?
- How does GP perform with verification?

### 2. **Multi + Full Linear** (Currently Running)
- Will improved Tier 2 help or hurt?
- Previous: Tier 2 hurt accuracy (-3.4%)
- Expected: Tier 2 should help with improvements

### 3. **Calibration Improvements**
- Tier 1 already shows **excellent ECE improvement** (0.482 → 0.130)
- Will Tier 2 maintain or improve this?

---

## Early Insights

### ✅ **Tier 1 Verification Works!**
- **ECE improved dramatically** (0.482 → 0.130)
- Shows verification can improve calibration
- This is a **strong research finding**

### ⚠️ **Accuracy Not Improving Yet**
- Multi-specialist accuracy: 43.3% (unchanged)
- Need to see single specialist (GP) results
- May need to wait for Full Linear to see Tier 2 impact

### 📊 **Calibration is Key Finding**
- Even if accuracy doesn't improve, **calibration improvement is valuable**
- Better calibration = better uncertainty quantification
- This is a **valid research contribution**

---

## Next Steps

1. ⏳ **Wait for experiment completion**
2. ⏳ **Analyze full results** (all 7 configurations)
3. ⏳ **Compare GP vs Respiratory specialist**
4. ⏳ **Check Tier 2 impact** with improvements
5. ⏳ **Refine research question** based on findings

---

## Status

**Experiment is progressing well!**

- ✅ Tier 1 shows **excellent calibration improvement**
- ⏳ Waiting for Single specialist (GP) results
- ⏳ Waiting for Multi + Full Linear (currently running)
- ⏳ Waiting for Multi + Bayesian

**Estimated time remaining**: ~1-2 hours
