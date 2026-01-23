# Tier 1 + Tier 2 Improvements Test Results (10 Questions)

## Summary

**Test Date**: 2026-01-15  
**Dataset**: 10 disagreement questions from `medqa_us_100q_high_disagreement.json`  
**Test Purpose**: Verify that Tier 1 correctness checking + Tier 2 improvements work together

## Metrics Comparison

| Configuration | Accuracy | ECE | AUROC |
|--------------|----------|-----|-------|
| **Baseline** | 50.0% | 0.209 | 0.460 |
| **Tier 1** | 50.0% | 0.366 | **0.680** |
| **Full Linear** | 50.0% | 0.330 | **0.680** |

## Key Findings

### ✅ **Positive Results**

1. **AUROC Improved Significantly** (Discrimination)
   - Baseline: 0.460 → Tier 1/Full Linear: **0.680** (+48% improvement)
   - This means the system is better at distinguishing correct vs incorrect answers
   - **This is a major success!**

2. **Tier 2 is Rejecting Wrong Answers** (in some cases)
   - Question 8: All specialists with wrong answer got REJECTED
   - Question 9: All specialists with wrong answer got REJECTED
   - This shows Tier 2 improvements are working in some cases

### ❌ **Critical Issues**

1. **Tier 1 Correctness Checking Still Not Working**
   - Wrong answers still getting high correctness scores (mean: **0.885**)
   - Only 0/2 wrong answers have correctness <0.4 (should be most/all)
   - The stricter prompt didn't help - LLM still says wrong answers are "CORRECT"

2. **Tier 2 Still Approving Wrong Answers**
   - 2 wrong answers got APPROVED by Tier 2
   - 0 wrong answers got REJECTED (in the analyzed subset)
   - Tier 2 is not being strict enough

3. **ECE Got Worse** (Calibration Degraded)
   - Tier 1: 0.209 → 0.366 (+75% worse)
   - Full Linear: 0.209 → 0.330 (+58% worse)
   - Confidence scores are less calibrated (less reliable)

4. **Accuracy Unchanged**
   - All configurations: 50.0%
   - Verification is not improving accuracy

## Detailed Analysis

### Tier 1 Status on Wrong Answers

**Question 5** (Wrong: "Psychomotor epilepsy" → Correct: "Neuroblastoma"):
- GP: Tier 1=NO, Correctness=0.880, S=0.370 ✅ (caught it)
- Neurology: Tier 1=YES, Correctness=0.880, S=0.827 ❌ (missed it)

**Question 6** (Wrong: "Alpha toxin" → Correct: "Toxic shock syndrome toxin 1"):
- All specialists: Tier 1=YES, Correctness=0.880-0.900 ❌ (all missed it)

**Problem**: Correctness scores are 0.880-0.900 for wrong answers. The LLM is saying they're "CORRECT" when they're not.

### Tier 2 Status on Wrong Answers

**Question 5**:
- GP: Tier 2=NEEDS_REVIEW, G=0.420 ✅ (caught it)
- Neurology: Tier 2=REJECTED, G=0.120 ✅ (caught it)

**Question 6**:
- GP: Tier 2=REJECTED, G=0.080 ✅ (caught it)
- Respiratory: Tier 2=APPROVED, G=0.900 ❌ (missed it)
- Neurology: Tier 2=APPROVED, G=0.900 ❌ (missed it)

**Problem**: Tier 2 is approving wrong answers even when Tier 1 says they're correct (but Tier 1 correctness is wrong).

## Root Cause Analysis

### Why Tier 1 Correctness Checking Fails

1. **LLM Evaluates Reasoning Quality, Not Medical Correctness**
   - The LLM sees well-reasoned explanations and marks them as "CORRECT"
   - It doesn't actually verify if the answer is medically accurate
   - Wrong answers can have excellent reasoning but still be incorrect

2. **No Ground Truth Available**
   - During inference, we don't know the correct answer
   - The LLM must evaluate correctness without reference
   - This is inherently difficult

3. **Prompt May Still Be Too Lenient**
   - Even with stricter prompt, LLM defaults to "CORRECT"
   - Need more explicit instructions to be skeptical

### Why Tier 2 Still Approves Wrong Answers

1. **Tier 1 Says Answer is Correct** (incorrectly)
   - Tier 1 correctness = 0.880 → Tier 2 doesn't apply aggressive penalty
   - Tier 2 trusts Tier 1's assessment

2. **Tier 2 Prompt May Need More Explicit Instructions**
   - Need to explicitly tell Tier 2 to compare against ALL options
   - Need to tell Tier 2 to be more skeptical when Tier 1 correctness is high but answer seems wrong

## Recommendations

### Immediate Fixes

1. **Make Tier 1 Correctness Checker More Aggressive**
   - Add explicit instruction: "If you are uncertain, mark as INCORRECT"
   - Add instruction: "Compare against ALL options - if another option is clearly better, mark as INCORRECT"
   - Lower the threshold for "CORRECT" status (require higher confidence)

2. **Make Tier 2 More Skeptical**
   - Even if Tier 1 says answer is correct, Tier 2 should still validate independently
   - Add explicit instruction: "Do not trust Tier 1's correctness assessment - validate independently"
   - Require Tier 2 to explicitly compare against all options

3. **Fix ECE Degradation**
   - The confidence scores are becoming less calibrated
   - May need to adjust temperature scaling or confidence capping
   - Or adjust penalty factors to preserve calibration

### Alternative Approach

**Consider Using Ensemble Voting for Correctness**:
- Instead of single LLM call, use multiple LLM calls and take majority vote
- Or use a different model/approach for correctness checking
- Or use a rule-based approach combined with LLM

## Conclusion

**Mixed Results**:
- ✅ **AUROC improved significantly** (discrimination working)
- ❌ **Tier 1 correctness checking still not working** (wrong answers get high scores)
- ❌ **Tier 2 still approving wrong answers** (needs to be more skeptical)
- ❌ **ECE got worse** (calibration degraded)
- ❌ **Accuracy unchanged** (verification not improving accuracy)

**Next Steps**:
1. Make Tier 1 correctness checker more aggressive (explicit "if uncertain, mark INCORRECT")
2. Make Tier 2 more independent (don't trust Tier 1's correctness assessment)
3. Investigate ECE degradation (may need to adjust confidence calibration)

The improvements are partially working (AUROC), but correctness checking needs to be more aggressive.
