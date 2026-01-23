# Wang et al. 2024 Verification

## Date: 2026-01-17

## Web Search Results: What Wang et al. Actually Did

### Key Finding: **They Do NOT Include a Separate GP Agent**

From the paper "Beyond Direct Diagnosis: LLM-based Multi-Specialist Agent Consultation for Automatic Diagnosis":

1. **No Explicit GP Agent**: 
   - The paper mentions GP in the narrative/motivation (real clinical workflows)
   - But **does NOT include a separate GP agent** in the actual architecture
   - GP role is descriptive, not structural

2. **Specialist Agents Only**:
   - Multiple specialist agents created from the same LLM
   - Each specialist has disease-specific knowledge
   - Each generates probability distributions over diseases

3. **Fusion Mechanism**:
   - Specialist outputs are fused via adaptive fusion (self-attention)
   - No GP involved in the fusion

## Our Current Setup (After Fix)

**Multi-Specialist Team**:
- Respiratory (Pulmonologist)
- Cardiology (Cardiologist)
- Neurology (Neurologist)
- Gastroenterology (Gastroenterologist)
- **No GP** ✅

**GP Role**:
- Only used for Single Specialist baseline
- **Not in multi-specialist team** ✅
- **Not used for Tier 2** (we're focusing on Tier 1 only) ✅

## Verification: Does Our Setup Match Wang et al.?

✅ **YES** - Our setup now matches Wang et al.:
- Multi-specialist team = domain specialists only (no GP)
- GP is not part of the specialist team
- We use GP only for baseline comparison (different from their setup, but acceptable)

## Note on Our Approach

**Our Innovation**: We add Tier 1 (Two-Phase Verification) to the multi-specialist consultation
- **Wang et al.**: Multi-specialist consultation with adaptive fusion
- **Our work**: Multi-specialist consultation + Tier 1 verification

This is a **novel contribution** - applying verification to multi-specialist systems.
