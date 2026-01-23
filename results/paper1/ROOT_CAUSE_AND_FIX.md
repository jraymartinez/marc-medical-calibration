# Root Cause Analysis and Fix Plan

## Date: 2026-01-20

## Root Causes Identified

### 1. **NO DISCRIMINATION in Final Confidence**
- **Problem**: Final confidence for correct (0.304) vs wrong (0.312) is almost identical (diff = -0.007)
- **Impact**: AUROC = 0.412 (needs to be 0.7+)
- **Why**: Temperature scaling (1.05) compresses all confidences into narrow range (0.28-0.35)

### 2. **Two-Phase S_scores Have Better Discrimination**
- **Finding**: Max S_score has AUROC = 0.590 (vs final confidence 0.412)
- **Impact**: We're not using the best signal available
- **Why**: Fusion uses majority voting, not S_scores directly

### 3. **ECE Gap: Confidence Too Low**
- **Problem**: Confidence bins show 0.28-0.32 but accuracy is 0.65-0.70
- **Impact**: ECE = 0.24-0.26 (needs to be <0.2)
- **Why**: Temperature scaling is too aggressive, reducing confidence too much

### 4. **Fusion Not Using Two-Phase Signals**
- **Problem**: 29/30 questions use simple majority voting
- **Impact**: Two-Phase Verification isn't helping
- **Why**: No specialists get YES status (Two-Phase too strict) OR fusion logic doesn't check properly

## Fix Strategy

### Fix 1: Use S_scores More Directly for Final Confidence
**Current**: Final confidence = fusion result after temperature scaling
**New**: Final confidence = weighted combination of:
- Max S_score among all specialists (60%)
- Fusion result (40%)
- Then apply less aggressive temperature scaling

**Expected Impact**: 
- Better discrimination (AUROC: 0.412 → 0.6+)
- Better calibration (ECE: 0.24 → 0.18)

### Fix 2: Make Two-Phase Less Strict
**Current**: YES requires inconsistency < 0.6 AND correctness > 0.65
**New**: YES requires inconsistency < 0.65 AND correctness > 0.60
**Also**: Increase YES boost from 1.05 to 1.1

**Expected Impact**: More correct answers get YES status, fusion can use them

### Fix 3: Improve Fusion to Use S_scores
**Current**: Fusion uses majority voting with small S_score boosts
**New**: 
- If max S_score > 0.6, prefer that specialist's answer (even if minority)
- Use S_score-weighted voting instead of simple majority
- Boost answers with high S_scores more aggressively

**Expected Impact**: Correct answers with good S_scores win even if minority

### Fix 4: Adjust Temperature Scaling
**Current**: temperature_scale = 1.05 for Multi-Agent + Two-Phase
**New**: temperature_scale = 1.0 (no scaling) OR use S_score-based confidence directly

**Expected Impact**: Confidence better matches actual accuracy

## Implementation Priority

1. **Fix 1** (Use S_scores) - Highest priority - directly addresses AUROC
2. **Fix 3** (Improve fusion) - High priority - helps accuracy
3. **Fix 2** (Less strict Two-Phase) - Medium priority - enables Fix 3
4. **Fix 4** (Temperature scaling) - Medium priority - helps ECE
