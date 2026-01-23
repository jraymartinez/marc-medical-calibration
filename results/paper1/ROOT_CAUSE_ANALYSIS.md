# Root Cause Analysis: Why Multi-Agent Underperforms

## Date: 2026-01-17

## Current Results

| Configuration | Accuracy | ECE | AUROC |
|--------------|----------|-----|-------|
| Single Specialist | 70.0% | 0.869 | 0.500 |
| Single Specialist + Tier 1 | 70.0% | 0.148 | 0.500 |
| Multi-Agent (No Verification) | 60.0% | 0.663 | 0.500 |
| Multi-Agent + Tier 1 | 63.3% | 0.668 | 0.500 |

## Critical Issues Identified

### Issue 1: Multi-Agent < Single Specialist ❌

**Problem**: Multi-Agent (60%) is WORSE than Single Specialist (70%)
- **Expected**: Multi-Agent should be better (more perspectives)
- **Reality**: Multi-Agent loses 10% accuracy

**Root Cause**: Fusion method picks wrong answers when majority is wrong

**Example - Question 3**:
- Correct Answer: "Increase in length constant" (A)
- Neurology: A (correct, conf: 0.900)
- Respiratory: B (wrong, conf: 0.900)
- Cardiology: B (wrong, conf: 0.900)
- Gastroenterology: B (wrong, conf: 0.900)
- **Fusion Result**: B (wrong) - 3 votes vs 1 vote

**Problem**: Simple confidence-weighted voting sums confidences:
- B: 0.9 + 0.9 + 0.9 = 2.7
- A: 0.9 = 0.9
- Winner: B (wrong!)

### Issue 2: Single Specialist + Tier 1 Has Very Low Confidence ❌

**Problem**: Average confidence = 0.148 (too low!)
- **Expected**: Reasonable confidence scores
- **Reality**: Tier 1 is too aggressive, reducing confidence too much

**Impact**: 
- ECE is good (0.148) but confidence is unrealistically low
- Might indicate Tier 1 penalties are too aggressive

### Issue 3: Multi-Agent + Tier 1 ECE Worse ❌

**Problem**: ECE increased from 0.663 → 0.668 (worse)
- **Expected**: Tier 1 should improve ECE
- **Reality**: Slight degradation

**Impact**: Calibration is worse with Tier 1

### Issue 4: AUROC = 0.500 for All ❌

**Problem**: AUROC is 0.500 (no discrimination)
- **Expected**: AUROC > 0.5 (better than random)
- **Reality**: No discrimination between correct/incorrect

**Possible Causes**:
- Confidence scores don't correlate with correctness
- All confidences are similar
- Calculation issue

## Root Causes

### 1. Fusion Method Issue

**Current Method**: Confidence-weighted voting (sum confidences)
```python
answer_votes[answer] += confidence  # Sum confidences
final_answer = max(answer_votes, key=answer_votes.get)  # Pick highest sum
```

**Problem**: 
- When 3 specialists agree on wrong answer, they win
- Doesn't consider that specialists might be wrong
- No mechanism to detect when majority is wrong

**Solution Options**:
1. **Majority voting with tie-breaking**: Require majority agreement
2. **Weighted voting with disagreement penalty**: Reduce confidence when specialists disagree
3. **Highest confidence selection**: Pick specialist with highest confidence (not sum)
4. **Consensus-based**: Require consensus or use highest confidence

### 2. Tier 1 Confidence Reduction Too Aggressive

**Problem**: Single Specialist + Tier 1 has avg confidence = 0.148
- Tier 1 penalties might be too aggressive
- Temperature scaling might be too aggressive
- Need to check Tier 1 adjustment factors

### 3. Multi-Agent Fusion Needs Improvement

**Problem**: Multi-agent fusion doesn't handle disagreements well
- When specialists disagree, fusion picks majority (even if wrong)
- Need better fusion strategy

## Recommended Fixes

### Fix 1: Improve Fusion Method

**Option A**: Use highest confidence selection (not sum)
```python
# Instead of summing, pick specialist with highest confidence
specialist_opinions.sort(key=lambda x: x['confidence'], reverse=True)
final_answer = specialist_opinions[0]['answer']
```

**Option B**: Require majority agreement
```python
# Count votes, require majority
vote_counts = Counter([s['answer'] for s in specialist_opinions])
if max(vote_counts.values()) >= len(specialist_opinions) / 2:
    final_answer = vote_counts.most_common(1)[0][0]
else:
    # No majority, use highest confidence
    final_answer = max(specialist_opinions, key=lambda x: x['confidence'])['answer']
```

### Fix 2: Adjust Tier 1 Confidence Reduction

**Check**: Tier 1 adjustment factors and temperature scaling
- Might be too aggressive for single specialist
- Need to balance between calibration and confidence

### Fix 3: Investigate AUROC Issue

**Check**: Why AUROC = 0.500 for all
- Might be confidence distribution issue
- Or calculation issue

## Next Steps

1. **Fix fusion method** - Use better strategy (highest confidence or majority)
2. **Adjust Tier 1 penalties** - Less aggressive for single specialist
3. **Investigate AUROC** - Check confidence distributions
4. **Re-test** - Run experiment again with fixes
