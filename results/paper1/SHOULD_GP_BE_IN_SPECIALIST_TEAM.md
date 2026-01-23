# Should GP Be Included in Specialist Team? Critical Analysis

## Date: January 22, 2025

---

## Key Question

**Do we need to include GP among specialists? Why did we do that? Did Wu et al. paper include GP in their specialist agents?**

---

## 1. What Wu et al. 2024 Actually Did

### Wu et al. 2024: "Uncertainty Estimation of Large Language Models in Medical Question Answering"

**Key Finding**: **Wu et al. did NOT use specialist agents at all!**

**Their Method**:
- Applied Two-Phase Verification to a **single LLM model** (not multi-agent)
- No specialist agents mentioned
- No GP mentioned
- Just: Single model → Two-Phase Verification → Uncertainty score

**Our Implementation**:
- We're combining **Wang et al. 2024** (multi-specialist agents) + **Wu et al. 2024** (Two-Phase Verification)
- This is a **novel combination** - Wu et al. didn't do multi-agent

**Conclusion**: Wu et al. paper is **not relevant** to the GP question - they didn't use specialist agents.

---

## 2. What Wang et al. 2024 Did

### Wang et al. 2024: "Beyond Direct Diagnosis: LLM-based Multi-Specialist Agent Consultation"

**Their Multi-Specialist Team**:
- Pulmonologist
- Internist
- General Surgeon
- Emergency Medicine
- **NO GP in specialist team**

**GP Role in Wang et al.**:
- Mentioned in narrative (real-world workflows)
- **NOT included as a specialist agent**
- Used for triage/initial assessment (not in architecture)

**Conclusion**: Wang et al. did **NOT include GP** in their specialist team.

---

## 3. Why We Added GP to Specialist Team

### History

**Original Decision (Jan 17)**: Remove GP from specialist team (to match Wang et al.)

**Later Decision (Jan 19)**: **Add GP back** as 5th specialist

**Reason**: Analysis showed GP got Questions 3, 9, 27 correct when **none** of the domain specialists did.

**Rationale**:
1. GP has broader knowledge across all specialties
2. When domain specialists all agree on wrong answer, GP can provide correct alternative
3. Matches real-world: GP often makes initial diagnosis before specialist referral

**Implementation**:
```python
multi_specialties = [
    "respiratory",
    "cardiology", 
    "neurology",
    "gastroenterology",
    "general practitioner"  # GP added as 5th specialist
]
```

---

## 4. Current Problem: GP Fallback Overused

### Issue Identified

**From Latest Results**:
- GP fallback used in **19/30 questions (63%)**
- Up from 14/30 (47%) before fixes
- This is suspicious - suggests fusion logic is failing

**Why GP Fallback is Being Overused**:
1. **GP is always available** (it's in the specialist team)
2. **Fusion logic falls back to GP** when no other rule applies
3. **GP threshold too low** (S_score >= 0.65)
4. **GP might not actually be best choice** in those 19 cases

**Current GP Fallback Logic** (line 199 in `run_final_comparison.py`):
```python
elif gp_spec and gp_s_score >= 0.65:
    final_answer = gp_spec['answer']
    final_confidence = max(gp_confidence, gp_s_score)
    fusion_reason = "gp_fallback"
```

**Problem**: This is being triggered too often, possibly because:
- GP is in the specialist team, so it's always available
- Threshold (0.65) is too low
- No requirement for verified_status='YES'

---

## 5. Should We Remove GP from Specialist Team?

### Option A: Remove GP (Match Wang et al.)

**Pros**:
1. ✅ **Matches Wang et al. 2024** - Same architecture
2. ✅ **Clear role separation** - Specialists diagnose, GP validates (if we use Tier 2)
3. ✅ **Focused expertise** - Domain specialists only
4. ✅ **Better comparison** - Easier to compare with literature
5. ✅ **Fixes GP fallback overuse** - GP won't be available for fallback
6. ✅ **Simpler fusion logic** - One less specialist to consider

**Cons**:
1. ❌ **Loses GP's broader knowledge** - GP got Q3, 9, 27 right when domain specialists didn't
2. ❌ **Might reduce accuracy** - If GP was helping in those cases
3. ❌ **Less realistic** - In real practice, GP often participates in consultations

### Option B: Keep GP but Fix Fallback Logic

**Pros**:
1. ✅ **Keeps GP's broader knowledge** - Still available when domain specialists fail
2. ✅ **More realistic** - Matches real-world practice
3. ✅ **Fixes overuse** - Stricter fallback logic prevents abuse

**Cons**:
1. ❌ **Doesn't match Wang et al.** - Different architecture
2. ❌ **Still complex** - GP in team + GP fallback logic
3. ❌ **Role confusion** - GP is both specialist and fallback

### Option C: Remove GP and Improve Domain Specialists

**Pros**:
1. ✅ **Matches Wang et al.** - Same architecture
2. ✅ **Fixes root cause** - Improve domain specialists instead of adding GP
3. ✅ **Better long-term** - Domain specialists should be able to handle these cases

**Cons**:
1. ❌ **Takes time** - Need to improve prompts, temperature, etc.
2. ❌ **Might not work** - Domain specialists might be fundamentally limited

---

## 6. Recommendation

### **I Recommend: Remove GP from Specialist Team (Option A)**

**Reasoning**:

1. **GP Fallback Overuse is a Problem**:
   - 19/30 questions using GP fallback suggests fusion logic is broken
   - GP being in the team makes it too easy to fall back to GP
   - This might be masking real fusion logic issues

2. **Matches Literature**:
   - Wang et al. 2024 doesn't include GP in specialist team
   - Our contribution is Two-Phase Verification, not GP inclusion
   - Better to match existing work for comparison

3. **Simpler Architecture**:
   - 4 specialists instead of 5
   - No GP fallback logic needed
   - Clearer fusion logic

4. **Fixes Current Issues**:
   - GP fallback overuse will disappear (GP won't be available)
   - Forces fusion logic to work with domain specialists only
   - Might reveal if fusion logic is the real problem

5. **GP Can Still Help**:
   - If we use Tier 2, GP can validate specialist diagnoses
   - But GP shouldn't be competing with specialists

**Expected Impact**:
- **Short-term**: Might reduce accuracy slightly (lose GP's help on Q3, 9, 27)
- **Long-term**: Forces us to fix fusion logic and improve domain specialists
- **Better for research**: Matches literature, clearer contribution

---

## 7. Alternative: Test Both Configurations

**If you want to be thorough**:

1. **Run experiment WITHOUT GP** in specialist team
2. **Compare results** with current (GP included)
3. **Analyze**:
   - Does removing GP reduce accuracy?
   - Does it fix GP fallback overuse?
   - Does fusion logic work better with 4 specialists?

**Then decide** based on empirical results.

---

## 8. Conclusion

**Answer to Your Questions**:

1. **Do we need to include GP?** 
   - **No** - We added it to help with cases where domain specialists failed, but it's causing GP fallback overuse

2. **Why did we do that?**
   - Analysis showed GP got Q3, 9, 27 right when domain specialists didn't
   - We thought GP's broader knowledge would help

3. **Did Wu et al. include GP?**
   - **No** - Wu et al. didn't use specialist agents at all (just single model + Two-Phase Verification)
   - **Wang et al.** (multi-specialist) also didn't include GP in specialist team

**Recommendation**: **Remove GP from specialist team** to:
- Match literature (Wang et al.)
- Fix GP fallback overuse
- Simplify architecture
- Force fusion logic to work properly

**Next Step**: Test without GP and see if it helps or hurts.
