# Model Knowledge vs Thresholds: Root Cause Analysis

## Key Finding: Raw Signals Show NO Discrimination

Analysis of raw Two-Phase Verification signals from 30-question run:

### Correctness Scores
- **Correct answers**: mean = **0.212**, std = 0.051 (n=90)
- **Wrong answers**: mean = **0.208**, std = 0.031 (n=60)
- **Gap: +0.005** (essentially ZERO discrimination!)

### Inconsistency Scores  
- **Correct answers**: mean = **0.592**, std = 0.309 (n=90)
- **Wrong answers**: mean = **0.585**, std = 0.345 (n=60)
- **Gap: +0.007** (also essentially ZERO discrimination!)

### Combined S_Scores (Current Formula)
- **Correct answers**: mean = **0.310**
- **Wrong answers**: mean = **0.312**
- **Gap: -0.001** (WRONG answers score HIGHER!)

## What This Tells Us

### 1. **The Correctness Checker is TOO Conservative**

The correctness scores are clustered around **0.20-0.21** for BOTH correct and wrong answers. This suggests:

- **The prompt defaults to INCORRECT** (base score 0.15-0.20)
- **The LLM evaluator rarely marks answers as CORRECT** (which would give 0.70-0.85)
- **Even when answers are correct, the checker is too skeptical**

Looking at the code:
```python
correctness_score = 0.2  # Default: INCORRECT (conservative approach)
if status == "CORRECT":
    correctness_score = 0.80  # But this rarely happens!
elif status == "INCORRECT":
    correctness_score = 0.15
```

**The problem**: The LLM evaluator is almost NEVER returning "CORRECT", so everything gets low scores (0.15-0.25 range).

### 2. **Is This Model Knowledge or Prompt Design?**

**Evidence for PROMPT DESIGN issue**:
- The correctness checker uses the **same Llama 3.1 8B model** that generates answers
- If the model didn't know answers, it wouldn't get 70% accuracy
- The fact that correctness scores are **uniformly low** (not randomly distributed) suggests the **prompt is too conservative**, not that the model lacks knowledge

**Evidence for MODEL KNOWLEDGE limitation**:
- Llama 3.1 8B is a smaller model (8B parameters)
- Medical QA requires specialized knowledge
- The model might know enough to answer but not enough to **evaluate** correctness confidently

**Most Likely**: **BOTH** - The prompt is too conservative AND the model's evaluation capability is limited.

### 3. **Why Weighting Doesn't Help**

Even with different correctness weights (0.4, 0.5, 0.6, 0.7), the gap stays near zero:
- Correctness weight 0.4: Gap = -0.002
- Correctness weight 0.5: Gap = -0.001  
- Correctness weight 0.6: Gap = 0.000
- Correctness weight 0.7: Gap = +0.001

**This confirms**: The fundamental problem is that **raw signals don't discriminate**, not the weighting.

## Root Cause: Conservative Prompt + Limited Evaluation Capability

### The Correctness Checker Prompt Issues

1. **Too many "BE SKEPTICAL" instructions**: The prompt says "BE EXTREMELY SKEPTICAL", "mark as INCORRECT if uncertain", "default to INCORRECT"
2. **High threshold for CORRECT**: Requires "ABSOLUTELY CONFIDENT" to mark as CORRECT
3. **No relative comparison**: Evaluates each answer in isolation, not compared to other options
4. **Penalties are too aggressive**: Multiple penalty layers reduce scores even further

### The Model Limitation

Llama 3.1 8B might:
- Know enough to answer questions (70% accuracy)
- But NOT know enough to confidently evaluate correctness
- Especially in disagreement cases where multiple options seem plausible

## Solutions: Focus on Prompt + Relative Comparison

### Priority 1: Make Correctness Checker Less Conservative

**Current**: Defaults to INCORRECT (0.15-0.20), rarely marks CORRECT (0.70-0.85)

**Proposed**:
1. **Remove "BE EXTREMELY SKEPTICAL" language** - Replace with "Evaluate carefully"
2. **Lower CORRECT threshold** - From "ABSOLUTELY CONFIDENT" to "REASONABLY CONFIDENT"
3. **Add middle ground** - Allow scores 0.40-0.60 for "PROBABLY CORRECT" or "LIKELY CORRECT"
4. **Reduce penalties** - Remove some of the aggressive penalty layers

### Priority 2: Add Relative Comparison

**Current**: Evaluates each answer independently

**Proposed**:
1. **Compare all options**: Ask LLM to rank all options by correctness
2. **Normalize scores**: After getting raw scores, normalize within each question (best answer gets highest score)
3. **Use ranking signal**: If an answer ranks #1, boost its correctness score

### Priority 3: Improve Fusion Logic

Even with better signals, fusion needs to:
1. **Prefer relative best**: If one specialist has clearly better S_score than others (even if all are low), prefer it
2. **Lower override threshold**: From 0.45 to 0.30-0.35
3. **Use ranking**: If correct specialist ranks #1 or #2 by S_score, prefer it over majority

## Expected Impact

### If we fix prompts (Priority 1-2):

**Optimistic**:
- Correctness scores: Correct 0.21 → **0.35-0.45**, Wrong 0.21 → **0.15-0.25** (gap: 0.20)
- S_score gap: -0.001 → **+0.10-0.15**
- AUROC: 0.519 → **0.65-0.70**

**Realistic**:
- Correctness scores: Correct 0.21 → **0.30-0.35**, Wrong 0.21 → **0.18-0.22** (gap: 0.10-0.15)
- S_score gap: -0.001 → **+0.05-0.08**
- AUROC: 0.519 → **0.60-0.65**

### If we only fix fusion (Priority 3):

- AUROC: 0.519 → **0.55-0.58** (small improvement, limited by poor signals)

## Conclusion

**Answer**: It's **BOTH model knowledge AND thresholds**, but **thresholds/prompts are the bigger issue**:

1. **The correctness checker prompt is too conservative** - Everything gets low scores (0.15-0.25)
2. **The model might have limited evaluation capability** - But we can't know until we fix the prompt
3. **Relative comparison would help** - Even if absolute scores are low, ranking can provide discrimination
4. **Fusion logic needs improvement** - But won't help much if signals don't discriminate

**Recommendation**: 
1. **First**: Fix correctness checker prompt (less conservative, add relative comparison)
2. **Then**: Improve fusion logic to better leverage improved signals
3. **Finally**: If still not working, consider if model upgrade (70B) is needed

The fact that raw signals show ZERO discrimination suggests the prompt is the primary bottleneck, not necessarily model knowledge.
