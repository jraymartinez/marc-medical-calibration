# Correctness Checker Removed - Using Pure Wu et al. Method

## Decision

**Option 1 Selected**: Remove the correctness checker entirely and rely only on Wu et al.'s consistency method (inconsistency-based verification).

## Changes Made

### 1. Removed Correctness Checking
- Removed `_check_answer_correctness()` call from `verify_specialist()`
- Removed correctness_score from combined_score calculation
- Removed correctness_score from return dictionary (set to None)

### 2. Updated Verification Logic
- **verification_confidence**: Now uses ONLY `1.0 - inconsistency_score` (pure Wu et al. method)
- **verified_status**: Based ONLY on inconsistency_score:
  - `inconsistency_score < 0.3` → YES (internally consistent)
  - `0.3 <= inconsistency_score < 0.6` → UNCERTAIN (some contradictions)
  - `inconsistency_score >= 0.6` → NO (highly contradictory)

### 3. Updated Adjustment Factors
- **NO**: 0.4 (high inconsistency → low confidence)
- **UNCERTAIN**: 0.7 (moderate inconsistency → moderate confidence)
- **YES**: 1.0 (low inconsistency → maintain confidence, no boost)

### 4. Updated Verification Method Name
- Changed from `"two_phase_wu_et_al_with_correctness"` to `"two_phase_wu_et_al"`

## Rationale

The correctness checker was causing issues:
1. **Too conservative**: Everything marked as UNCERTAIN/NO
2. **No discrimination**: Correct and wrong answers had similar scores
3. **Accuracy dropped**: From 66.7% to 53.3% after the fix
4. **Model limitation**: Llama 3.1 8B may not reliably evaluate medical correctness

## Expected Impact

By using only Wu et al.'s consistency method:
- **Simpler**: No additional LLM call for correctness checking
- **Faster**: One less LLM inference per specialist
- **More reliable**: Consistency checking is what Wu et al. validated
- **Better discrimination**: Inconsistency scores should distinguish consistent vs inconsistent answers

## Next Steps

1. Run 30-question test to validate the change
2. Check if inconsistency scores provide better discrimination
3. Verify that accuracy improves back to 66.7% or higher
4. Check if AUROC and ECE improve
