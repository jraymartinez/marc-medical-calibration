# Tier 1 Verification: Wu et al. Two-Phase Implementation

## Date
2026-01-14

## Implementation

Rewrote Tier 1 verification to match **Wu et al. 2024** "Uncertainty Estimation of Large Language Models in Medical Question Answering" exactly.

## Method: Two-Phase Verification

### Phase 1: Generate & Explain (Already Done)
- Specialist generates answer with step-by-step explanation
- This is already handled by `SpecialistAgent.analyze_question()`

### Phase 2: Two-Phase Verification (New Implementation)

#### Step 2a: Formulate Verification Questions
- Extract factual claims from the explanation
- Formulate 2-4 specific verification questions
- Questions target specific medical facts mentioned in the explanation

#### Step 2b: Answer Independently
- Answer verification questions **without** reference to the original explanation
- Uses only general medical knowledge
- This tests if the model can independently verify the claims

#### Step 2c: Answer With Reference
- Answer verification questions **with** reference to the original explanation
- Uses the explanation to guide answers
- This tests if the model is consistent with its own reasoning

#### Step 2d: Measure Inconsistencies
- Compare independent answers vs. reference answers
- Count inconsistencies (different answers = inconsistency)
- Inconsistency score: 0.0 (all consistent) to 1.0 (all inconsistent)

### Confidence Calculation

1. **Inconsistency → Confidence**: `verification_confidence = 1.0 - inconsistency_score`
   - Low inconsistency (0.0-0.2) → High confidence (0.8-1.0) → Status: YES
   - Moderate inconsistency (0.2-0.5) → Medium confidence (0.5-0.8) → Status: UNCERTAIN
   - High inconsistency (0.5-1.0) → Low confidence (0.0-0.5) → Status: NO

2. **Adjustment Factors** (same as before):
   - YES: `adjustment_factor = 1.0`
   - UNCERTAIN: `adjustment_factor = 0.5`
   - NO: `adjustment_factor = 0.15`

3. **Final S Score**:
   ```
   S_score = (consistency_weight * initial_confidence + 
              (1 - consistency_weight) * verification_confidence) * adjustment_factor
   ```

## Key Differences from Previous Implementation

### Previous (Incorrect)
- Single prompt asking model to verify its own answer
- Model self-assesses: "Is this correct?"
- Result: Almost always returned UNCERTAIN (too conservative)

### New (Wu et al. Method)
- Formulates specific verification questions
- Answers questions twice: independently and with reference
- Measures inconsistencies objectively
- Result: Should get more YES/NO decisions based on actual inconsistencies

## Expected Improvements

1. **More YES/NO Decisions**:
   - Previous: 800/800 UNCERTAIN (100%)
   - Expected: 200-400 YES, 50-150 NO, 250-550 UNCERTAIN

2. **Better Score Distinction**:
   - Previous: All specialists got 0.375-0.4 (similar)
   - Expected: S_scores vary more (0.2-0.8 range)

3. **More Answer Changes**:
   - Previous: 2 changes (net 0)
   - Expected: 10-20 changes with net improvement

4. **Accuracy Improvement**:
   - Previous: 53% (no improvement)
   - Expected: 55-58% (2-5% improvement)

## Implementation Details

### Files Modified
- `src/verification/tier1_verification.py`: Complete rewrite

### New Methods
- `_formulate_verification_questions()`: Step 2a
- `_answer_verification_questions_independently()`: Step 2b
- `_answer_verification_questions_with_reference()`: Step 2c
- `_measure_inconsistencies()`: Step 2d
- `_answers_similar()`: Helper for consistency checking

### Fallback
- If question formulation fails, uses simple verification fallback
- Still better than previous implementation

## Testing Plan

1. **Test with 10 questions**: Verify question formulation works
2. **Check inconsistency scores**: Should vary (not all 0.5)
3. **Verify S_score distribution**: Should see more variation
4. **Run full 100-question experiment**: Compare metrics

## References

Wu, J., Yu, Y., & Zhou, H. (2024). Uncertainty Estimation of Large Language Models in Medical Question Answering. *arXiv preprint*.

Key quote from paper:
> "First, an LLM generates a step-by-step explanation alongside its initial answer, followed by formulating verification questions to check the factual claims in the explanation. The model then answers these questions twice: first independently, and then referencing the explanation. Inconsistencies between the two sets of answers measure the uncertainty in the original response."
