# Single vs Multi-Specialist Ablation Study

**Date**: January 9, 2026  
**Status**: Running  
**Purpose**: Complete ablation study comparing single vs multi-specialist architectures

---

## Experiment Design

### 7 Configurations Being Tested

#### Single Specialist (Pulmonologist)
1. **Single (No Verification)** - Pure baseline
2. **Single + Tier 1** - Self-verification only
3. **Single + Full Linear** - Full hierarchical verification

#### Multi-Specialist (4 specialists)
4. **Multi (No Verification)** - Consultation baseline
5. **Multi + Tier 1** - Consultation + self-verification
6. **Multi + Full Linear** - Full system
7. **Multi + Bayesian** - Alternative integration

### Why Pulmonologist as Single Specialist?
- **Most relevant**: Respiratory disease dataset
- **Best single expert**: Should perform best individually
- **Upper bound**: Shows maximum single-specialist performance
- **Fair comparison**: Gives single specialist the advantage

---

## Research Questions

### RQ1: Multi-Specialist Benefit
**Question**: Does multi-specialist consultation improve performance?

**Comparison**: 
- Single (No Verif) vs Multi (No Verif)

**Expected**: Multi ≥ Single (Wang et al. 2024 suggests +2-5%)

**Measures**:
- Accuracy difference
- Confidence calibration
- Answer diversity

### RQ2: Verification Benefit - Single
**Question**: Does verification help single specialists?

**Comparison**:
- Single (No Verif) vs Single + Tier 1 vs Single + Full Linear

**Expected**: Verification improves both accuracy and calibration

**Measures**:
- Accuracy gain with verification
- ECE improvement
- Demonstrates verification works for individual experts

### RQ3: Verification Benefit - Multi
**Question**: Does verification help multi-specialist systems?

**Comparison**:
- Multi (No Verif) vs Multi + Tier 1 vs Multi + Full Linear

**Expected**: Hierarchical verification adds value to consultation

**Already shown**: Multi + Full Linear: 40% accuracy, 0.146 ECE

### RQ4: Synergy Effect
**Question**: Is the combination better than sum of parts?

**Comparison**:
- (Multi - Single) vs (Multi+Verif - Single+Verif)

**Expected**: Verification benefit amplified in multi-specialist setting

**Measures**:
- Additive vs multiplicative benefit
- Interaction effect

### RQ5: Computational Efficiency
**Question**: Is 4× cost justified?

**Comparison**:
- Single + Full Linear vs Multi + Full Linear
- Cost: 1× vs 4×
- Benefit: ? accuracy, ? ECE

**Decision**: If Multi only +1-2% better, may not be worth 4× cost

---

## Expected Results

### Hypothesis 1: Multi-Specialist Helps
```
Single (No Verif):        ~36-38% accuracy
Multi (No Verif):         ~36-37% accuracy (observed)
Multi-specialist benefit: 0-2% (smaller than expected?)
```

### Hypothesis 2: Verification Helps Both
```
Single (No Verif) → Single + Full Linear:  +3-5%
Multi (No Verif) → Multi + Full Linear:    +3.3% (observed)

Both improve similarly with verification
```

### Hypothesis 3: Synergy Exists
```
Best single specialist:     ~38-40%
Multi-specialist consensus: ~40%
Multi + Verification:       ~40-42%

Synergy: Verification works better when multiple viewpoints available
```

---

## Possible Outcomes & Implications

### Outcome A: Multi >> Single (Expected)
**If Multi (No Verif) is 38% and Single is 34%:**
- ✅ Multi-specialist justified
- ✅ Consultation adds unique value
- ✅ Current architecture validated

**Paper Impact**: Strong justification for multi-agent approach

### Outcome B: Multi ≈ Single (Surprising)
**If both around 36-37%:**
- 🤔 Specialist consensus doesn't help much
- 🤔 Most value from single expert domain knowledge
- 🤔 Multi-specialist benefit minimal

**Paper Impact**: Need to explain why (question difficulty? model limitations?)

### Outcome C: Single > Multi (Unexpected!)
**If Single is 38% and Multi is 36%:**
- ⚠️ Majority voting dilutes expert knowledge
- ⚠️ Non-experts add noise
- ⚠️ Need smarter fusion (Paper 2!)

**Paper Impact**: Motivation for learned fusion weights

### Outcome D: Single + Verification >> Multi (No Verif)
**If Single + Tier 1 is 40% and Multi is 36%:**
- ✅ Verification > Consultation
- ✅ Quality of reasoning > quantity of opinions
- ✅ Single expert + verification is efficient

**Paper Impact**: Practical deployment recommendation

---

## Analysis Plan

### 1. Direct Comparisons

**Multi-Specialist Benefit:**
```
Benefit = Multi (No Verif) - Single (No Verif)
```

**Verification Benefit (Single):**
```
Tier 1 Benefit = Single + Tier 1 - Single (No Verif)
Full Benefit = Single + Full Linear - Single (No Verif)
```

**Verification Benefit (Multi):**
```
Tier 1 Benefit = Multi + Tier 1 - Multi (No Verif)
Full Benefit = Multi + Full Linear - Multi (No Verif)
```

### 2. Interaction Effect

**Test if synergy exists:**
```
Expected (additive): 
  Multi + Verif = Multi_benefit + Verif_benefit + Baseline

Actual (if synergy):
  Multi + Verif > Expected

Synergy = Actual - Expected
```

### 3. Cost-Benefit Analysis

**Efficiency Metric:**
```
Efficiency = (Accuracy Gain) / (Computational Cost)

Single: Efficiency_single = Accuracy / 1×
Multi: Efficiency_multi = Accuracy / 4×

If Efficiency_single > Efficiency_multi:
  → Use single specialist for deployment
```

### 4. Statistical Significance

**McNemar's Test:**
- Single vs Multi (paired)
- With/without verification (paired)
- Determine if differences are significant

**Effect Sizes:**
- Cohen's h for proportions
- Relative risk ratios
- Number needed to treat (NNT)

---

## Visualization Plans

### New Plots to Generate

**1. Factorial Design Plot**
```
      |  No Verif  |  Tier 1  | Full Linear
------|------------|----------|-------------
Single|     ●      |    ●     |      ●
Multi |     ●      |    ●     |      ●
```

**2. Component Contribution Chart**
```
Accuracy: [Baseline][+Multi][+Tier1][+Tier2] = Final

Shows additive contributions of each component
```

**3. Cost-Benefit Scatter**
```
Y-axis: Accuracy
X-axis: Computational Cost (1× to 4×)

Points: All 7 configurations
Ideal: Upper-left (high accuracy, low cost)
```

**4. Calibration Comparison**
```
ECE by configuration type:
- Single specialists (3 configs)
- Multi specialists (4 configs)

Shows if multi-specialist affects calibration
```

---

## Implications for Paper

### If Multi-Specialist Justified
**Sections to emphasize:**
1. Multi-specialist consultation benefits (Intro)
2. Specialist agreement analysis (Methods)
3. Synergy with verification (Results)
4. When to use multiple experts (Discussion)

### If Single Specialist Competitive
**Sections to add:**
1. Computational efficiency analysis
2. Deployment recommendations (single for production)
3. When single expert suffices
4. Motivation for Paper 2 (learned weights)

### If Verification Most Important
**Key Finding:**
"Verification quality matters more than expert quantity"

**Implications:**
- Focus investment on better verification
- Single expert + verification more practical
- Multi-specialist may not scale to more specialties

---

## Expected Timeline

**Started**: 2026-01-09 ~12:30  
**Expected Completion**: 2026-01-09 ~15:00  
**Duration**: ~2.5 hours (7 configs × ~20 min each)

**Post-Processing**:
- Generate visualizations: 10 min
- Run analysis: 10 min
- Create summary: 20 min

**Total**: ~3 hours for complete ablation study

---

## Files to Generate

**Results**:
- `comparison_7configs_[timestamp].json`

**Visualizations**:
- `combined_analysis_7configs.png` - All 7 configurations
- `factorial_design.png` - 2×3 design visualization
- `cost_benefit_analysis.png` - Efficiency comparison
- `single_vs_multi.png` - Direct comparison

**Analysis**:
- `SINGLE_VS_MULTI_RESULTS.md` - Detailed findings
- `metrics_table_7configs.tex` - LaTeX table

---

## Success Criteria

### Minimum Requirements
1. ✅ All 7 configurations run successfully
2. ✅ Statistically significant differences detected
3. ✅ Clear recommendation emerges

### Ideal Outcomes
1. ✅ Multi-specialist shows clear benefit
2. ✅ Verification helps both single and multi
3. ✅ Synergy effect demonstrated
4. ✅ Full system (Multi + Full Linear) is best
5. ✅ Results support current architecture

### Acceptable Alternatives
1. ⚠️ Single competitive with Multi
   → Show verification is key component
   → Recommend single for efficiency
   
2. ⚠️ No synergy effect
   → Benefits are additive, not multiplicative
   → Still valuable independently

---

## Next Steps After Results

### If Architecture Validated
1. ✅ Scale to full dataset (1,200 questions)
2. ✅ Run statistical tests
3. ✅ Write comprehensive results section
4. ✅ Submit Paper 1

### If Architecture Needs Revision
1. 🔄 Implement learned fusion weights (Paper 2 preview)
2. 🔄 Test with more/fewer specialists
3. 🔄 Adaptive specialist selection
4. 🔄 Revise Paper 1 accordingly

---

**Status**: Experiment running in terminal 10  
**Monitor**: Check progress every 30 minutes  
**ETA**: ~3 hours to completion
