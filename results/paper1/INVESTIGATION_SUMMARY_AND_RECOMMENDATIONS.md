# Investigation Summary and Recommendations

## Date: January 22, 2025

---

## Executive Summary

**Results After Fixes**: 
- ✅ Accuracy improved slightly: **60.0% → 63.3%** (+1 question)
- ❌ ECE worsened: **0.699 → 0.756** (+0.057)
- ❌ AUROC worsened: **0.590 → 0.395** (-0.195)

**Key Finding**: The fixes helped with targeted questions (Q3, Q8, Q26) but introduced new problems:
1. **GP fallback overused** (19/30 questions, up from 14)
2. **S_score discrimination worsened** (gap 0.047 → 0.015)
3. **Two questions got worse** (Q10, Q13)

---

## 1. What Happened

### 1.1 Questions That Improved (3)
- **Q3**: Fixed! Was using "strong_yes_shortcut" (wrong B), now uses GP fallback (correct A)
- **Q8**: Fixed! Was using "max_s_override_majority" (wrong D), now uses GP fallback (correct C)
- **Q26**: Fixed! Was using "max_s_no_majority" (wrong B), now uses GP fallback (correct D)

**Root Cause Fixed**: The "strong_yes_shortcut" and overly permissive "max_s_override_majority" were causing wrong answers.

### 1.2 Questions That Got Worse (2)
- **Q10**: Was correct (B), now wrong (C) - Cardiology's verified wrong answer overrides correct majority
- **Q13**: Was correct (A), now wrong (B) - All specialists gave wrong answers, but wrong B chosen

### 1.3 Critical Issues
1. **GP fallback overused**: 19/30 questions (63%), up from 14/30 (47%)
2. **S_score discrimination worsened**: Gap decreased from 0.047 to 0.015
3. **Fusion logic not leveraging S_scores effectively**: Too many cases falling back to GP

---

## 2. Root Cause Analysis

### 2.1 Why Is GP Fallback Overused?

**Current Logic** (line 199 in `run_final_comparison.py`):
```python
elif gp_spec and gp_s_score >= 0.65:
    final_answer = gp_spec['answer']
    final_confidence = max(gp_confidence, gp_s_score)
    fusion_reason = "gp_fallback"
```

**Problem**: 
- Threshold is too low (0.65)
- No requirement for verified_status='YES'
- Being used as default when no other fusion rule applies
- GP might not actually be the best choice in those 19 cases

**Analysis**: Looking at Q3, Q8, Q26 - they all use GP fallback now. But:
- Q3: GP has S_score 0.825, verified_status='UNCERTAIN' - is this good enough?
- Q8: GP has S_score 0.700, verified_status='NO' - is this good enough?
- Q26: GP has S_score 0.950, verified_status='YES' - this is good!

**Conclusion**: GP fallback is being used even when GP doesn't have strong verification signals.

### 2.2 Why Did S_score Discrimination Worsen?

**Before**: 
- Correct: Mean=0.867, Wrong: Mean=0.819, Gap=0.047

**After**:
- Correct: Mean=0.876, Wrong: Mean=0.861, Gap=0.015

**Root Cause**: 
1. The fixes made the system more conservative (less wrong overrides)
2. But didn't improve the **quality** of the signals (S_scores, Two-Phase Verification)
3. Both correct and wrong answers are getting similar S_scores
4. This explains why AUROC dropped (0.590 → 0.395)

**The Real Problem**: The S_score formula itself doesn't discriminate well. We need to:
- Improve the S_score formula
- Apply calibration
- Make Two-Phase Verification stricter

### 2.3 Why Are Verified Answers Still Wrong?

**Q10 Example**: Cardiology got verified_status='YES' (inconsistency=0.0) for **wrong answer C**, and it's overriding the correct majority (B).

**Root Cause**: 
- Two-Phase Verification is giving YES to wrong answers (consistency ≠ correctness)
- The "max_s_override_majority" fix (gap 0.10, requires verified) is still allowing wrong verified answers to override

**Solution Needed**: Even with verified_status='YES', we need:
- Larger gap requirement (0.15+ instead of 0.10)
- OR require at least 2 verified specialists agreeing
- OR add medical plausibility check

---

## 3. What We Need to Do

### Option A: Investigate First (Recommended)

**Why**: We need to understand:
1. **Why is GP fallback being overused?** - Is GP actually the best choice in those 19 cases?
2. **Why did S_score discrimination worsen?** - Is it the formula, Two-Phase thresholds, or fusion logic?
3. **Why are verified answers still wrong?** - Is Two-Phase Verification fundamentally flawed?

**Actions**:
1. **Analyze the 19 GP fallback cases**:
   - Are they correct?
   - What are GP's S_scores and verified_status?
   - Why is GP being chosen over other specialists?
   
2. **Analyze S_score distribution**:
   - Compare S_scores for correct vs wrong answers
   - Check if Two-Phase Verification is providing good signals
   - Identify why discrimination is getting worse

3. **Analyze verified answer cases**:
   - How many verified answers are wrong?
   - What are their inconsistency scores?
   - Why is Two-Phase Verification giving YES to wrong answers?

**Expected Outcome**: We'll understand the root causes and can make targeted fixes.

### Option B: Implement Improvements Directly

**Actions**:
1. **Improve S_score discrimination**:
   - Test hybrid formula: `S = 0.7 * initial + 0.3 * verification * (1 - inconsistency)^2`
   - Apply calibration (temperature scaling)
   - Stricter Two-Phase thresholds (YES only if inconsistency < 0.10 AND initial confidence > 0.8)

2. **Fix GP fallback**:
   - Increase threshold (0.65 → 0.75)
   - Require verified_status='YES' or 'UNCERTAIN'
   - Only use if GP is clearly better than other specialists

3. **Fix verified answer override**:
   - Require larger gap (0.15+ instead of 0.10)
   - Require at least 2 verified specialists agreeing
   - Add medical plausibility check

4. **Improve specialist agents**:
   - Better prompts (more explicit medical reasoning)
   - Higher temperature (0.3 → 0.4-0.5)
   - Chain-of-thought reasoning

**Risk**: We might be fixing symptoms without understanding the root causes.

---

## 4. Recommendation

**I recommend Option A: Investigate First**

**Reasoning**:
1. **We've been making fixes without understanding root causes** - This is why results are getting worse
2. **GP fallback overuse is suspicious** - 19/30 cases suggests something is wrong with fusion logic
3. **S_score discrimination worsening** - This is the core problem, we need to understand why
4. **Verified answers still wrong** - Two-Phase Verification might be fundamentally flawed for our use case

**Investigation Plan**:
1. **Create analysis script** to investigate:
   - GP fallback cases (19 questions)
   - S_score distribution (correct vs wrong)
   - Verified answer accuracy (how many verified answers are wrong?)
   - Fusion reason effectiveness (which fusion reasons lead to correct answers?)

2. **Analyze results** to identify:
   - Why GP fallback is being overused
   - Why S_score discrimination is worsening
   - Why verified answers are still wrong
   - What fusion logic actually works

3. **Make targeted fixes** based on investigation results

**Expected Timeline**: 
- Investigation: 1-2 hours
- Analysis: 30 minutes
- Targeted fixes: 1-2 hours
- Testing: 1.5-2 hours

**Total**: ~4-5 hours

---

## 5. Alternative: Quick Fixes

If you want to try quick fixes first, I recommend:

1. **Fix GP fallback threshold** (5 minutes):
   - Increase from 0.65 to 0.75
   - Require verified_status='YES' or 'UNCERTAIN'

2. **Fix verified answer override** (10 minutes):
   - Increase gap from 0.10 to 0.15
   - Require at least 2 verified specialists agreeing

3. **Test** (1.5-2 hours)

**Risk**: These might not address the root causes, but they're quick to try.

---

## 6. Conclusion

**Current Status**: 
- ✅ Fixed 3 targeted questions (Q3, Q8, Q26)
- ❌ But introduced new problems (GP overuse, worse discrimination)
- ❌ ECE and AUROC got worse

**Root Cause**: We're fixing symptoms (wrong fusion decisions) but not the disease (poor S_score discrimination, unreliable Two-Phase Verification).

**Recommendation**: **Investigate first** to understand root causes, then make targeted fixes.

**Your Decision**: Do you want to:
1. **Investigate first** (recommended) - Understand root causes, then fix
2. **Try quick fixes** - Fix GP fallback and verified override, then test
3. **Implement improvements directly** - Improve S_score formula, specialist agents, etc.

What would you like to do?
