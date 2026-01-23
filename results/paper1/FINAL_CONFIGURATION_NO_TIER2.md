# Final Configuration: Tier 1 Only (No Tier 2)

## Date: 2026-01-17

## Decision: Focus on Tier 1 Only

Since we're focusing on Tier 1 (Two-Phase Verification) as the main contribution, **Tier 2 (GP validation) is not used**.

## Final Configurations

### 1. Single Specialist (Baseline)
- **Specialist**: GP (General Practitioner)
- **Verification**: None
- **Purpose**: Baseline performance

### 2. Single Specialist + Tier 1
- **Specialist**: GP (General Practitioner)
- **Verification**: Tier 1 (Two-Phase Verification)
- **Purpose**: Show verification helps even for single agent

### 3. Multi-Agent (No Verification)
- **Specialists**: Respiratory, Cardiology, Neurology, Gastroenterology
- **Verification**: None
- **Purpose**: Show multi-agent helps

### 4. Multi-Agent + Tier 1 (Two-Phase Verification) ⭐ **MAIN CONTRIBUTION**
- **Specialists**: Respiratory, Cardiology, Neurology, Gastroenterology
- **Verification**: Tier 1 (Two-Phase Verification)
- **Purpose**: Show multi-agent + verification is best

## Key Points

1. **No Tier 2**: GP validation is not used in any configuration
2. **GP only for baseline**: GP is used as single specialist baseline, not for validation
3. **Multi-specialist team**: Domain specialists only (no GP)
4. **Focus**: Tier 1 (Two-Phase Verification) is the main contribution

## Multi-Specialist Team

**Team**: Domain specialists only
- Respiratory (Pulmonologist)
- Cardiology (Cardiologist)
- Neurology (Neurologist)
- Gastroenterology (Gastroenterologist)

**GP Role**: Only used for Single Specialist baseline (not in multi-specialist team, not for Tier 2)

## Why This Configuration?

1. **Focus on Tier 1**: Main contribution is Tier 1 (Two-Phase Verification)
2. **No Tier 2 complexity**: Simpler system, easier to explain
3. **Clear comparison**: Single vs Multi-Agent, with and without Tier 1
4. **Matches research focus**: Tier 1 is what we're demonstrating works
