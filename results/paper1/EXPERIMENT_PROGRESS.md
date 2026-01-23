# Experiment Progress: Tier 2 Improvements + GP Implementation

## Current Status: Running ⏳

The experiment is currently running with:
- ✅ **Tier 2 improvements** (less strict prompt, adjusted penalties, higher temperature)
- ✅ **Non-determinism fix** (deterministic specialist answers)
- ✅ **GP for single specialist** (General Practitioner instead of respiratory specialist)

---

## Configurations Completed So Far

Based on terminal output:

1. ✅ **Single (No Verification)** - Completed
2. ✅ **Single + Tier 1** - Completed
3. ✅ **Single + Full Linear** - Completed
4. ✅ **Multi (No Verification)** - Completed
5. ⏳ **Multi + Tier 1** - Currently running (or just finished)

## Remaining Configurations

6. ⏳ **Multi + Full Linear** - Pending
7. ⏳ **Multi + Bayesian** - Pending

---

## Key Changes in This Run

### 1. **Tier 2 Improvements**
- Less strict prompt (focus on correctness, not finding flaws)
- Less aggressive penalties (REJECTED: 0.15 → 0.35, NEEDS_REVIEW: 0.5 → 0.65)
- Higher temperature (0.15 → 0.2)
- Answer options added to GP context

### 2. **Non-Determinism Fix**
- Deterministic specialist answers (same question → same answer)
- Answer caching enabled
- `temperature=0.0` and `do_sample=False` for deterministic mode

### 3. **GP for Single Specialist**
- Single specialist configurations use **GP** (General Practitioner)
- Multi-specialist configurations use **domain specialists** (respiratory, cardiology, etc.)
- GP has broader medical knowledge across all specialties

---

## Expected Improvements

### Previous Results (Before Improvements):
- Single + Tier 1: 46.7% accuracy
- Single + Full Linear: 43.3% accuracy (Tier 2 hurt!)
- Multi + Tier 1: 46.7% accuracy
- Multi + Full Linear: 43.3% accuracy (Tier 2 hurt!)

### Expected Results (With Improvements):
- **GP should perform better** than respiratory specialist (broader knowledge)
- **Tier 2 should help more** (less likely to reject correct answers)
- **Better accuracy** overall (GP + improved Tier 2)

---

## What to Watch For

1. **GP Performance**: Is GP better than respiratory specialist?
2. **Tier 2 Impact**: Does Tier 2 help or hurt with improvements?
3. **Accuracy Comparison**: Single vs Multi configurations
4. **Calibration**: ECE and AUROC improvements

---

## Next Steps After Completion

1. **Compare results** to previous run
2. **Analyze GP vs Respiratory specialist** performance
3. **Check if Tier 2 improvements helped**
4. **Refine research question** based on findings
5. **Decide on final research direction**:
   - Single GP + verification?
   - Multi-specialist (if it helps)?
   - Or something else?

---

## Estimated Time Remaining

- **Completed**: ~5/7 configurations
- **Remaining**: ~2 configurations
- **Estimated**: ~1-2 hours remaining (depending on question processing time)

The experiment is progressing well! Once it completes, we can analyze the results and see if GP + improved Tier 2 performs better.
