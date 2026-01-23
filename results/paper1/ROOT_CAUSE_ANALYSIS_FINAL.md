# Root Cause Analysis: Multi-Agent + Tier 1 Underperformance

## Date: 2026-01-19

## Current Results

- **Single Specialist**: 70.0% accuracy
- **Single Specialist + Tier 1**: 70.0% accuracy (ECE improved: 0.144 vs 0.869)
- **Multi-Agent (No Verification)**: 60.0% accuracy
- **Multi-Agent + Tier 1**: 53.3% accuracy ❌

## Expected Ranking

1. Multi-Agent + Tier 1 (best) ⭐
2. Multi-Agent (No Verification) or Single Specialist + Tier 1
3. Single Specialist (baseline)

## Actual Ranking

1. Single Specialist + Tier 1 (70.0%)
2. Single Specialist (70.0%)
3. Multi-Agent (No Verification) (60.0%)
4. Multi-Agent + Tier 1 (53.3%) ❌

## Root Causes Identified

### Issue 1: No Correct Specialist (8/14 wrong cases = 57%)

**Problem**: In 57% of wrong cases, none of the 4 specialists selected the correct answer.

**Root Cause**: Specialist agents themselves are giving wrong answers, not a fusion/verification issue.

**Impact**: Cannot be fixed by fusion/verification alone - requires improving specialist prompts or knowledge bases.

**Examples**:
- Question 3: All 4 specialists selected wrong answers
- Question 9: All 4 specialists selected wrong answers
- Question 21: All 4 specialists selected wrong answers

### Issue 2: Correct Specialist Lost (1/14 wrong cases = 7%)

**Problem**: Correct specialist exists but wrong one selected by fusion.

**Root Cause**: Highest confidence selection picks wrong specialist when wrong specialist has higher confidence.

**Example**: Question 12
- Respiratory: C (correct, conf: 0.282)
- Cardiology, Neurology, Gastroenterology: A (wrong, conf: 0.297, 0.274, 0.213)
- **Selected**: A (wrong) because Cardiology has highest confidence (0.297)

**Fix Options**:
1. **Majority Voting**: Select answer chosen by majority of specialists
2. **Answer Validation**: Boost confidence for correct answers (if we can identify them)
3. **Confidence Weighted Voting**: Sum confidences per answer, select highest sum

### Issue 3: Tier 1 Penalized Correct Specialist (1/14 wrong cases = 7%)

**Problem**: Tier 1 reduced confidence for correct answers more than wrong answers.

**Root Cause**: Tier 1 penalties are too aggressive, causing correct answers to lose fusion.

**Fix**: Adjust Tier 1 to be less aggressive on correct answers.

## Recommended Fixes

### Fix 1: Use Majority Voting for Multi-Agent Fusion

**Current Method**: Highest confidence selection
```python
specialist_outputs.sort(key=lambda x: x['confidence'], reverse=True)
final_answer = specialist_outputs[0]['answer']
```

**Problem**: Single wrong specialist with high confidence can override correct majority.

**Proposed Method**: Majority voting with confidence tie-breaking
```python
from collections import Counter

# Count votes per answer
answer_votes = Counter([s['answer'] for s in specialist_outputs])
most_common = answer_votes.most_common()

if most_common[0][1] > len(specialist_outputs) / 2:
    # Majority exists
    final_answer = most_common[0][0]
else:
    # No majority - use highest confidence
    specialist_outputs.sort(key=lambda x: x['confidence'], reverse=True)
    final_answer = specialist_outputs[0]['answer']
```

**Expected Impact**: 
- Question 8: 3/4 specialists correct → Majority voting selects correct answer ✅
- Question 12: 1/4 specialists correct → Still selects wrong (but this is expected)

### Fix 2: Adjust Tier 1 Penalties

**Current Penalties**:
- NO: 0.4 (multiplier)
- UNCERTAIN: 0.7 (multiplier)
- YES: 1.0 (no penalty)

**Problem**: Too aggressive, causing correct answers to lose fusion.

**Proposed Adjustment**:
- NO: 0.5 (less aggressive)
- UNCERTAIN: 0.8 (less aggressive)
- YES: 1.0 (no change)

**Expected Impact**: Correct answers maintain higher confidence, win fusion more often.

### Fix 3: Improve Specialist Prompts (Long-term)

**Problem**: 57% of wrong cases have no correct specialist.

**Solution**: Improve specialist prompts to:
- Better understand question context
- Consider all options carefully
- Use medical knowledge more effectively

**Impact**: Requires prompt engineering and testing, but addresses root cause.

## Implementation Priority

1. **Fix 1 (Majority Voting)**: High priority - addresses 1/14 cases directly, may help others
2. **Fix 2 (Tier 1 Penalties)**: Medium priority - addresses 1/14 cases, improves overall confidence
3. **Fix 3 (Specialist Prompts)**: Low priority - long-term improvement, requires extensive testing

## Expected Results After Fixes

- **Multi-Agent + Tier 1**: 60-65% accuracy (up from 53.3%)
- **Multi-Agent (No Verification)**: 60-65% accuracy (maintain or improve)
- **Ranking**: Multi-Agent + Tier 1 ≥ Multi-Agent ≥ Single Specialist

## Next Steps

1. Implement Fix 1 (Majority Voting)
2. Implement Fix 2 (Tier 1 Penalties)
3. Re-run 30-question experiment
4. Analyze results and iterate
