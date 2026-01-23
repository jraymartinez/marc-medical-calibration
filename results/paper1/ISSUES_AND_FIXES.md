# Issues and Fixes for Final Comparison

## Date: 2026-01-17

## Critical Issues Found

### Issue 1: Fusion Method Picks Wrong Answers ❌

**Problem**: Confidence-weighted voting (summing) picks wrong answers when majority is wrong

**Example - Question 3**:
- Correct: "Increase in length constant" (A)
- Neurology: A (correct, conf: 0.9)
- Respiratory, Cardiology, Gastroenterology: B (wrong, conf: 0.9 each)
- **Current Fusion**: B wins (0.9 + 0.9 + 0.9 = 2.7 > 0.9)
- **Result**: Wrong answer selected

**Root Cause**: Simple summing doesn't account for correctness, just majority

### Issue 2: Multi-Agent < Single Specialist ❌

**Problem**: Multi-Agent (60%) < Single Specialist (70%)
- **Expected**: Multi-Agent should be better
- **Reality**: Multi-Agent loses 10% accuracy

**Root Cause**: Fusion method picks wrong answers when specialists disagree

### Issue 3: Single Specialist + Tier 1 Confidence Too Low ❌

**Problem**: Average confidence = 0.148 (unrealistically low)
- **Expected**: Reasonable confidence scores
- **Reality**: Tier 1 is too aggressive

**Impact**: ECE is good but confidence is too low

### Issue 4: Multi-Agent + Tier 1 ECE Worse ❌

**Problem**: ECE increased (0.663 → 0.668)
- **Expected**: Tier 1 should improve ECE
- **Reality**: Slight degradation

## Recommended Fixes

### Fix 1: Improve Fusion Method

**Current**: Sum confidences, pick highest sum
```python
answer_votes[answer] += confidence  # Sum
final_answer = max(answer_votes, key=answer_votes.get)  # Pick highest sum
```

**Problem**: Majority wins even if wrong

**Solution**: Use majority voting with tie-breaking by highest confidence
```python
# Count votes
vote_counts = Counter([s['answer'] for s in specialist_outputs])
most_common = vote_counts.most_common()

if most_common[0][1] > len(specialist_outputs) / 2:
    # Majority exists
    final_answer = most_common[0][0]
else:
    # No majority, use highest confidence
    final_answer = max(specialist_outputs, key=lambda x: x['confidence'])['answer']
```

**Alternative**: Use highest confidence selection (simpler)
```python
# Pick specialist with highest confidence
specialist_outputs.sort(key=lambda x: x['confidence'], reverse=True)
final_answer = specialist_outputs[0]['answer']
final_confidence = specialist_outputs[0]['confidence']
```

### Fix 2: Adjust Tier 1 Confidence Reduction

**Check**: Tier 1 adjustment factors might be too aggressive
- Single Specialist + Tier 1: avg conf = 0.148 (too low)
- Need to check Tier 1 penalties and temperature scaling

### Fix 3: Investigate AUROC = 0.500

**Problem**: AUROC = 0.500 (no discrimination)
- Might be confidence distribution issue
- Or all confidences are similar
- Need to check confidence distributions

## Next Steps

1. **Fix fusion method** - Use majority voting or highest confidence
2. **Check Tier 1 parameters** - Adjust if too aggressive
3. **Re-test** - Run experiment with fixes
