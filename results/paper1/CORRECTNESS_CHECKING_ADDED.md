# Correctness Checking Added to Tier 1 Verification

## Date
2026-01-15

## Fix Applied

Added **correctness checking** to Tier 1 verification to address the fundamental limitation of Wu et al. Two-Phase Verification method.

### The Problem

**Wu et al. method only checks internal consistency, not correctness:**
- Measures inconsistencies between independent and reference answers
- Wrong answers can have low inconsistency if internally consistent
- Result: Wrong answers get YES status → high confidence → worse ECE

### The Solution

**Added Step 2e: Correctness Checking**

After measuring inconsistencies (Wu et al. method), we now also check if the answer is **actually correct**:

1. **Consistency checking** (Wu et al.): Measures internal coherence
2. **Correctness checking** (NEW): Measures medical accuracy
3. **Combine both**: Both must be good for high confidence

### Implementation

#### New Method: `_check_answer_correctness()`

- Asks LLM: "Is this answer medically correct?"
- Returns correctness score: 0.0 (wrong) to 1.0 (correct)
- Checks medical facts, appropriateness, accuracy

#### Combined Verification

```python
# Combine consistency and correctness
combined_score = (1.0 - inconsistency_score) * 0.5 + correctness_score * 0.5
verification_confidence = combined_score

# Status determination (BOTH must be good)
if inconsistency_score < 0.6 and correctness_score > 0.6:
    verified_status = "YES"  # Low inconsistency AND correct
elif inconsistency_score < 0.8 and correctness_score > 0.4:
    verified_status = "UNCERTAIN"
else:
    verified_status = "NO"  # High inconsistency OR wrong answer
```

### Expected Impact

#### Before (Consistency Only)
- Wrong but consistent answer → YES status → high confidence
- Wrong answers in high-confidence bins (0.8-0.9)
- Accuracy in high bins: 42-47% (worse than baseline 50%)
- **ECE: 0.30-0.32** (worse than baseline 0.265)

#### After (Consistency + Correctness)
- Wrong but consistent answer → NO status (correctness low) → low confidence
- Wrong answers stay in lower-confidence bins (0.6-0.7)
- High-confidence bins have better accuracy (should be >50%)
- **ECE: Expected 0.25-0.27** (better than baseline!)

### Status Distribution Expected

**Before**:
- YES: 51% on wrong answers ❌
- NO: 27% on wrong answers

**After**:
- YES: ~20% on wrong answers ✅ (only if both consistent AND correct)
- NO: ~60% on wrong answers ✅ (catches wrong answers)

### Accuracy Expected

- **Tier 1**: 50% → **52-54%** (+2-4%)
- **Full Linear**: 48% → **53-55%** (+5-7%)

### ECE Expected

- **Tier 1**: 0.301 → **0.25-0.27** (improved)
- **Full Linear**: 0.320 → **0.25-0.27** (improved)

## Next Steps

1. ✅ **Correctness checking added** - Code updated
2. **Test on 10 questions** - Verify it catches wrong answers
3. **Run full experiment** - Test on 100 questions
4. **Verify improvements** - Check ECE, accuracy, degradations
