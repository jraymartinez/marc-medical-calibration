# Single Specialist Choice Analysis

## Date: 2026-01-17

## Question: GP vs Specialist for Single Specialist Configurations?

### Dataset Analysis

**Dataset**: `medqa_us_100q_high_disagreement.json`
- **Mixed specialties**: Respiratory, Cardiology, Neurology questions
- **Not single-specialty focused**: Questions span multiple medical domains

### Options

#### Option 1: GP (General Practitioner) ✅ **RECOMMENDED**

**Pros**:
1. **Fairer comparison**: GP has general knowledge across all specialties
   - Not biased toward respiratory, cardiology, or neurology
   - Represents what you'd realistically use in a single-agent system

2. **Consistent with existing codebase**: 
   - `compare_7_configs.py` already uses GP for single specialist (line 338)
   - Established pattern in the codebase

3. **Realistic scenario**: 
   - In real medical practice, a GP would handle mixed cases
   - More representative of a single-agent medical AI system

4. **Better for mixed dataset**:
   - Can handle respiratory, cardiology, and neurology questions
   - Not disadvantaged on non-respiratory questions

**Cons**:
- Less specialized knowledge than domain specialists
- Might have lower accuracy than specialists on their domain questions

#### Option 2: Specialist (e.g., Pulmonologist)

**Pros**:
- More specialized knowledge
- Better for respiratory questions

**Cons**:
1. **Unfair comparison**: 
   - Biased toward respiratory questions
   - Disadvantaged on cardiology/neurology questions
   - Not representative of a realistic single-agent system

2. **Dataset mismatch**: 
   - Dataset has mixed specialties
   - Using Pulmonologist only is unfair for cardiology/neurology questions

3. **Comparison issue**:
   - If Pulmonologist performs well on respiratory but poorly on cardiology/neurology
   - Hard to interpret results fairly

## Recommendation: **Use GP (General Practitioner)**

### Rationale

1. **Fair comparison**: GP has general knowledge, making it a fair baseline
2. **Realistic**: Represents what you'd use in a single-agent system
3. **Consistent**: Matches existing codebase (`compare_7_configs.py`)
4. **Better for mixed dataset**: Can handle all specialty questions

### Updated Configuration

```python
# Single specialist: Use GP (General Practitioner) for broader perspective
single_specialty = "general practitioner"  # GP for single specialist
single_specialist_team = create_specialist_team([single_specialty], llm_client)
```

### Expected Results

| Configuration | Expected Performance | Rationale |
|--------------|---------------------|-----------|
| **Single Specialist (GP)** | Baseline | GP has general knowledge |
| **Multi-Agent (No Verification)** | Better than Single | Multiple specialists > GP |
| **Multi-Agent + Tier 1** | Best | Multi-agent + verification |
| **Single Specialist + Tier 1** | Better than Single, worse than Multi-Agent | Shows multi-agent helps even with verification |

## Implementation

Update `scripts/run_final_comparison.py` to use GP instead of Pulmonologist.
