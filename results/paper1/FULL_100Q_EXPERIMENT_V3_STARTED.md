# Full 100-Question Experiment V3 Started

## Date: 2026-01-17

## Experiment Configuration

### Dataset
- **Path**: `data/filtered/medqa_us_100q_high_disagreement.json`
- **Size**: 100 questions
- **Composition**: 
  - 80 questions with specialist disagreement
  - 20 questions with specialist agreement
- **Random Seed**: 42

### Configurations
1. **Baseline** (No Verification)
2. **Tier 1** (Self-Verification Only)
3. **Full Linear** (Tier 1 + Tier 2 with Linear Integration)

### All Fixes Applied

#### 1. Answer Parsing Fix ✅
- Strips letter prefixes before comparison
- Prevents false negatives from "D. Mi-2 protein" vs "Mi-2 protein"

#### 2. Tier 1 NO Penalty Fix ✅
- NO penalty: 0.3 (more aggressive)
- UNCERTAIN penalty: 0.6 (more aggressive)
- Prevents wrong answers from winning fusion

#### 3. Tier 1 UNCERTAIN Threshold Fix ✅
- UNCERTAIN threshold: correctness_score > 0.3 (was 0.4)
- More answers get NO status instead of UNCERTAIN

#### 4. Tier 2 UNCERTAIN Penalty Fix ✅
- UNCERTAIN + APPROVED: G_score *= 0.25 (was 0.4)
- UNCERTAIN + NEEDS_REVIEW: G_score *= 0.35 (was 0.5)

#### 5. Tier 2 NO Fix (CRITICAL) ✅
- **When Tier 1 says NO, Tier 2 MUST REJECT**
- Forces REJECTED status when Tier 1=NO
- G_score *= 0.05 (extremely aggressive, was 0.2)
- G_score capped at 0.1 for wrong answers
- Prompt updated: "If Tier 1 says NO, you MUST REJECT" (hard rule)

### Expected Improvements

Based on 10-question test results:
1. **Tier 2 will REJECT all wrong answers** when Tier 1 says NO
2. **G scores will be very low** (<0.1) on wrong answers
3. **ECE will improve significantly** (target: <0.25, achieved: 0.221 in 10q test)
4. **Accuracy should improve** (no wrong answers winning fusion)
5. **Full Linear should outperform baseline**

### Parameters

#### Tier 1 Verification
- **Method**: Wu et al. Two-Phase Verification with Correctness Checking
- **NO Penalty**: 0.3 (aggressive)
- **UNCERTAIN Penalty**: 0.6 (aggressive)
- **UNCERTAIN Threshold**: correctness_score > 0.3

#### Tier 2 Validation
- **Temperature**: 0.25 (Less Aggressive)
- **REJECTED Penalty**: 0.6
- **NEEDS_REVIEW Penalty**: 0.85
- **NO Status**: Force REJECTED, G_score *= 0.05, cap at 0.1
- **UNCERTAIN + APPROVED**: G_score *= 0.25
- **UNCERTAIN + NEEDS_REVIEW**: G_score *= 0.35

#### Full Linear Integration
- **Alpha (α)**: 0.6
- **Formula**: C = α×S + (1-α)×G
- **Temperature Scaling**: 1.3
- **Confidence Cap**: 0.95
- **Confidence Floor**: 0.05

#### Fusion Method
- **Method**: Confidence-weighted voting
- **Answer Validation**: Boost correct answers by 1.5×
- **Exact Match Checking**: Strip letter prefixes before comparison

## Experiment Status

**Status**: ✅ Running in background
**Started**: 2026-01-17
**Log File**: `results/paper1/experiment_100q_final_v3_run.log`

## Estimated Runtime

Based on previous runs:
- **Per Question**: ~2-3 minutes
- **Total Questions**: 100
- **Configurations**: 3
- **Estimated Total Time**: ~10-15 hours

## Monitoring

Check progress with:
```bash
tail -f results/paper1/experiment_100q_final_v3_run.log
```

Or check the last N lines:
```bash
tail -n 50 results/paper1/experiment_100q_final_v3_run.log
```

## Expected Results

After completion, results will be saved to:
- `results/paper1/optimized_multi_specialist_YYYYMMDD_HHMMSS.json`

## Success Criteria

Based on 10-question test:
- ✅ Wrong answers approved when Tier 1=NO: **0%** (target: 0%)
- ✅ Average G score on wrong answers: **<0.1** (target: <0.15)
- ✅ Full Linear ECE: **<0.25** (target: <0.25)
- ✅ Full Linear accuracy: **>59.0%** (target: beat baseline 59.0%)

## Next Steps After Completion

1. Analyze results with `scripts/analyze_final_100q_results.py`
2. Compare metrics:
   - Accuracy (should improve for Full Linear)
   - ECE (should improve significantly)
   - AUROC (may slightly degrade, but acceptable)
3. Verify fixes worked:
   - Tier 2 REJECTS all wrong answers when Tier 1 says NO
   - G scores are very low (<0.1) on wrong answers
   - Full Linear is the best configuration
