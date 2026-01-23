# Comprehensive Fix Plan: Question Selection + Verification Issues

## Date
2026-01-13

## Two Critical Issues to Address

### Issue 1: Question Selection
**Question**: Should we finalize 100 good questions or is random seed good enough?

### Issue 2: Verification Problems
**Problems**:
1. Verification too aggressive → All answers get similar confidence
2. Fusion method can't distinguish when confidences are equal
3. Most questions have specialist agreement → Verification can't help

---

## Issue 1: Question Selection Analysis

### Current Situation

**Random Seed 42**:
- ✅ Deterministic and reproducible
- ✅ Same questions each run
- ❓ But: Are these "good" questions?

**Question Quality Findings**:
- Baseline accuracy: 30.0% (lower than 30-Q run's 43.3%)
- Question length: Mean 372 characters (reasonable)
- Specialist agreement: 68% all agree, only 4% all disagree

### The Problem

**68% of questions have all specialists agreeing**:
- When all agree on correct answer → Verification maintains (doesn't improve)
- When all agree on wrong answer → Verification can't help
- **Only 4% have all disagreeing** → This is where verification should help!

### Recommendation: Curate Questions

**Option A: Filter for Disagreement Cases (Recommended)**
- Select questions where specialists disagree
- These are where verification can actually help
- More relevant for testing verification effectiveness

**Option B: Keep Random Seed (Current)**
- Reproducible but may not be optimal
- Many questions where verification can't help
- Lower baseline accuracy (30.0% vs 43.3%)

**Option C: Stratified Sampling**
- Sample by difficulty/type
- More representative
- But more complex

### My Recommendation: **Option A - Filter for Disagreement**

**Why**:
- Verification only helps when specialists disagree
- Current sample: Only 4% disagreement cases
- Need more disagreement cases to test verification

**How**:
1. Run baseline on all questions
2. Identify questions where specialists disagree
3. Select 100 questions with disagreement
4. Re-run experiments on curated set

---

## Issue 2: Verification Problems

### Problem 1: Verification Too Aggressive

**Current Behavior**:
- Tier 1: Most answers get "UNCERTAIN" → Confidence drops to ~0.30
- Tier 2: Even approved answers get penalized
- Result: All answers have similar confidence (0.30-0.50)

**Evidence from Q1**:
- All specialists: Different answers (A, B, D, C)
- After verification: All have confidence 0.360
- Can't distinguish which is correct!

### Fix 1: Less Aggressive Tier 1 Penalties

**Current**:
- NO: 0.1 (very harsh)
- UNCERTAIN: 0.4 (harsh)

**Proposed**:
- NO: 0.2 (less harsh)
- UNCERTAIN: 0.6 (less harsh)

**Rationale**: Preserve more distinction between answers

### Fix 2: Less Aggressive Tier 2 Penalties

**Current**:
- REJECTED: 0.5
- NEEDS_REVIEW: 0.75

**Proposed**:
- REJECTED: 0.6 (less harsh)
- NEEDS_REVIEW: 0.85 (less harsh)

**Rationale**: Preserve more confidence for approved answers

### Fix 3: Better Tier 1/Tier 2 Balance

**Current**: Tier 1 is too strict (most get UNCERTAIN)

**Proposed**: 
- Adjust Tier 1 prompt to be less critical
- Or adjust Tier 1 temperature (higher = less strict)

### Problem 2: Fusion Method Limitation

**Current Method**:
```python
specialist_outputs.sort(key=lambda x: x['confidence'], reverse=True)
final_answer = specialist_outputs[0]['answer']  # Picks first
```

**Problem**: When all have same confidence, picks first specialist (might be wrong)

### Fix 4: Improved Fusion Method

**Option A: Confidence-Weighted Voting (Recommended)**
```python
# Sum confidence per answer across specialists
answer_votes = {}
for spec in specialist_outputs:
    answer = spec['answer']
    if answer not in answer_votes:
        answer_votes[answer] = 0
    answer_votes[answer] += spec['confidence']

# Pick answer with highest total confidence
final_answer = max(answer_votes, key=answer_votes.get)
```

**Benefits**:
- Works even when individual confidences are similar
- Uses all specialist opinions
- More robust to ties

**Option B: Specialty-Weighted Voting**
- Give more weight to relevant specialists
- E.g., respiratory specialist for respiratory questions

**Option C: Majority Voting with Confidence Tie-Breaker**
- If majority exists, use it
- If tie, use confidence-weighted voting

---

## Comprehensive Fix Plan

### Phase 1: Fix Verification Issues (First)

**Priority**: HIGH - These are fundamental problems

**Steps**:
1. **Less Aggressive Tier 1 Penalties**:
   - NO: 0.1 → 0.2
   - UNCERTAIN: 0.4 → 0.6

2. **Less Aggressive Tier 2 Penalties**:
   - REJECTED: 0.5 → 0.6
   - NEEDS_REVIEW: 0.75 → 0.85

3. **Implement Confidence-Weighted Voting**:
   - Replace "highest confidence selection"
   - Use sum of confidences per answer

4. **Test on 100-Q sample**:
   - See if fixes improve accuracy
   - Compare to current results

**Time**: ~6 hours (one full run)

### Phase 2: Curate Questions (Second)

**Priority**: MEDIUM - Improves relevance but not fundamental

**Steps**:
1. **Identify Disagreement Cases**:
   - Run baseline on all questions
   - Find questions where specialists disagree
   - Select 100 questions with disagreement

2. **Re-run Experiments**:
   - Run with fixed verification
   - Compare to current results

**Time**: ~8 hours (baseline run + full experiment)

### Phase 3: Re-Tune Parameters (Third)

**Priority**: LOW - Only if Phase 1/2 show promise

**Steps**:
1. Quick re-tune on curated 100-Q
2. Test alpha = 0.6, 0.7
3. Compare to Tier 1

**Time**: ~4-6 hours

---

## Recommended Order

### **Fix Verification Issues FIRST** (Most Important)

**Why**:
- These are fundamental problems
- Fixing them might solve accuracy issue
- Can test on current 100-Q sample
- No need to curate questions first

**Steps**:
1. Implement less aggressive penalties
2. Implement confidence-weighted voting
3. Test on current 100-Q sample
4. If improvement → Continue
5. If no improvement → Then curate questions

### **Then Curate Questions** (If Needed)

**Why**:
- Only if verification fixes don't help
- More relevant for testing verification
- But adds complexity

---

## Implementation Plan

### Step 1: Fix Verification Aggressiveness

**Files to Modify**:
1. `src/verification/tier1_verification.py`:
   - NO: 0.1 → 0.2
   - UNCERTAIN: 0.4 → 0.6

2. `src/verification/tier2_validation.py`:
   - REJECTED: 0.5 → 0.6
   - NEEDS_REVIEW: 0.75 → 0.85

### Step 2: Fix Fusion Method

**File to Modify**:
- `scripts/run_optimized_multi_specialist.py`:
  - Replace "highest confidence selection"
  - Implement confidence-weighted voting

### Step 3: Test on 100-Q

**Run experiment with fixes**:
- Compare to current results
- See if accuracy improves
- See if calibration maintains

---

## Expected Outcomes

### With Fixes

**Best Case**:
- Accuracy improves (30.0% → 35-40%)
- Calibration maintains (ECE ~0.05-0.10)
- Full Linear becomes competitive with Tier 1

**Realistic Case**:
- Accuracy improves slightly (30.0% → 32-33%)
- Calibration maintains
- Tier 1 still best, but Full Linear closer

**Worst Case**:
- No accuracy improvement
- But at least we tried
- Can then curate questions

---

## Recommendation

### **YES, Fix Verification Issues First**

**Order**:
1. ✅ Fix verification aggressiveness (less harsh penalties)
2. ✅ Fix fusion method (confidence-weighted voting)
3. ✅ Test on current 100-Q sample
4. ⏳ If needed, then curate questions
5. ⏳ If promising, then re-tune parameters

**Why This Order**:
- Fixes fundamental problems first
- Can test immediately on current sample
- No need to curate questions first
- More efficient use of time

**Time Investment**:
- Fixes: ~1 hour (code changes)
- Testing: ~6 hours (one full run)
- **Total: ~7 hours** (much less than re-tuning)

---

## Conclusion

**Address both issues, but in order**:

1. **First**: Fix verification issues (aggressiveness + fusion method)
2. **Second**: Test on current 100-Q sample
3. **Third**: If needed, curate questions for disagreement cases
4. **Fourth**: If promising, re-tune parameters

This approach is more efficient and addresses root causes first.
