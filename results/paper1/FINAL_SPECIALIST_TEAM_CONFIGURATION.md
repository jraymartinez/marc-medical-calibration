# Final Specialist Team Configuration

## Date: 2026-01-17

## Decision: Remove GP from Multi-Specialist Team

### Rationale (Based on Wang et al. 2024)

**Wang et al. 2024 Approach**:
- **Multi-Specialist Team**: Domain specialists (Pulmonologist, Internist, General Surgeon, Emergency Medicine)
- **GP Role**: Used for triage/initial assessment, NOT as a specialist
- **Architecture**: Specialists diagnose → GP validates

**Our Updated Approach**:
- **Multi-Specialist Team**: Domain specialists only
  - Respiratory (Pulmonologist)
  - Cardiology (Cardiologist)
  - Neurology (Neurologist)
  - Gastroenterology (Gastroenterologist)
- **GP Role**: Only for Tier 2 validation (separate from specialists)

## Final Configuration

### Single Specialist (Baseline)
- **GP**: Used as single specialist (broader perspective for baseline comparison)

### Multi-Specialist Team
- **Respiratory** (Pulmonologist)
- **Cardiology** (Cardiologist)
- **Neurology** (Neurologist)
- **Gastroenterology** (Gastroenterologist)

**Note**: GP is NOT included in the multi-specialist team

### Tier 2 Validator
- **GP**: Only used for validation (separate role, not a specialist)

## Why This Configuration?

1. **Matches Wang et al. 2024**: Same architecture - specialists diagnose, GP validates
2. **Clear role separation**: 
   - Specialists = domain experts providing diagnoses
   - GP = validator checking diagnoses
3. **Maintains 4-specialist team**: Still have 4 specialists for robust fusion
4. **Better comparison**: Easier to compare with Wang et al.'s results
5. **Focused expertise**: Domain specialists focus on their specialties

## Benefits

✅ **Aligned with literature**: Matches Wang et al. 2024 approach  
✅ **Clear roles**: No confusion about GP's role  
✅ **Better comparison**: Easier to compare with existing work  
✅ **Focused**: Domain specialists provide focused expertise  
