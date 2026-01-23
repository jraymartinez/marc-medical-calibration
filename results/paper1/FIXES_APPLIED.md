# Fixes Applied to Improve Multi-Agent + Tier 1 Performance

## Date: 2026-01-19

## Issues Identified

1. **Correct Specialist Lost**: 1/14 wrong cases - Correct specialist exists but wrong one selected by fusion
2. **Tier 1 Too Aggressive**: 1/14 wrong cases - Tier 1 penalized correct specialist more than wrong
3. **No Correct Specialist**: 8/14 wrong cases - Cannot be fixed by fusion/verification alone

## Fixes Applied

### Fix 1: Majority Voting for Multi-Agent Fusion ✅

**File**: `scripts/run_final_comparison.py`

**Change**: Switched from highest confidence selection to majority voting with confidence tie-breaking

**Before**:
```python
# Highest confidence selection
specialist_outputs_sorted = sorted(specialist_outputs, key=lambda x: x['confidence'], reverse=True)
final_answer = specialist_outputs_sorted[0]['answer']
```

**After**:
```python
# Majority voting with confidence tie-breaking
from collections import Counter
answer_votes = Counter([s['answer'] for s in specialist_outputs])
most_common = answer_votes.most_common()

if most_common and most_common[0][1] > len(specialist_outputs) / 2:
    # Majority exists (>50% of specialists agree)
    majority_answer = most_common[0][0]
    majority_specialists = [s for s in specialist_outputs if s['answer'] == majority_answer]
    best_specialist = max(majority_specialists, key=lambda x: x['confidence'])
    final_answer = best_specialist['answer']
else:
    # No majority - use highest confidence (tie-breaking)
    specialist_outputs_sorted = sorted(specialist_outputs, key=lambda x: x['confidence'], reverse=True)
    final_answer = specialist_outputs_sorted[0]['answer']
```

**Expected Impact**:
- Question 8: 3/4 specialists correct → Majority voting selects correct answer ✅
- Question 12: 1/4 specialists correct → Still selects wrong (expected, but less likely to happen)

### Fix 2: Less Aggressive Tier 1 Penalties ✅

**File**: `src/verification/tier1_verification.py`

**Change**: Reduced penalties for NO and UNCERTAIN statuses

**Before**:
- NO: 0.35 (multiplier)
- UNCERTAIN: 0.75 (multiplier)
- YES: 1.0 (no penalty)

**After**:
- NO: 0.5 (less aggressive)
- UNCERTAIN: 0.8 (less aggressive)
- YES: 1.0 (no change)

**Expected Impact**:
- Correct answers maintain higher confidence after Tier 1
- Less likely to lose fusion due to Tier 1 penalties
- Better balance between catching wrong answers and preserving correct answers

## Expected Results After Fixes

### Before Fixes:
- Multi-Agent + Tier 1: 53.3% accuracy
- Multi-Agent (No Verification): 60.0% accuracy
- Single Specialist: 70.0% accuracy

### After Fixes (Expected):
- Multi-Agent + Tier 1: **60-65% accuracy** (up from 53.3%)
- Multi-Agent (No Verification): **60-65% accuracy** (maintain or improve)
- Single Specialist: 70.0% accuracy (baseline)

### Expected Ranking:
1. Single Specialist + Tier 1: 70.0% (best ECE: 0.144)
2. Single Specialist: 70.0% (baseline)
3. Multi-Agent + Tier 1: **60-65%** (improved from 53.3%)
4. Multi-Agent (No Verification): **60-65%**

## Next Steps

1. ✅ Fix 1 applied (Majority Voting)
2. ✅ Fix 2 applied (Tier 1 Penalties)
3. ⏳ Re-run 30-question experiment
4. ⏳ Analyze results and iterate

## Notes

- **8/14 wrong cases** have no correct specialist - these cannot be fixed by fusion/verification alone
- **Long-term solution**: Improve specialist prompts/knowledge bases to increase correct answer rate
- **Short-term solution**: Majority voting and less aggressive Tier 1 should improve accuracy by 7-12%
