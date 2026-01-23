# Experiment Running: Tier 2 Improvements Test

## Status: Running

The 30-question experiment is currently running with all Tier 2 improvements applied.

---

## Improvements Applied

### 1. **Tier 2 Prompt** ✅
- Less strict language ("STRICT" → removed)
- Focus on "Is this answer medically correct?" not "Are there better alternatives?"
- Added answer options to GP context

### 2. **Penalty Factors** ✅
- REJECTED: 0.15 → 0.35 (less aggressive)
- NEEDS_REVIEW: 0.5 → 0.65 (less aggressive)

### 3. **Temperature** ✅
- Tier 2: 0.15 → 0.2 (more nuanced judgments)

### 4. **Non-Determinism Fix** ✅
- Answer caching enabled (deterministic specialist answers)
- Same question → same answer across configurations

---

## Expected Results

### Previous Results (Before Improvements):
- Single + Full Linear: 43.3% accuracy, ECE=0.156, AUROC=0.532
- Multi + Full Linear: 43.3% accuracy, ECE=0.164, AUROC=0.753

### Expected Improvements:
- **Accuracy**: Should improve (Tier 2 less likely to reject correct answers)
- **ECE**: Should improve (better calibration)
- **AUROC**: Should maintain or improve (better uncertainty discrimination)

---

## How to Compare Results

Once the experiment completes, run:

```bash
python scripts/compare_tier2_improvements.py \
    results/paper1/comparison_7configs_20260111_032033.json \
    results/paper1/comparison_7configs_[NEW_TIMESTAMP].json
```

This will show:
- Before vs After metrics for each configuration
- Changes in accuracy, ECE, AUROC
- Assessment of Tier 2 improvements

---

## Key Questions to Answer

1. **Did accuracy improve?**
   - Previous: Tier 2 hurt accuracy (-3.4% from Tier 1)
   - Expected: Tier 2 should help or at least not hurt

2. **Did calibration improve?**
   - Previous: ECE was similar or slightly worse
   - Expected: Better calibration with improved Tier 2

3. **Did uncertainty discrimination improve?**
   - Previous: AUROC was good (0.753 for multi)
   - Expected: Maintain or improve AUROC

---

## Next Steps After Results

1. **Analyze comparison** using the comparison script
2. **If promising**: Scale to 100 questions for statistical power
3. **If not promising**: Further tune Tier 2 parameters
4. **Document findings** in results summary

---

## Experiment Details

- **Questions**: 30 (same as previous run)
- **Random Seed**: 42 (same questions as previous run)
- **Model**: Llama 3.1 8B Instruct (FP16)
- **Configurations**: 7 (Single + Multi specialist, various verification levels)
- **Deterministic Mode**: Enabled (same question → same answer)

---

## Status

⏳ **Experiment is running...**

Check progress in terminal or wait for completion notification.
