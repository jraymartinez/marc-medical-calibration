# GP in Multi-Specialist Team: Analysis

## Date: 2026-01-17

## Question: Should GP be included in the multi-specialist team?

### Current Setup

**Multi-Specialist Team**:
- General Practitioner (GP)
- Respiratory (Pulmonologist)
- Cardiology (Cardiologist)
- Neurology (Neurologist)

**Tier 2 Validator**: GP (separate role)

### Wang et al. 2024 (AMSC Paper) Approach

Based on web search and paper analysis:

**Multi-Specialist Team** (from README):
- Pulmonologist
- Internist
- General Surgeon
- Emergency Medicine

**GP Role**: Used for **initial assessment/triage**, then specialists provide opinions

**Key Difference**: 
- Wang et al. use GP for **initial triage** (before specialists)
- We use GP as **one of the specialists** (alongside domain specialists)
- We also use GP for **Tier 2 validation** (separate role)

## Analysis

### Option 1: Include GP in Multi-Specialist Team (Current) ✅

**Pros**:
1. **Broader perspective**: GP provides general medical knowledge
2. **Realistic**: In real practice, GP often participates in consultations
3. **Web search supports**: Recent papers show GP inclusion improves performance
4. **Better for mixed datasets**: GP handles diverse cases well

**Cons**:
1. **Different from Wang et al.**: They use GP for triage, not as a specialist
2. **Role confusion**: GP is both a specialist AND Tier 2 validator
3. **Less focused**: GP's general knowledge might dilute specialist expertise

### Option 2: Exclude GP from Multi-Specialist Team (Match Wang et al.)

**Multi-Specialist Team**:
- Respiratory (Pulmonologist)
- Cardiology (Cardiologist)
- Neurology (Neurologist)
- [Add one more: e.g., Internist or General Surgeon]

**GP Role**: Only for Tier 2 validation

**Pros**:
1. **Matches Wang et al.**: More aligned with their approach
2. **Clear role separation**: GP only validates, doesn't diagnose
3. **More focused**: Only domain specialists provide diagnoses
4. **Better comparison**: Easier to compare with Wang et al.'s results

**Cons**:
1. **Less general knowledge**: Missing GP's broad perspective
2. **Smaller team**: 3 specialists vs 4 (if we remove GP)

## Recommendation: **Exclude GP from Multi-Specialist Team**

### Rationale:

1. **Match Wang et al. 2024**: Their approach separates GP (triage/validation) from specialists (diagnosis)
2. **Clear role separation**: 
   - **Specialists**: Provide diagnoses (domain experts)
   - **GP**: Validates diagnoses (Tier 2)
3. **Better comparison**: Easier to compare results with Wang et al.
4. **More focused**: Domain specialists focus on their expertise

### Updated Multi-Specialist Team:

**Option A**: Match Wang et al. exactly
- Pulmonologist (Respiratory)
- Internist (General Medicine)
- General Surgeon
- Emergency Medicine

**Option B**: Keep domain specialists (simpler)
- Respiratory (Pulmonologist)
- Cardiology (Cardiologist)
- Neurology (Neurologist)
- Internist (General Medicine) - replaces GP

**Option C**: Add one more domain specialist
- Respiratory (Pulmonologist)
- Cardiology (Cardiologist)
- Neurology (Neurologist)
- Endocrinology (Endocrinologist) - or another relevant specialty

## Recommended: **Option B** (Replace GP with Internist)

**Multi-Specialist Team**:
- Respiratory (Pulmonologist)
- Cardiology (Cardiologist)
- Neurology (Neurologist)
- Internist (General Medicine) - replaces GP

**Rationale**:
- Internist provides general medical knowledge (like GP) but is still a specialist
- Maintains 4-specialist team
- Clear separation: Specialists diagnose, GP validates
- Matches our dataset (Respiratory, Cardiology, Neurology questions)

## Implementation

Update `scripts/run_final_comparison.py`:

```python
# Multi-specialist team (domain specialists only, no GP)
multi_specialties = [
    "respiratory",      # Pulmonologist
    "cardiology",       # Cardiologist
    "neurology",        # Neurologist
    "internal medicine" # Internist (replaces GP)
]
```

**GP Role**: Only used for Tier 2 validation (already separate)
