# Analysis: Fixed Fusion Logic Results

## Executive Summary

**Results**: Accuracy improved slightly (60% → 63.3%), but **ECE and AUROC got worse**.

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Accuracy** | 60.0% | 63.3% | +3.3% ✅ |
| **ECE** | 0.699 | 0.756 | +0.057 ❌ |
| **AUROC** | 0.590 | 0.395 | -0.195 ❌ |

**Key Finding**: The fixes helped with the targeted questions (Q3, Q8, Q26), but introduced new problems:
1. **GP fallback overused** (19/30 questions, up from 14)
2. **S_score discrimination worsened** (gap 0.047 → 0.015)
3. **Two questions got worse** (Q10, Q13)

---

## 1. What Improved

### Questions That Got Better (3 questions)
- **Q3**: Fixed! Was using "strong_yes_shortcut" (Cardiology's wrong B), now uses GP fallback (correct A)
- **Q8**: Fixed! Was using "max_s_override_majority" (wrong D), now uses GP fallback (correct C)
- **Q26**: Fixed! Was using "max_s_no_majority" (wrong B), now uses GP fallback (correct D)

**Root Cause Fixed**: The "strong_yes_shortcut" and overly permissive "max_s_override_majority" were causing wrong answers. These fixes addressed that.

---

## 2. What Got Worse

### Questions That Got Worse (2 questions)
- **Q10**: Was correct (B) with "strong_yes_shortcut", now wrong (C) with "max_s_override_majority"
  - **Problem**: Cardiology got verified_status='YES' for wrong answer C, and now it's overriding the correct majority (B)
  - **Root Cause**: The "max_s_override_majority" fix is still allowing wrong verified answers to override
  
- **Q13**: Was correct (A) with "max_s_override_majority", now wrong (B) with "max_s_override_majority"
  - **Problem**: All specialists gave wrong answers, but Cardiology's wrong B (S_score 0.575) is being chosen
  - **Root Cause**: The correct answer A was not among any specialist's outputs

**Root Cause**: The fixes made the system too conservative in some cases, but not conservative enough in others.

---

## 3. Critical Issues Identified

### 3.1 GP Fallback Overused

**Before**: 14/30 questions (47%)
**After**: 19/30 questions (63%)

**Problem**: The system is falling back to GP too often, which suggests:
1. The fusion logic is not finding consensus
2. GP is being used as a default when fusion is uncertain
3. This might be masking the real fusion logic issues

**Analysis**: Looking at Q3, Q8, Q26 - they all use GP fallback now. But GP fallback should only be used when:
- GP has a solid Two-Phase score (S_score >= 0.65)
- Other specialists disagree

**Question**: Is GP fallback being used correctly, or is it being used as a default?

### 3.2 S_score Discrimination Worsened

**Before**: 
- Correct: Mean=0.867, Wrong: Mean=0.819, Gap=0.047

**After**:
- Correct: Mean=0.876, Wrong: Mean=0.861, Gap=0.015

**Problem**: The discrimination gap **decreased** from 0.047 to 0.015 (worse!). This means:
- S_scores are becoming less useful for distinguishing correct vs wrong answers
- Both correct and wrong answers are getting similar S_scores
- This explains why AUROC dropped (0.590 → 0.395)

**Root Cause**: The fixes are not improving S_score discrimination - they're making it worse. This suggests:
1. The S_score formula itself needs improvement
2. Two-Phase Verification is not providing good signals
3. The fusion logic changes are not leveraging S_scores effectively

### 3.3 Fusion Reason Distribution Changed

**Before**:
- `strong_yes_shortcut`: 6 cases (20%)
- `max_s_override_majority`: 9 cases (30%)
- `gp_fallback`: 14 cases (47%)

**After**:
- `gp_fallback`: 19 cases (63%) ⬆️
- `max_s_override_majority`: 5 cases (17%) ⬇️
- `verified_consensus`: 2 cases (7%) NEW
- `verified_disagreement_best`: 2 cases (7%) NEW
- `max_s_yield_to_majority`: 2 cases (7%) NEW

**Analysis**: 
- `strong_yes_shortcut` is gone (good - we removed it)
- `max_s_override_majority` decreased (good - we made it stricter)
- But `gp_fallback` increased significantly (bad - suggests fusion is failing)

---

## 4. Root Cause Analysis

### 4.1 Why Did Accuracy Improve Slightly?

**Answer**: The fixes worked for the 3 targeted questions (Q3, Q8, Q26), but 2 other questions got worse (Q10, Q13).

**Net Result**: +3 improved, -2 worsened = +1 net improvement (60% → 63.3%)

### 4.2 Why Did ECE and AUROC Get Worse?

**Answer**: 
1. **S_score discrimination worsened** (gap 0.047 → 0.015)
2. **GP fallback overused** (19/30 cases) - GP might not have good S_scores
3. **Fusion logic not leveraging S_scores effectively** - too many cases falling back to GP

**Root Cause**: The fixes made the system more conservative (less wrong overrides), but didn't improve the **quality** of the signals (S_scores, Two-Phase Verification). The system is now avoiding bad decisions, but not making better decisions.

### 4.3 Why Is GP Fallback Being Overused?

**Possible Reasons**:
1. **Fusion logic is too conservative** - when specialists disagree, it falls back to GP
2. **GP threshold too low** - S_score >= 0.65 might be too permissive
3. **GP is being used as default** - when no other fusion rule applies, it uses GP

**Analysis Needed**: Check if GP fallback is being used correctly or if it's a default fallback.

---

## 5. What We Need to Do

### 5.1 Investigate GP Fallback Usage

**Action**: Analyze when GP fallback is being used and why:
- Is GP actually the best choice in those 19 cases?
- Is GP fallback being used as a default when fusion is uncertain?
- Should we require GP to have verified_status='YES' before using it?

### 5.2 Improve S_score Discrimination

**Problem**: S_score discrimination is getting worse, not better.

**Options**:
1. **Improve S_score formula** - Test hybrid formula, apply calibration
2. **Stricter Two-Phase thresholds** - Make verified_status='YES' harder to get
3. **Better inconsistency penalties** - Penalize wrong but consistent answers more

### 5.3 Fix "max_s_override_majority" for Verified Answers

**Problem**: Q10 shows that verified_status='YES' answers can still be wrong and override correct majorities.

**Solution**: Even with verified_status='YES', require:
- Larger gap (0.15+ instead of 0.10)
- OR require at least 2 verified specialists agreeing
- OR add medical plausibility check

### 5.4 Improve Specialist Agents

**Problem**: Q13 shows that all specialists gave wrong answers.

**Solution**: 
- Better prompts
- Higher temperature (0.3 → 0.4-0.5)
- Chain-of-thought reasoning

---

## 6. Recommendations

### Priority 1: Investigate GP Fallback
1. **Analyze the 19 GP fallback cases** - Are they correct? Why is GP being chosen?
2. **Check GP S_scores** - Are they actually good (>= 0.65)?
3. **Require GP verification** - Should GP also need verified_status='YES'?

### Priority 2: Improve S_score Discrimination
1. **Test hybrid S_score formula** - `S = 0.7 * initial + 0.3 * verification * (1 - inconsistency)^2`
2. **Apply calibration** - Temperature scaling to S_scores
3. **Stricter Two-Phase thresholds** - YES only if inconsistency < 0.10 AND initial confidence > 0.8

### Priority 3: Fix Verified Answer Override
1. **Require larger gap** - 0.15+ instead of 0.10 for verified overrides
2. **Require consensus** - At least 2 verified specialists agreeing
3. **Add validation** - Medical plausibility check before override

### Priority 4: Improve Specialist Agents
1. **Better prompts** - More explicit medical reasoning instructions
2. **Higher temperature** - 0.3 → 0.4-0.5 for more exploration
3. **Chain-of-thought** - Require explicit reasoning before answer

---

## 7. Conclusion

**What Worked**:
- ✅ Fixed the 3 targeted questions (Q3, Q8, Q26)
- ✅ Removed "strong_yes_shortcut" (no longer trusting single verified answers)
- ✅ Made "max_s_override_majority" stricter

**What Didn't Work**:
- ❌ S_score discrimination worsened (gap 0.047 → 0.015)
- ❌ GP fallback overused (14 → 19 cases)
- ❌ ECE and AUROC got worse
- ❌ 2 questions got worse (Q10, Q13)

**Root Cause**: The fixes addressed the **symptoms** (wrong fusion decisions) but not the **disease** (poor S_score discrimination, unreliable Two-Phase Verification).

**Next Steps**: 
1. **Investigate GP fallback** - Why is it being overused?
2. **Improve S_score discrimination** - This is the core problem
3. **Fix verified answer override** - Still allowing wrong verified answers
4. **Improve specialist agents** - Many questions have no correct specialist answer

**Target**: Get Multi-Agent + Two-Phase Verification to **70%+ accuracy** and **AUROC 0.6-0.7**.
