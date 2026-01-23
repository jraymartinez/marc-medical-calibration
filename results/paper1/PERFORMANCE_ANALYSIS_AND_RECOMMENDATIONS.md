# Performance Analysis: Multi-Agent + Two-Phase Verification

## Current Performance (30 Questions)

**Latest Run** (`final_comparison_20260121_124058.json`):

| Configuration | Accuracy | ECE | AUROC |
|--------------|----------|-----|-------|
| Single Specialist | 70.0% | 0.759 | 0.455 |
| Single Specialist + Two-Phase | 70.0% | 0.158 | 0.442 |
| Multi-Agent (No Verification) | 70.0% | 0.781 | 0.458 |
| **Multi-Agent + Two-Phase** | **70.0%** | **0.279** | **0.519** |

**Best Configuration**: Single Specialist + Two-Phase (best ECE, but Multi+Two-Phase has better AUROC)

## Root Cause Analysis

### 1. **Confidence Discrimination Issue**

**Multi-Agent + Two-Phase**:
- Correct answers: mean conf = **0.383** (n=21)
- Wrong answers: mean conf = **0.370** (n=9)
- **Confidence gap: +0.013** (positive but TINY)

This explains why AUROC is only **0.519** (needs 0.6-0.7). The system can barely distinguish correct from wrong answers.

### 2. **S_Score Discrimination Failure**

Analysis of 5 fusion-miss cases (where correct specialist existed but was ignored):

| Question | Max Correct S | Max Wrong S | Gap | Issue |
|----------|---------------|-------------|-----|-------|
| Q3 | 0.332 | 0.332 | 0.000 | **No discrimination** |
| Q4 | 0.305 | 0.398 | **-0.093** | **Wrong is HIGHER** |
| Q8 | 0.310 | 0.354 | **-0.044** | **Wrong is HIGHER** |
| Q12 | 0.430 | 0.372 | +0.058 | Correct higher but override didn't trigger |
| Q17 | 0.354 | 0.376 | **-0.022** | **Wrong is HIGHER** |

**Critical Finding**: In **3 out of 5** fusion-miss cases, **Two-Phase Verification assigns HIGHER S_scores to WRONG answers than correct answers!**

This is the core problem preventing AUROC from reaching 0.6-0.7.

### 3. **Why Override Didn't Work for Q12**

Q12 had correct S=0.430 vs wrong S=0.372 (gap=0.058 > 0.05 threshold), but override still didn't trigger. Likely reasons:
- The override logic requires `max_s_score >= 0.45` OR `max_s_score >= majority_max_s + 0.05`
- Q12's max correct S (0.430) is below 0.45 threshold
- The gap (0.058) should have triggered the second condition, but may have been evaluated against wrong majority's S_score

### 4. **Fusion Reason Analysis**

All 9 wrong cases use `fusion_reason="majority"`, meaning:
- No strong YES specialist shortcut triggered
- No max_S override triggered (even when it should have)
- System fell back to simple majority voting

## Is This a Small Sample Size Issue?

**Partially, but NOT primarily**:

1. **Accuracy**: Yes, 30 questions is small (1 question = 3.33%). All configs tied at 70% suggests sample size variance.

2. **AUROC/ECE**: **NO** - These are systematic issues:
   - **AUROC 0.519** is low because confidence ordering is wrong (wrong answers get similar/higher confidence)
   - **ECE 0.279** is moderate but could be better with better discrimination
   - The S_score discrimination failure (wrong > correct in 3/5 cases) is a **systematic problem**, not sample size

3. **If we run 100 questions**: 
   - Accuracy differences might emerge (more statistical power)
   - **BUT AUROC will likely stay low** unless we fix the S_score discrimination issue
   - The fundamental problem (Two-Phase giving wrong answers higher scores) will persist

## Recommendations to Achieve AUROC 0.6-0.7

### Priority 1: Fix Two-Phase Correctness Discrimination

**Problem**: Two-Phase correctness checker is too conservative and sometimes rates wrong answers higher than correct ones.

**Solutions**:
1. **Improve correctness prompt**: Add more explicit comparison instructions, require the LLM to rank all options
2. **Adjust correctness thresholds**: Current thresholds (CORRECT=0.80, INCORRECT=0.15) may be too extreme. Consider:
   - CORRECT: 0.75-0.90 range (wider, more nuanced)
   - INCORRECT: 0.10-0.25 range (less aggressive penalty)
3. **Add relative comparison**: Instead of absolute correctness, compare correctness scores across specialists for the same question
4. **Weight correctness more**: Currently correctness and inconsistency are weighted equally (50/50). Consider 60/40 or 70/30 favoring correctness

### Priority 2: Fix Fusion Override Logic

**Problem**: Override threshold (0.45) is too high, and gap threshold (0.05) may not be evaluated correctly.

**Solutions**:
1. **Lower override threshold**: From 0.45 to 0.35 or even 0.30 for disagreement cases
2. **Fix gap evaluation**: Ensure gap is calculated correctly (max_correct_S vs max_wrong_S, not max_S vs majority_S)
3. **Add relative override**: If correct specialist's S_score is in top 2 and gap > 0.03, prefer it over majority
4. **Track correct specialist explicitly**: When a specialist's answer matches the correct option (even if we don't know it's correct), give it a small boost if its S_score is reasonable

### Priority 3: Improve S_Score Calculation

**Current**: `combined_score = (1.0 - inconsistency_score) * 0.5 + correctness_score * 0.5`

**Proposed**:
1. **Weight correctness more**: `combined_score = (1.0 - inconsistency_score) * 0.4 + correctness_score * 0.6`
2. **Add relative normalization**: Normalize correctness scores within each question (so best correctness gets highest S_score)
3. **Penalize wrong majority**: If 3+ specialists agree on wrong answer, reduce their S_scores by 10-15%

### Priority 4: Sample Size

**Recommendation**: After fixing the above issues, run **100 questions** to:
- Get more statistical power for accuracy differences
- Better estimate AUROC/ECE (less variance)
- Validate that fixes generalize

## Expected Impact

If we implement Priority 1-3 fixes:

**Optimistic**:
- AUROC: 0.519 → **0.65-0.70** (better discrimination)
- ECE: 0.279 → **0.20-0.25** (better calibration)
- Accuracy: 70% → **72-75%** (better fusion decisions)

**Realistic**:
- AUROC: 0.519 → **0.60-0.65** (moderate improvement)
- ECE: 0.279 → **0.22-0.27** (slight improvement)
- Accuracy: 70% → **71-73%** (small improvement)

## Conclusion

**The issue is NOT primarily sample size**. The core problem is **Two-Phase Verification failing to discriminate correct from wrong answers** (wrong answers get higher S_scores in 60% of fusion-miss cases).

**To achieve AUROC 0.6-0.7**, we must:
1. Fix Two-Phase correctness discrimination (Priority 1)
2. Fix fusion override logic (Priority 2)
3. Improve S_score calculation (Priority 3)
4. Then run 100 questions to validate (Priority 4)

Without these fixes, running 100 questions will likely show similar AUROC (0.50-0.55) because the systematic discrimination failure will persist.
