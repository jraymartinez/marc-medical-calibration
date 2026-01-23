# Temperature Analysis: Impact on Performance

## Current Temperature Settings

### Specialist Agents
- **Temperature: 0.3** (from `src/agents/specialist_agent.py`)
- **Deterministic mode**: `use_deterministic=True` (greedy decoding, temperature=0.0)
- **Note**: When deterministic=True, temperature is ignored and greedy decoding is used

### Two-Phase Verification
- **Temperature: 0.2** (from `src/verification/tier1_verification.py`)
- Used for:
  - Formulating verification questions
  - Answering questions independently
  - Answering questions with reference

## How Temperature Affects Wu et al.'s Method

### 1. **Consistency Measurement**
Wu et al.'s method measures **inconsistency** between:
- Independent answers (without reference)
- Reference answers (with reference to explanation)

**Problem**: If temperature is too high:
- Independent answers become more random/variable
- Higher inconsistency scores (even for correct answers)
- False positives (correct answers marked as inconsistent)

**If temperature is too low**:
- Answers become too deterministic
- Lower inconsistency scores (even for wrong answers)
- False negatives (wrong answers marked as consistent)

### 2. **Verification Question Formulation**
Temperature affects how verification questions are generated:
- **High temperature**: More creative/diverse questions (good for coverage)
- **Low temperature**: More focused/consistent questions (good for reliability)

### 3. **Answer Quality**
Temperature affects reasoning quality:
- **High temperature**: More diverse reasoning, but potentially less accurate
- **Low temperature**: More focused reasoning, but potentially less creative

## Current Issues

### Problem 1: **Inconsistent Temperature Usage**
- Specialist agents: 0.3 (or 0.0 if deterministic)
- Verification: 0.2
- **Mismatch**: Different temperatures for generation vs verification could cause inconsistency

### Problem 2: **Temperature Too Low for Verification?**
- Current: 0.2
- **Issue**: Very low temperature might make verification too deterministic
- Independent answers might be too similar to reference answers (low inconsistency even when wrong)

### Problem 3: **Deterministic Mode for Specialists**
- Specialists use `use_deterministic=True` → temperature=0.0 (greedy)
- **Issue**: Completely deterministic answers might be too confident
- No exploration of alternative reasoning paths

## Recommendations

### Option 1: **Match Temperatures** (Recommended)
- Use **same temperature** for specialists and verification
- **Suggested: 0.2-0.3** for consistency
- Ensures verification questions and answers are generated with same randomness level

### Option 2: **Higher Temperature for Verification**
- Specialists: 0.3 (or 0.0 if deterministic)
- Verification: **0.4-0.5** (higher)
- **Rationale**: More diverse independent answers → better inconsistency detection
- **Risk**: Too much randomness might hurt accuracy

### Option 3: **Lower Temperature for Verification**
- Specialists: 0.3
- Verification: **0.1** (lower)
- **Rationale**: More focused verification questions and answers
- **Risk**: Too deterministic → might miss inconsistencies

### Option 4: **Temperature for Independent vs Reference Answers**
- Independent answers: **Higher temperature (0.4-0.5)** - more diverse
- Reference answers: **Lower temperature (0.1-0.2)** - more focused
- **Rationale**: Independent answers should explore different reasoning, reference should be consistent

## Expected Impact

### If we increase verification temperature (0.2 → 0.4):
- **Pros**:
  - More diverse independent answers
  - Better inconsistency detection
  - Might catch more wrong answers
- **Cons**:
  - More variable inconsistency scores
  - Might mark correct answers as inconsistent
  - Less reliable verification

### If we decrease verification temperature (0.2 → 0.1):
- **Pros**:
  - More consistent verification
  - More reliable inconsistency scores
- **Cons**:
  - Might miss inconsistencies in wrong answers
  - Independent answers too similar to reference

### If we match temperatures (both 0.3):
- **Pros**:
  - Consistent randomness level
  - Better alignment between generation and verification
- **Cons**:
  - Might need to tune both together

## Recommendation

**Start with matching temperatures at 0.3**:
1. Set specialist temperature to 0.3 (if not using deterministic)
2. Set verification temperature to 0.3
3. Test and compare with current (0.2)

**Then try higher verification temperature (0.4)**:
- Independent answers need more diversity to detect inconsistencies
- Reference answers can stay at 0.2-0.3

## Next Steps

1. Test with matched temperatures (0.3 for both)
2. Test with higher verification temperature (0.4)
3. Compare results with current (0.2)
4. Choose best performing configuration
