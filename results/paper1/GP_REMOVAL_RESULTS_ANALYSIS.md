# GP Removal Results: Analysis

## Date: January 22, 2025

---

## Executive Summary

**Removing GP made things WORSE**:
- ✅ **S_score discrimination improved** (gap 0.015 → 0.048)
- ❌ **Accuracy decreased** (63.3% → 60.0%, -3.3%)
- ❌ **ECE worsened** (0.756 → 0.771)
- ✅ **AUROC improved** (0.395 → 0.604)

**Key Finding**: **GP was actually helping!** In 6 questions (Q3, Q8, Q9, Q12, Q21, Q26), GP had the correct answer when domain specialists didn't.

---

## 1. Overall Metrics Comparison

| Metric | With GP | Without GP | Change |
|--------|---------|------------|--------|
| **Accuracy** | 63.3% (19/30) | 60.0% (18/30) | **-3.3%** ❌ |
| **ECE** | 0.756 | 0.771 | **+0.015** ❌ |
| **AUROC** | 0.395 | 0.604 | **+0.209** ✅ |
| **S_score Gap** | 0.015 | 0.048 | **+0.033** ✅ |

**Net Result**: Accuracy decreased, but S_score discrimination and AUROC improved.

---

## 2. Questions That Changed

### Improved (Wrong → Correct): 5 questions
- Q6, Q7, Q10, Q13, Q28

### Worsened (Correct → Wrong): 6 questions
- **Q3, Q8, Q9, Q12, Q21, Q26** - All were correct with GP, wrong without GP

**Key Insight**: GP was helping in 6 questions where domain specialists failed!

---

## 3. Detailed Analysis of Worsened Questions

### Q3: "Increase in length constant"
- **With GP**: Correct (A) - GP had S_score 0.825, used gp_fallback
- **Without GP**: Wrong (B) - Gastroenterology had S_score 0.825 (wrong answer), used max_s_yield_to_majority
- **Problem**: Domain specialists all gave wrong answer B, only GP had correct A

### Q8: "Type III hypersensitivity"
- **With GP**: Correct (C) - GP had S_score 0.700, used gp_fallback
- **Without GP**: Wrong (D) - Respiratory had S_score 0.450 (wrong answer), used max_s_yield_to_majority
- **Problem**: Domain specialists gave wrong answers, GP had correct C

### Q9: "Decreased physiologic dead space"
- **With GP**: Correct (B) - GP had S_score 0.783, used gp_fallback
- **Without GP**: Wrong (C) - Neurology had S_score 1.000 with verified_status='YES' (but wrong answer!), used max_s_no_majority
- **Problem**: Neurology got verified_status='YES' for wrong answer C, GP had correct B

### Q12: "21-hydroxylase"
- **With GP**: Correct (C) - GP had S_score 0.950, used verified_consensus
- **Without GP**: Wrong (A) - Cardiology had S_score 0.875 (wrong answer), used max_s_yield_to_majority
- **Problem**: Domain specialists gave wrong answer A, GP had correct C

### Q21: "Urinary tract infection"
- **With GP**: Correct (A) - GP had S_score 0.950, used gp_fallback
- **Without GP**: Wrong (B) - Cardiology had S_score 0.825 (wrong answer), used max_s_no_majority
- **Problem**: Domain specialists gave wrong answers, GP had correct A

### Q26: "Shingles vaccine"
- **With GP**: Correct (D) - GP had S_score 0.950, used gp_fallback
- **Without GP**: Wrong (B) - Respiratory and Cardiology had S_score 0.825 (wrong answer), used max_s_no_majority
- **Problem**: Domain specialists gave wrong answer B, GP had correct D

**Pattern**: In all 6 cases, GP had the correct answer when domain specialists didn't!

---

## 4. Fusion Reason Changes

### With GP:
- `gp_fallback`: 19 cases (63%) ⬆️
- `max_s_override_majority`: 5 cases
- `max_s_yield_to_majority`: 2 cases
- `verified_consensus`: 2 cases

### Without GP:
- `max_s_yield_to_majority`: 15 cases (50%) ⬆️
- `max_s_override_majority`: 6 cases
- `max_s_no_majority`: 6 cases
- `verified_consensus`: 2 cases

**Key Finding**: Without GP, fusion logic falls back to majority voting (`max_s_yield_to_majority`), which is less effective.

---

## 5. S_score Discrimination

### With GP:
- Correct: Mean=0.876
- Wrong: Mean=0.861
- **Gap: 0.015** (very small)

### Without GP:
- Correct: Mean=0.869
- Wrong: Mean=0.821
- **Gap: 0.048** (better!)

**Key Finding**: Removing GP improved S_score discrimination (gap increased from 0.015 to 0.048). This explains why AUROC improved (0.395 → 0.604).

**Why?**: GP's S_scores were similar for both correct and wrong answers, diluting discrimination. Without GP, domain specialists' S_scores have better discrimination.

---

## 6. Root Cause Analysis

### Why Removing GP Made Things Worse

1. **GP Was Actually Helping**:
   - GP got 6 questions correct (Q3, Q8, Q9, Q12, Q21, Q26) when domain specialists didn't
   - GP's broader knowledge was valuable

2. **GP Fallback Was Overused**:
   - 19/30 questions used gp_fallback (63%)
   - This was masking fusion logic issues
   - But GP was often the correct choice!

3. **Fusion Logic Without GP**:
   - Falls back to majority voting (`max_s_yield_to_majority`)
   - Less effective than GP fallback
   - Domain specialists often agree on wrong answers

4. **S_score Discrimination Improved**:
   - Without GP, S_scores have better discrimination
   - But accuracy decreased because GP was helping

---

## 7. The Real Problem

**We have a conflict**:
- ✅ **GP helps accuracy** (got 6 questions right when domain specialists didn't)
- ❌ **GP hurts S_score discrimination** (dilutes the gap)
- ❌ **GP fallback overused** (19/30 cases)

**The Solution**: **Keep GP but fix GP fallback logic**:
1. **Stricter GP fallback threshold** (0.65 → 0.75)
2. **Require verified_status** ('YES' or 'UNCERTAIN')
3. **Only use GP when domain specialists disagree** (not as default)
4. **Check if GP is actually better** than domain specialists before using

---

## 8. Recommendations

### Option A: Add GP Back with Stricter Fallback Logic (Recommended)

**Changes**:
1. Add GP back to specialist team
2. Increase GP fallback threshold: 0.65 → 0.75
3. Require verified_status: 'YES' or 'UNCERTAIN'
4. Only use GP when domain specialists disagree (not as default)
5. Check if GP S_score is meaningfully better than domain specialists

**Expected Impact**:
- ✅ Keep GP's help on Q3, Q8, Q9, Q12, Q21, Q26
- ✅ Reduce GP fallback overuse (from 19/30 to ~10-12/30)
- ✅ Improve S_score discrimination (stricter GP usage)
- ✅ Better accuracy (63.3% → 65-67%)

### Option B: Keep GP Removed and Improve Domain Specialists

**Changes**:
1. Keep GP removed
2. Improve domain specialist prompts
3. Increase temperature (0.3 → 0.4-0.5)
4. Add chain-of-thought reasoning
5. Fix fusion logic to work better with 4 specialists

**Expected Impact**:
- ✅ Better S_score discrimination (already improved)
- ✅ Better AUROC (already improved)
- ⚠️ Need to improve domain specialists to get accuracy back to 63%+

### Option C: Hybrid Approach

**Changes**:
1. Keep GP in team but don't use GP fallback
2. Let GP participate in normal fusion logic (majority voting, S_score comparison)
3. GP is just another specialist, no special fallback

**Expected Impact**:
- ✅ GP helps when it has correct answer
- ✅ No GP fallback overuse
- ✅ GP participates in fusion like other specialists

---

## 9. Conclusion

**Key Findings**:
1. **GP was actually helping** - Got 6 questions right when domain specialists didn't
2. **GP fallback was overused** - 19/30 cases, but GP was often correct
3. **Removing GP hurt accuracy** - Lost 6 correct answers
4. **Removing GP helped S_score discrimination** - Gap improved from 0.015 to 0.048

**Recommendation**: **Add GP back with stricter fallback logic**:
- Keep GP's help on questions where domain specialists fail
- Reduce GP fallback overuse with stricter thresholds
- Improve S_score discrimination by using GP more selectively

**Next Step**: Implement Option A (GP back with stricter fallback logic) and test.
