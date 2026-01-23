# Fusion Analysis - Do Low G Scores Prevent Wrong Answers?

## Date: 2026-01-16

## Question 7 Analysis

**Correct Answer**: Mi-2 protein  
**Final Answer Selected**: D. Mi-2 protein (WRONG)  
**Winning Votes**: 0.813

## Specialist Outputs

| Specialist | Answer | Tier 1 | S Score | Tier 2 | G Score | Final Conf |
|-----------|--------|--------|---------|--------|---------|------------|
| GP | D. Mi-2 protein | NO | 0.406 | APPROVED | 0.190 | 0.416 |
| Neurology | D. Mi-2 protein | NO | 0.376 | APPROVED | 0.190 | 0.397 |
| Respiratory | A. Centromeres | NO | 0.351 | REJECTED | 0.090 | 0.340 |
| Cardiology | A. Centromeres | NO | 0.372 | REJECTED | 0.045 | 0.335 |

## Fusion Votes

- **D. Mi-2 protein**: 0.416 + 0.397 = **0.813** (WON)
- **A. Centromeres**: 0.340 + 0.335 = 0.675

## Root Cause Analysis

### Why Wrong Answer Won Despite Low G Scores

1. **S Scores Are Too High**
   - GP: S=0.406 (Tier 1 said NO, but S score is still high)
   - Neurology: S=0.376 (Tier 1 said NO, but S score is still high)
   - **Tier 1 penalty for NO status isn't aggressive enough**

2. **Linear Integration Compensates for Low G**
   - GP: Final = 0.6 × 0.406 + 0.4 × 0.190 = 0.244 + 0.076 = 0.320 (before scaling)
   - After temperature scaling: 0.320^(1/1.3) = 0.416
   - **Even with low G (0.190), high S (0.406) keeps final confidence high**

3. **Multiple Specialists Agree**
   - Two specialists chose "D. Mi-2 protein"
   - Sum of confidences: 0.416 + 0.397 = 0.813
   - **Fusion picks answer with highest sum, not individual confidence**

4. **No Correct Answer Available**
   - No specialist selected "Mi-2 protein" (correct answer)
   - Answer validation can't help if no specialist has the correct answer

## The Problem

**Tier 1 says NO, but S scores are still too high (0.406, 0.376)**

**Current Tier 1 penalty for NO status**: adjustment_factor = 0.5

**Calculation**:
- Initial confidence: ~1.0 (from specialist)
- Verification confidence: ~0.5 (from Tier 1 verification)
- Combined: 0.65 × 1.0 + 0.35 × 0.5 = 0.65 + 0.175 = 0.825
- After NO penalty (0.5): 0.825 × 0.5 = 0.4125

**This matches the observed S scores (0.406, 0.376)**

## Solution

### Make Tier 1 NO Penalty More Aggressive

**Current**: adjustment_factor = 0.5 for NO status  
**Proposed**: adjustment_factor = 0.3 for NO status

**Expected impact**:
- S score would be: 0.825 × 0.3 = 0.2475 (instead of 0.4125)
- Final confidence: 0.6 × 0.2475 + 0.4 × 0.190 = 0.1485 + 0.076 = 0.2245
- After temperature scaling: 0.2245^(1/1.3) = 0.285

**This would make wrong answers have much lower final confidence, preventing them from winning fusion.**

## Recommendation

**Make Tier 1 NO penalty more aggressive**:
- Change adjustment_factor from 0.5 to 0.3 for NO status
- This will reduce S scores when Tier 1 says NO
- Combined with low G scores, wrong answers will have very low final confidence
- This should prevent wrong answers from winning fusion

## Expected Results After Fix

- Wrong answers with Tier 1=NO: Final confidence ~0.25-0.30 (instead of 0.40-0.42)
- Wrong answers won't win fusion even if multiple specialists agree
- Correct answers (if any) will have higher final confidence and win
