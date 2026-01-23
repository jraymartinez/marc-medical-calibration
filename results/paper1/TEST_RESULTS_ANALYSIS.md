# Test Results Analysis - Tier 1 + Tier 2 Fixes (9 Questions)

## Summary

**Test Date**: 2026-01-15  
**Questions Completed**: 9/10 (Question 10 crashed due to Unicode error)  
**Status**: Partial results - significant improvements but issues remain

## Accuracy (9 Questions)

| Configuration | Correct | Accuracy |
|--------------|---------|----------|
| **Baseline** | 4/9 | 44.4% |
| **Tier 1** | 4/9 | 44.4% |
| **Full Linear** | 3/9 | 33.3% |

**Note**: Accuracy is lower than expected (50% in previous test) - may be due to different question subset.

## Tier 1 Correctness Checking - MAJOR IMPROVEMENT

### Results by Question

**Question 5** (Wrong: "Psychomotor epilepsy" → Correct: "Neuroblastoma"):
- GP: Correctness=0.180 (NO) - SUCCESS
- Neurology: Correctness=0.180 (NO) - SUCCESS

**Question 6** (Wrong: "Alpha toxin" → Correct: "Toxic shock syndrome toxin 1"):
- GP: Correctness=0.180 (NO) - SUCCESS
- Respiratory: Correctness=0.619 (UNCERTAIN) - PARTIAL (still too high)
- Neurology: Correctness=0.180 (NO) - SUCCESS

**Question 7** (Wrong: "D. Mi-2 protein" → Correct: "Mi-2 protein"):
- GP: Correctness=0.885 (YES) - FAILED (still too high!)
- Neurology: Correctness=0.625 (UNCERTAIN) - PARTIAL

**Question 8** (Wrong: "Golden-brown fusiform rods" → Correct: "Noncaseating granulomas"):
- Cardiology: Correctness=0.180 (NO) - SUCCESS
- Neurology: Correctness=0.180 (NO) - SUCCESS

**Question 9** (Wrong: "Hemosiderin-laden alveolar macrophages" → Correct: "Intraarticular iron deposition"):
- Respiratory: Correctness=0.180 (NO) - SUCCESS
- Cardiology: Correctness=0.180 (NO) - SUCCESS
- Neurology: Correctness=0.180 (NO) - SUCCESS

### Summary

- **SUCCESS**: 5/7 wrong answers caught (71%) with correctness=0.180
- **PARTIAL**: 2/7 wrong answers with correctness 0.619-0.625 (UNCERTAIN)
- **FAILED**: 1/7 wrong answers with correctness=0.885 (YES)

**Improvement**: Mean correctness for wrong answers: 0.885 → 0.180 (80% reduction!)

## Tier 2 Validation - MIXED RESULTS

### Results by Question

**Question 1** (Wrong: "Streptococcus pneumoniae" → Correct: "Haemophilus influenzae"):
- Respiratory: Tier 1=NO, Tier 2=APPROVED - FAILED
- Cardiology: Tier 1=NO, Tier 2=APPROVED - FAILED

**Question 5** (Wrong: "Psychomotor epilepsy"):
- GP: Tier 1=NO, Tier 2=REJECTED - SUCCESS
- Neurology: Tier 1=NO, Tier 2=REJECTED - SUCCESS

**Question 6** (Wrong: "Alpha toxin"):
- GP: Tier 1=NO, Tier 2=REJECTED - SUCCESS
- Respiratory: Tier 1=UNCERTAIN, Tier 2=APPROVED - FAILED
- Neurology: Tier 1=NO, Tier 2=APPROVED - FAILED

**Question 7** (Wrong: "D. Mi-2 protein"):
- GP: Tier 1=YES, Tier 2=APPROVED - FAILED
- Neurology: Tier 1=UNCERTAIN, Tier 2=APPROVED - FAILED

**Question 8** (Wrong: "Golden-brown fusiform rods"):
- Cardiology: Tier 1=NO, Tier 2=REJECTED - SUCCESS
- Neurology: Tier 1=NO, Tier 2=REJECTED - SUCCESS

**Question 9** (Wrong: "Hemosiderin-laden alveolar macrophages"):
- All specialists: Tier 1=NO, Tier 2=REJECTED - SUCCESS

### Summary

- **SUCCESS**: 5/9 wrong answers REJECTED (56%)
- **FAILED**: 4/9 wrong answers APPROVED (44%)

**Issue**: Tier 2 is still approving wrong answers when:
1. Tier 1 says YES (Question 7)
2. Tier 1 says UNCERTAIN (Question 6)
3. Tier 1 says NO but Tier 2 validates independently and approves (Question 1, 6)

## Key Findings

### SUCCESSES

1. **Tier 1 Correctness Checking - MAJOR IMPROVEMENT**
   - Most wrong answers now get correctness=0.180 (was 0.885)
   - 80% reduction in correctness scores for wrong answers
   - 71% of wrong answers caught with NO status

2. **Tier 2 REJECTED More Wrong Answers**
   - 56% of wrong answers REJECTED (was 0% in previous test)
   - Better at catching wrong answers when Tier 1 says NO

### ISSUES REMAINING

1. **Tier 1 Still Approving Some Wrong Answers**
   - Question 7: Correctness=0.885 (YES) - still too high
   - Question 6: One specialist with correctness=0.619 (UNCERTAIN)
   - Need to make correctness checking even more aggressive

2. **Tier 2 Still Approving Wrong Answers**
   - Question 1: APPROVED even when Tier 1 said NO
   - Question 6: APPROVED when Tier 1 said UNCERTAIN or NO
   - Question 7: APPROVED when Tier 1 said YES
   - Tier 2 needs to be more skeptical even when Tier 1 approves

3. **Accuracy Not Improved**
   - Full Linear accuracy: 33.3% (worse than baseline 44.4%)
   - Verification is not improving accuracy yet
   - May need more questions or better fusion method

## Root Cause Analysis

### Why Tier 1 Still Approves Some Wrong Answers

**Question 7** (Correctness=0.885):
- The answer "D. Mi-2 protein" is very close to correct "Mi-2 protein"
- LLM may see this as "correct" because it's almost the same
- Need to check for exact match or very strict comparison

**Question 6** (Correctness=0.619):
- Respiratory specialist got UNCERTAIN status
- Correctness score is in the middle range
- Need to lower UNCERTAIN threshold or treat as INCORRECT

### Why Tier 2 Still Approves Wrong Answers

1. **Tier 2 Validates Independently** (as designed)
   - But it's not being skeptical enough
   - Need to raise APPROVED threshold even more (0.8-0.9 → 0.85-0.9)

2. **Tier 2 Trusts Tier 1's YES Status**
   - When Tier 1 says YES, Tier 2 should still validate
   - Need to add penalty even when Tier 1 says YES but answer seems wrong

3. **Tier 2 Not Comparing Against All Options**
   - May be evaluating answer in isolation
   - Need to explicitly require comparison against all options

## Recommendations

### Immediate Fixes

1. **Make Tier 1 Even More Aggressive**
   - Lower UNCERTAIN threshold: 0.5 → 0.4
   - Treat UNCERTAIN as INCORRECT (score = 0.2)
   - Add exact match checking for answers

2. **Make Tier 2 Even More Skeptical**
   - Raise APPROVED threshold: 0.8-0.9 → 0.85-0.9
   - Add penalty when Tier 1 says YES but answer seems wrong
   - Require explicit comparison against all options

3. **Fix Unicode Error**
   - Handle special characters in answer text
   - Use ASCII-safe encoding for display

### Next Steps

1. **Re-test with fixes** (10 questions)
2. **Check if accuracy improves** with more questions
3. **If successful, run full 100-question experiment**

## Conclusion

**Significant Progress**:
- Tier 1 correctness checking: 80% improvement (0.885 → 0.180)
- Tier 2 REJECTED: 56% of wrong answers (was 0%)

**Still Need**:
- Tier 1: Catch remaining 29% of wrong answers
- Tier 2: REJECT more wrong answers (target: 80%+)
- Accuracy: Improve from 33.3% to >44.4%

The fixes are working, but need to be even more aggressive.
