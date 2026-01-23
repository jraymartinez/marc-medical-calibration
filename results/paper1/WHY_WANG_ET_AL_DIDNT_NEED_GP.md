# Why Wang et al. Didn't Need GP But We Do

## Date: January 22, 2025

---

## Key Question

**Does it make sense to have GP in the team? Why did Wang et al. not use it but have good performance?**

---

## 1. What Wang et al. 2024 Actually Did

### Their Architecture

**Multi-Specialist Team**:
- Pulmonologist
- Internist
- General Surgeon
- Emergency Medicine
- **NO GP**

**Fusion Method**: **Adaptive Fusion (Self-Attention)**
- Learned fusion mechanism
- Automatically learns to weight specialists based on their performance
- Can adaptively handle disagreements
- More sophisticated than simple majority voting

**Model**: (Need to check, but likely GPT-4 or similar large model)

**Result**: Good performance without GP

---

## 2. What We're Doing

### Our Architecture

**Multi-Specialist Team**:
- Respiratory (Pulmonologist)
- Cardiology (Cardiologist)
- Neurology (Neurologist)
- Gastroenterology (Gastroenterologist)
- **GP (added later)** ❓

**Fusion Method**: **Simple Fusion Logic**
- Majority voting
- Highest confidence selection
- S_score-based selection
- **NOT learned/adaptive**

**Model**: **Llama 3.1 8B** (smaller, less capable)

**Result**: Poor performance without GP (60% accuracy)

---

## 3. Why Wang et al. Didn't Need GP

### Reason 1: Better Fusion Method

**Wang et al.**: **Adaptive Fusion (Self-Attention)**
- Learned mechanism that adapts to specialist performance
- Can handle disagreements intelligently
- Automatically weights specialists based on their expertise for each case
- More sophisticated than simple rules

**Us**: **Simple Fusion Logic**
- Majority voting (3 wrong specialists beat 1 correct specialist)
- Highest confidence (can be wrong if specialist is overconfident)
- S_score-based (but S_scores have poor discrimination)
- **Rule-based, not learned**

**Impact**: Their fusion method can handle cases where domain specialists disagree, so they don't need GP as a fallback.

### Reason 2: Better Model (Likely)

**Wang et al.**: Likely used GPT-4 or similar large model
- Better medical knowledge
- Better reasoning
- Better specialist agents

**Us**: **Llama 3.1 8B**
- Smaller model
- Less medical knowledge
- Weaker specialist agents
- Domain specialists fail more often

**Impact**: Their domain specialists are better, so they don't need GP to compensate.

### Reason 3: Better Prompts/Knowledge Bases

**Wang et al.**: 
- Disease-specific knowledge bases
- Well-tuned prompts
- Specialist agents are more capable

**Us**:
- Basic knowledge bases
- Simple prompts
- Specialist agents struggle

**Impact**: Their domain specialists are more capable, so they don't need GP.

---

## 4. Why We Need GP

### The Real Problem

**We're using GP as a crutch** to compensate for:

1. **Weak Fusion Logic**:
   - Simple majority voting fails when 3 specialists agree on wrong answer
   - Highest confidence selection fails when wrong specialist is overconfident
   - S_score-based selection fails because S_scores have poor discrimination
   - **GP fallback** (19/30 cases) is masking these issues

2. **Weak Domain Specialists**:
   - Domain specialists fail on Q3, Q8, Q9, Q12, Q21, Q26
   - GP gets these right (broader knowledge)
   - **We need GP** because domain specialists aren't good enough

3. **Weak Model**:
   - Llama 3.1 8B might not have enough medical knowledge
   - Domain specialists struggle
   - **GP helps** because it has broader knowledge

---

## 5. Does It Make Sense to Have GP in the Team?

### Arguments FOR Including GP

1. **GP Actually Helps**:
   - Got 6 questions right when domain specialists didn't
   - Broader knowledge is valuable
   - Matches real-world (GP often participates in consultations)

2. **Our Domain Specialists Are Weak**:
   - They fail on many questions
   - GP compensates for their weaknesses
   - Without GP, accuracy drops (63.3% → 60.0%)

3. **Our Fusion Logic Is Weak**:
   - Simple rules don't work well
   - GP fallback helps when fusion logic fails
   - Without GP, fusion logic struggles more

### Arguments AGAINST Including GP

1. **Doesn't Match Literature**:
   - Wang et al. didn't use GP
   - Harder to compare results
   - Less aligned with existing work

2. **Masking Real Problems**:
   - GP fallback (19/30 cases) is masking fusion logic issues
   - We should fix fusion logic instead of adding GP
   - GP is a band-aid, not a solution

3. **Hurts S_score Discrimination**:
   - GP's S_scores dilute discrimination (gap 0.015 vs 0.048)
   - Without GP, S_score discrimination is better
   - But accuracy is worse

---

## 6. The Real Solution

### We Should NOT Need GP If We Fix Root Causes

**What We Should Do**:

1. **Improve Fusion Logic**:
   - Implement adaptive fusion (self-attention) like Wang et al.
   - OR improve our simple fusion logic to handle disagreements better
   - Fix majority voting to not always trust majority
   - Better S_score-based selection

2. **Improve Domain Specialists**:
   - Better prompts (more explicit medical reasoning)
   - Better knowledge bases (disease-specific, more detailed)
   - Higher temperature (0.3 → 0.4-0.5) for more exploration
   - Chain-of-thought reasoning

3. **Improve Model** (if possible):
   - Use larger model (Llama 3.1 70B if available)
   - OR fine-tune Llama 3.1 8B on medical data
   - OR use GPT-4 if budget allows

4. **Improve S_score Discrimination**:
   - Better S_score formula
   - Stricter Two-Phase Verification thresholds
   - Calibration

**If We Fix These**: We shouldn't need GP, just like Wang et al. didn't.

---

## 7. Recommendation

### Short-Term: Keep GP But Fix Fusion Logic

**Why**:
- GP is helping (6 questions correct)
- Removing GP hurts accuracy (63.3% → 60.0%)
- But we need to fix GP fallback overuse

**Action**:
1. Keep GP in team
2. Fix GP fallback logic (stricter thresholds, require verification)
3. Improve fusion logic to work better with 4 domain specialists
4. Reduce GP fallback from 19/30 to ~10-12/30

### Long-Term: Remove GP and Fix Root Causes

**Why**:
- Matches literature (Wang et al.)
- Forces us to fix real problems
- Better for research

**Action**:
1. Implement adaptive fusion (self-attention) like Wang et al.
2. Improve domain specialist prompts and knowledge bases
3. Improve S_score discrimination
4. Test without GP
5. If accuracy is still good, keep GP removed

---

## 8. Conclusion

**Why Wang et al. Didn't Need GP**:
1. ✅ **Better fusion method** (adaptive fusion/self-attention)
2. ✅ **Better model** (likely GPT-4 or similar)
3. ✅ **Better domain specialists** (better prompts/knowledge bases)

**Why We Need GP**:
1. ❌ **Weak fusion logic** (simple rules, not learned)
2. ❌ **Weak domain specialists** (Llama 3.1 8B, basic prompts)
3. ❌ **Weak model** (smaller, less capable)

**Does It Make Sense to Have GP?**:
- **Short-term**: Yes, because it helps (6 questions correct)
- **Long-term**: No, we should fix root causes instead

**The Real Solution**: 
- Fix fusion logic (implement adaptive fusion)
- Improve domain specialists (better prompts, knowledge bases)
- Improve model (if possible)
- Then we won't need GP, just like Wang et al.

**Next Steps**:
1. **Short-term**: Keep GP but fix GP fallback logic
2. **Long-term**: Implement adaptive fusion, improve specialists, then remove GP
