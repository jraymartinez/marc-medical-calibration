# Parameter Tuning Strategy: Make Full Linear Best Configuration

## Goal
Make **Full Linear** the best configuration (highest accuracy) among:
1. Multi (No Verification)
2. Multi + Tier 1
3. Multi + Full Linear
4. Multi + Bayesian

## Current Problem

**Full Linear accuracy (40.0%) < Tier 1 accuracy (43.3%)**

**Root Cause**: Tier 2 GP validation is rejecting correct answers, causing their confidence to drop, and wrong answers win in confidence-weighted voting.

---

## Parameters to Tune

### 1. **Alpha (α) in Linear Integration** ⭐ PRIMARY FOCUS

**Current**: α = 0.5 (equal weight between S and G)

**Formula**: `C = α*S + (1-α)*G`

**Strategy**:
- **Increase α** → Give more weight to Tier 1 (S score)
- **Decrease α** → Give more weight to Tier 2 (G score)

**Hypothesis**: 
- If Tier 2 is rejecting correct answers, **increase α** (e.g., 0.7-0.8) to rely more on Tier 1
- This should preserve correct answers that Tier 1 identified

**Test Values**: α = [0.6, 0.7, 0.8, 0.9]

---

### 2. **Tier 2 Penalty Factors** ⭐ SECONDARY FOCUS

**Current**:
- REJECTED: G_score *= 0.35
- NEEDS_REVIEW: G_score *= 0.65
- APPROVED: No penalty

**Problem**: Even with 0.35 penalty, REJECTED answers drop confidence significantly.

**Strategy**:
- **Reduce penalties** → Make Tier 2 less aggressive
- **Test**: REJECTED = [0.5, 0.6, 0.7] (less aggressive)
- **Test**: NEEDS_REVIEW = [0.75, 0.8, 0.85] (less aggressive)

**Hypothesis**: Less aggressive penalties preserve correct answers better.

---

### 3. **Tier 2 Temperature** ⭐ TERTIARY FOCUS

**Current**: temperature = 0.2

**Strategy**:
- **Increase temperature** → More nuanced judgments (less strict)
- **Test**: temperature = [0.25, 0.3, 0.35]

**Hypothesis**: Higher temperature makes GP less strict, reducing false rejections.

---

### 4. **Tier 2 Prompt** ⭐ ALREADY IMPROVED

**Current**: Already improved to be less strict and more balanced.

**Status**: ✅ Already optimized (focuses on correctness, not finding alternatives)

---

## Recommended Tuning Order

### Phase 1: Tune Alpha (α) ⭐ PRIMARY
**Goal**: Find optimal α that makes Full Linear best

**Test**: α = [0.6, 0.7, 0.8, 0.9]

**Expected**: Higher α (0.7-0.8) should preserve Tier 1's correct answers better.

---

### Phase 2: Tune Tier 2 Penalties (If Alpha Alone Doesn't Work)
**Goal**: Reduce false rejections

**Test**:
- REJECTED: [0.5, 0.6, 0.7]
- NEEDS_REVIEW: [0.75, 0.8, 0.85]

**Expected**: Less aggressive penalties preserve correct answers.

---

### Phase 3: Tune Tier 2 Temperature (If Still Not Working)
**Goal**: Make GP less strict

**Test**: temperature = [0.25, 0.3, 0.35]

**Expected**: Higher temperature reduces false rejections.

---

## Experiment Design

### Configuration 1: Alpha Sweep (Primary)
Run 4 configurations with different α values:
- Multi + Full Linear (α=0.6)
- Multi + Full Linear (α=0.7)
- Multi + Full Linear (α=0.8)
- Multi + Full Linear (α=0.9)

**Compare**: Which α gives best accuracy?

---

### Configuration 2: Combined Tuning
Once optimal α is found, test with adjusted penalties:
- Multi + Full Linear (optimal α, reduced penalties)

---

## Expected Outcome

**Best Configuration**: Multi + Full Linear (α=0.7-0.8) with possibly reduced penalties

**Expected Accuracy**: > 43.3% (beating Tier 1)

**Why**: Higher α preserves Tier 1's correct answers while Tier 2 still provides validation for wrong answers.

---

## Implementation Plan

1. ✅ Create focused experiment script (4 multi-specialist configs)
2. ⏳ Test alpha sweep: α = [0.6, 0.7, 0.8, 0.9]
3. ⏳ Analyze results to find optimal α
4. ⏳ If needed, test penalty adjustments
5. ⏳ Finalize optimal parameters
