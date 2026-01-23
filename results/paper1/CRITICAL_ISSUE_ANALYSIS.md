# Critical Issue: Accuracy Dropped from 66.7% to 53.3%

## The Problem

After applying the prompt fix to make the LLM evaluator explicitly evaluate the proposed answer, **accuracy dropped by 13.4%** (from 66.7% to 53.3%).

## Analysis

### Correctness Scores
- **Correct answers**: mean=0.463 (range: 0.404-0.475)
- **Wrong answers**: mean=0.459 (range: 0.148-0.475)
- **Gap**: 0.004 (essentially ZERO - no discrimination!)

### Status Distribution
- **UNCERTAIN**: 111 cases
- **NO**: 39 cases
- **YES**: 0 cases (none!)

### Correctness Score Distribution
- **<0.3**: 4 cases (only 4 wrong answers got low scores!)
- **0.3-0.5**: 146 cases (almost everything)
- **>=0.5**: 0 cases (nothing got high scores)

## Root Cause

The prompt fix made the LLM **too conservative**:
1. **No YES status**: All answers are marked as UNCERTAIN or NO
2. **Clustered scores**: Everything is in the 0.3-0.5 range
3. **No discrimination**: Correct and wrong answers have the same scores
4. **Fusion fails**: With no clear correct answers, fusion picks wrong ones

## The Real Issue

The LLM (Llama 3.1 8B) might not be capable of reliably evaluating medical correctness. The prompt fix made it more explicit, but the model still:
- Can't reliably distinguish correct from wrong answers
- Gets confused about which answer to evaluate
- Is too conservative (marks everything as UNCERTAIN)

## Possible Solutions

1. **Revert the prompt fix** - Go back to the previous version
2. **Use a different approach** - Don't rely on LLM for correctness checking
3. **Use a larger model** - Llama 3.1 70B might be better
4. **Simplify the task** - Just check consistency, not correctness
5. **Use few-shot examples** - Add more examples of correct vs wrong

## Recommendation

**Revert the prompt fix** and go back to the previous approach. The explicit instructions made things worse, not better. The LLM model might not be capable of this task reliably.
