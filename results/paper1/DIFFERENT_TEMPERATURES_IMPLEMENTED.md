# Different Temperatures for Independent vs Reference Answers

## Implementation

### Changes Made

1. **Added separate temperature parameters** to `Tier1Verifier.__init__()`:
   - `independent_temp: float = 0.4` - For independent answers (higher for diversity)
   - `reference_temp: float = 0.2` - For reference answers (lower for consistency)
   - `question_temp: float = 0.3` - For verification question formulation

2. **Updated method calls**:
   - `_formulate_verification_questions()`: Uses `self.question_temp` (0.3)
   - `_answer_verification_questions_independently()`: Uses `self.independent_temp` (0.4)
   - `_answer_verification_questions_with_reference()`: Uses `self.reference_temp` (0.2)

## Rationale

### Why Different Temperatures?

**Wu et al.'s method** measures inconsistency between:
1. **Independent answers** (without reference) - Should explore different reasoning paths
2. **Reference answers** (with reference) - Should be consistent with explanation

### Temperature Settings

| Step | Temperature | Rationale |
|------|-------------|-----------|
| **Question Formulation** | 0.3 | Moderate - balanced coverage and focus |
| **Independent Answers** | 0.4 | **Higher** - more diversity to catch inconsistencies |
| **Reference Answers** | 0.2 | **Lower** - consistent with explanation |

### Expected Impact

1. **Better Inconsistency Detection**:
   - Independent answers (0.4) explore different reasoning paths
   - More likely to catch inconsistencies in wrong but consistent answers
   - Better discrimination between correct and wrong answers

2. **More Reliable Reference**:
   - Reference answers (0.2) stay consistent with explanation
   - Provides stable baseline for comparison
   - Reduces false positives (correct answers marked as inconsistent)

3. **Improved Performance**:
   - Should improve accuracy (better detection of wrong answers)
   - Should improve AUROC (better discrimination)
   - Should improve ECE (more reliable confidence scores)

## Backward Compatibility

- Default `temperature` parameter still exists (for backward compatibility)
- If not specified, uses the new specific temperatures
- Old code will still work but use new temperature settings

## Next Steps

1. Test with these new temperature settings
2. Compare with previous results (single temperature 0.2)
3. If needed, tune the temperatures further:
   - Independent: 0.3-0.5 range
   - Reference: 0.1-0.3 range
   - Question: 0.2-0.4 range
