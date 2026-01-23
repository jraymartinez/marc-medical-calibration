# GP Removed from Multi-Specialist Team

## Date: 2026-01-17

## Change Made

**Before**:
- Multi-Specialist Team: GP, Respiratory, Cardiology, Neurology
- GP Role: Both specialist AND Tier 2 validator

**After**:
- Multi-Specialist Team: Respiratory, Cardiology, Neurology, Internal Medicine
- GP Role: Only Tier 2 validator (separate from specialists)

## Rationale

### 1. Match Wang et al. 2024 Approach
- **Wang et al.**: Multi-specialist team = domain specialists (Pulmonologist, Internist, General Surgeon, Emergency Medicine)
- **GP Role**: Used for triage/validation, NOT as a specialist
- **Our approach now**: Matches Wang et al. - GP only validates, specialists diagnose

### 2. Clear Role Separation
- **Specialists**: Provide diagnoses (domain experts)
- **GP**: Validates diagnoses (Tier 2)
- **No confusion**: GP is not both a specialist and validator

### 3. Better Comparison
- Easier to compare results with Wang et al. 2024
- Same architecture: Specialists diagnose, GP validates
- More aligned with their methodology

### 4. Focused Expertise
- Domain specialists focus on their expertise
- Internist provides general medical knowledge (like GP) but is still a specialist
- Maintains 4-specialist team

## Updated Configuration

### Single Specialist (Baseline)
- **GP**: Used as single specialist (broader perspective for baseline)

### Multi-Specialist Team
- **Respiratory** (Pulmonologist)
- **Cardiology** (Cardiologist)
- **Neurology** (Neurologist)
- **Internal Medicine** (Internist) - replaces GP

### Tier 2 Validator
- **GP**: Only used for validation (separate role)

## Benefits

1. ✅ **Matches Wang et al. 2024**: Same architecture
2. ✅ **Clear roles**: Specialists diagnose, GP validates
3. ✅ **Better comparison**: Easier to compare with literature
4. ✅ **Maintains team size**: Still 4 specialists
5. ✅ **Focused expertise**: Domain specialists focus on their domains
