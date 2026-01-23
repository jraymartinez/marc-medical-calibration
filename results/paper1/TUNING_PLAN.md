# Parameter Tuning Plan: Make Full Linear Best Configuration

## Goal
Make **Full Linear** the best configuration (highest accuracy) among:
1. Multi (No Verification) - Baseline
2. Multi + Tier 1 - Self-verification only
3. Multi + Full Linear - Tier 1 + Tier 2 (Linear integration)
4. Multi + Bayesian - Tier 1 + Tier 2 (Bayesian integration)

---

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
- This should preserve correct answers that Tier 1 identified

**Test Values**: α = [0.5, 0.6, 0.7, 0.8, 0.9]

**Expected**: Higher α (0.7-0.8) should preserve Tier 1's correct answers better.

---

### 2. **Tier 2 Penalty Factors** ⭐ SECONDARY FOCUS

**Current**:
- REJECTED: G_score *= 0.35
- NEEDS_REVIEW: G_score *= 0.65
- APPROVED: No penalty

**Strategy**:
- **Reduce penalties** → Make Tier 2 less aggressive
- **Test**: REJECTED = [0.5, 0.6, 0.7] (less aggressive)
- **Test**: NEEDS_REVIEW = [0.75, 0.8, 0.85] (less aggressive)

**Expected**: Less aggressive penalties preserve correct answers better.

---

### 3. **Tier 2 Temperature** ⭐ TERTIARY FOCUS

**Current**: temperature = 0.2

**Strategy**:
- **Increase temperature** → More nuanced judgments (less strict)
- **Test**: temperature = [0.25, 0.3, 0.35]

**Expected**: Higher temperature makes GP less strict, reducing false rejections.

---

## Experiment Design

### Phase 1: Alpha Sweep (Primary)
Run Full Linear with different α values:
- Multi + Full Linear (α=0.5) - Current
- Multi + Full Linear (α=0.6)
- Multi + Full Linear (α=0.7)
- Multi + Full Linear (α=0.8)
- Multi + Full Linear (α=0.9)

**Compare**: Which α gives best accuracy?

---

### Phase 2: Tier 2 Penalty Tuning (If Alpha Alone Doesn't Work)
Once optimal α is found, test with adjusted penalties:
- Multi + Full Linear (optimal α, default penalties) - Already tested
- Multi + Full Linear (optimal α, less aggressive penalties)
- Multi + Full Linear (optimal α, moderate penalties)

---

## Expected Outcome

**Best Configuration**: Multi + Full Linear (α=0.7-0.8) with possibly reduced penalties

**Expected Accuracy**: > 43.3% (beating Tier 1)

**Why**: Higher α preserves Tier 1's correct answers while Tier 2 still provides validation for wrong answers.

---

## Implementation

Script: `scripts/tune_full_linear.py`

**Runs**:
1. Baseline: Multi (No Verification)
2. Tier 1: Multi + Tier 1
3. Alpha Sweep: Multi + Full Linear (α=[0.5, 0.6, 0.7, 0.8, 0.9])
4. Bayesian: Multi + Bayesian
5. Best Alpha + Penalty Tuning: Multi + Full Linear (best α, different penalties)

---

## Next Steps

1. ✅ Created focused experiment script
2. ⏳ Run experiment with 30 questions
3. ⏳ Analyze results to find optimal α
4. ⏳ Test penalty adjustments if needed
5. ⏳ Finalize optimal parameters
