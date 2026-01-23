# Tier 2 Investigation Summary

## Investigation Complete ✅

We investigated the 4 divergent questions where Tier 1 was correct but Full Linear was wrong.

---

## Key Findings

### 1. **Tier 2 GP Validation is Too Conservative**

**Problem**: The GP prompt instructs the LLM to:
- "BE CRITICAL"
- "Only APPROVE if you're confident this is the best answer"
- "Use NEEDS_REVIEW if there are any doubts or alternatives"
- "REJECT if you find significant errors or much better alternatives"

**Result**: GP is rejecting correct answers because it's being too strict and looking for "better alternatives" that don't exist.

**Evidence**:
- Question 15: Respiratory specialist (CORRECT answer A) → **REJECTED** → G Score = 0.120
- Question 17: Respiratory specialist (closer to correct) → **REJECTED** → G Score = 0.030
- Wrong answers from other specialists → **NEEDS_REVIEW** → G Score = 0.250-0.350 (higher!)

### 2. **Confidence-Weighted Voting Amplifies the Problem**

**How it works**:
- Each specialist's answer gets weighted by their final confidence
- Final answer = answer with highest total weighted votes

**What happened**:
1. Respiratory specialist (correct) → Tier 2 rejects → confidence drops from 0.300 to 0.160-0.210
2. Other specialists (wrong) → Tier 2 gives NEEDS_REVIEW → confidence stays at 0.275-0.325
3. Wrong answer wins because it has higher total confidence!

**Example (Question 15)**:
- Respiratory (A - correct): 0.210 confidence
- Cardiology (C - wrong): 0.275 confidence
- Neurology (C - wrong): 0.210 confidence
- Gastroenterology (C - wrong): 0.275 confidence
- **Total: A = 0.210, C = 0.760 → C wins!**

### 3. **Non-Deterministic LLM Behavior (Single-Specialist)**

**Problem**: Same question → different answers across Tier 1 vs Full Linear runs.

**Cause**: 
- Specialist agent uses `temperature=0.3` and `do_sample=True`
- LLM generates different answers each time
- This is NOT a Tier 2 issue, but a reproducibility issue

**Evidence**:
- Question 26: Tier 1 = "Mucosal tear" (correct), Full Linear = "Transmural tear" (wrong)
- Question ABG: Tier 1 = "Mixed acidosis" (correct), Full Linear = "Metabolic alkalosis" (wrong)

---

## Root Cause Analysis

### Why Tier 2 is Rejecting Correct Answers

1. **GP Prompt is Too Strict**
   - Instructs GP to "BE CRITICAL" and look for "better alternatives"
   - GP doesn't know the correct answer, so it guesses
   - Sometimes guesses wrong and rejects the correct answer

2. **GP Doesn't Have Full Context**
   - GP only sees: question, specialist answer, specialist reasoning, Tier 1 result
   - GP doesn't see: all answer options, other specialists' answers
   - GP might think there's a "better alternative" that doesn't exist

3. **Penalty Factors Are Too Aggressive**
   - REJECTED: G_score *= 0.15 (85% penalty!)
   - NEEDS_REVIEW: G_score *= 0.5 (50% penalty)
   - Even if GP gives moderate confidence (0.5), REJECTED drops it to 0.075

4. **GP Validation Quality**
   - GP might not understand respiratory specialist's reasoning
   - GP might be biased against certain types of answers
   - GP might be making errors in medical judgment

---

## Solutions

### Solution 1: **Specialty Weighting** ✅ (Implemented)

**How it helps**:
- Respiratory specialist gets 2x weight in voting
- Even if Tier 2 rejects it (confidence = 0.210), weighted vote = 0.420
- Wrong answers (confidence = 0.275) × 0.5 weight = 0.1375
- **Correct answer wins!**

**Status**: Implemented, ready to test

### Solution 2: **Fix Tier 2 Prompt**

**Current prompt issues**:
- Too strict ("BE CRITICAL", "REJECT if better alternatives")
- Doesn't emphasize validating correctness
- Encourages rejection

**Proposed changes**:
- Remove "BE CRITICAL" language
- Focus on "Is this answer medically correct?" not "Are there better alternatives?"
- Emphasize validating correctness, not finding flaws
- Add context: show all answer options

**Action**: Update `TIER2_VALIDATION_PROMPT` in `src/agents/prompts.py`

### Solution 3: **Adjust Penalty Factors**

**Current**:
- REJECTED: 0.15 (85% penalty)
- NEEDS_REVIEW: 0.5 (50% penalty)

**Proposed**:
- REJECTED: 0.3-0.4 (less aggressive)
- NEEDS_REVIEW: 0.6-0.7 (less aggressive)

**Rationale**: GP might be wrong, so don't penalize so heavily

**Action**: Update `tier2_validation.py` line 109-111

### Solution 4: **Fix Non-Determinism**

**For single-specialist**:
- Option A: Use `temperature=0.0` for specialist (deterministic)
- Option B: Cache specialist answers and only re-run verification
- Option C: Use fixed random seed

**Action**: Update `specialist_agent.py` or implement caching

### Solution 5: **Improve GP Context**

**Add to GP prompt**:
- All answer options (so GP knows what alternatives exist)
- Other specialists' answers (for multi-specialist)
- Ground truth (for training, not inference)

**Action**: Update `get_verification_prompt()` to include options

---

## Recommended Next Steps

### Priority 1: Test Specialty Weighting (Quick Win)
1. Enable `USE_SPECIALTY_WEIGHTING = True`
2. Run 30-question test
3. Check if accuracy improves

**Expected**: +3-5% accuracy improvement for multi-specialist

### Priority 2: Fix Tier 2 Prompt (Medium Effort)
1. Update `TIER2_VALIDATION_PROMPT` to be less strict
2. Add answer options to GP context
3. Re-run 30-question test

**Expected**: Fewer incorrect rejections

### Priority 3: Adjust Penalty Factors (Easy)
1. Change REJECTED penalty from 0.15 to 0.3-0.4
2. Change NEEDS_REVIEW penalty from 0.5 to 0.6-0.7
3. Re-run 30-question test

**Expected**: Less aggressive confidence reduction

### Priority 4: Fix Non-Determinism (Easy)
1. Set `temperature=0.0` for specialist agent
2. Or implement answer caching
3. Re-run single-specialist configs

**Expected**: Consistent answers across runs

### Priority 5: Scale to 100 Questions (Thorough)
1. After fixes, run 100 questions
2. Get statistically reliable results
3. Finalize conclusions

---

## Expected Impact

### With Specialty Weighting Only:
- Multi-specialist accuracy: **+3-5%** (from 43.3% to 46-48%)
- Single-specialist: No change (not applicable)

### With All Fixes:
- Multi-specialist accuracy: **+5-8%** (from 43.3% to 48-51%)
- Single-specialist: **+2-3%** (from 46.7% to 48-49%)
- Better calibration (lower ECE)
- Better uncertainty discrimination (higher AUROC)

---

## Conclusion

**Tier 2 is hurting accuracy because:**
1. GP validation is too conservative (rejecting correct answers)
2. Confidence-weighted voting amplifies the problem
3. Non-deterministic LLM behavior causes inconsistency

**Solutions:**
1. ✅ **Specialty weighting** (implemented, ready to test)
2. ⏳ **Fix Tier 2 prompt** (less strict, more context)
3. ⏳ **Adjust penalty factors** (less aggressive)
4. ⏳ **Fix non-determinism** (temperature=0.0 or caching)

**Next Action**: Test specialty weighting first (quick win), then implement other fixes.
