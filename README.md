# Paper 1: Hierarchical Verification Framework for Multi-Agent Medical Diagnosis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Dissertation Paper 1 of 3**: Hierarchical Uncertainty Quantification for Medical AI Systems  
> **Author**: John Ray Martinez  
> **Institution**: Harrisburg University of Science and Technology  
> **Advisor**: Dr. Vaida  
> **Expected Submission**: May 2026

---

## 🎯 Research Question

**Can hierarchical priority-based fusion with Two-Phase Verification improve confidence calibration and uncertainty quantification in multi-agent medical diagnosis?**

**Key Finding**: Multi-Agent + Two-Phase Verification achieves **superior calibration (ECE 0.170)** and **discrimination (AUROC 0.599)** compared to single specialist approaches, with an acceptable accuracy trade-off for better uncertainty quantification.

---

## 📋 Abstract

This research addresses the critical challenge of uncertainty quantification in multi-agent medical diagnosis systems. We propose a novel hierarchical priority-based fusion strategy that integrates Two-Phase Self-Verification (Wu et al., 2024) with explicit minority protection mechanisms.

**Key Innovation**: An interpretable fusion strategy with 9 decision pathways that explicitly protects high-confidence minority opinions while maintaining transparency through detailed fusion reasons.

**Main Results** (100-question validation):
- **Best Calibration**: ECE 0.170 (10% better than Single Specialist + 2P)
- **Best Discrimination**: AUROC 0.599 (29% better than Single Specialist + 2P)
- **Accuracy**: 54% (acceptable trade-off for superior uncertainty quantification)

**Key Contributions**:
- Novel hierarchical priority-based fusion strategy with minority protection
- Interpretable decision taxonomy (9 fusion reasons)
- Integration of Two-Phase Verification with multi-agent systems
- Comprehensive fairness and ablation analysis (5 experimental phases)
- Superior confidence calibration and uncertainty quantification for medical AI

---

## 🏗️ System Architecture
```
Medical Question
     ↓
Multi-Specialist Diagnosis
     ├─ Respiratory Specialist
     ├─ Cardiology Specialist
     ├─ Neurology Specialist
     └─ Gastroenterology Specialist
     ↓
Two-Phase Self-Verification (Wu et al., 2024)
     ├─ Phase 1: Generate diagnosis + reasoning
     ├─ Phase 2a: Formulate verification questions
     ├─ Phase 2b: Answer independently (without reference)
     ├─ Phase 2c: Answer with reference to explanation
     └─ Phase 2d: Calculate S-score from inconsistency
     ↓
Hierarchical Priority-Based Fusion
     ├─ Priority 0: Verified Consensus (2+ verified agree)
     ├─ Priority 1: S-score Override (high S overrides majority)
     │   ├─ Minority Protection (S>0.65, gap>0.05)
     │   └─ Override Logic (gap>0.08 or verified advantage)
     ├─ Priority 2: Verified Answer (high confidence verified)
     ├─ Priority 3: Agreement + S-score (2+ agree, weighted)
     ├─ Priority 4: Majority with Penalty (weak majority check)
     └─ Priority 5: Highest Confidence (fallback)
     ↓
Final Diagnosis + Fusion Reason + Calibrated Confidence
```

**Key Features**:
- **9 Interpretable Fusion Reasons**: Each decision is labeled and explainable
- **Explicit Minority Protection**: High-confidence minorities protected from majority override
- **S-score Integration**: Two-Phase Verification scores guide fusion decisions
- **Temperature Scaling**: Post-processing calibration (T=1.4) for all configurations

---

## 📁 Project Structure
```
paper1-hierarchical-verification/
├── src/                           # Source code
│   ├── filtering/                 # ✅ Respiratory disease filtering pipeline
│   ├── agents/                    # Multi-agent system (Specialists + GP)
│   ├── verification/              # Two-tier verification logic
│   ├── fusion/                    # Confidence integration methods
│   └── evaluation/                # Validation metrics
├── tests/                         # Test suite
├── experiments/                   # Experiment runners
│   ├── run_baseline.py
│   ├── run_tier1_only.py
│   ├── run_tier2_only.py
│   └── run_full_system.py
├── notebooks/                     # Analysis notebooks
├── scripts/                       # Utility scripts
├── data/                          # Datasets (git-ignored)
│   ├── raw/                       # MedQA, MedMCQA
│   └── filtered/                  # Respiratory cases
├── results/                       # Experiment outputs (git-ignored)
├── docs/                          # Documentation
└── paper/                         # Manuscript, figures, tables
```

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
OpenAI API key or Anthropic API key
```

### Installation
```bash
# Clone repository
git clone https://github.com/jraymartinez/paper1-hierarchical-verification.git
cd paper1-hierarchical-verification

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Setup API Keys
```bash
# Create .env file (never commit this!)
echo "OPENAI_API_KEY=your-key-here" > .env
# or
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Run Data Filtering
```bash
# Filter respiratory cases from datasets
python scripts/filter_datasets_with_logging.py

# Output: ~10,000+ respiratory cases
# See: data/filtered/README.md for dataset format details
```

**⚠️ Important**: Filtered datasets contain questions from multiple sources with different answer formats. See `data/filtered/README.md` for detailed documentation on handling MedQA vs MedMCQA answer fields.

### Run Experiments
```bash
# Run final comparison (all configurations)
python scripts/run_final_comparison.py --num_questions 100 --dataset data/filtered/medqa_us_100q_high_disagreement.json --seed 42

# Configurations tested:
# 1. Single Specialist (baseline)
# 2. Single Specialist + Two-Phase Verification
# 3. Multi-Agent (No Verification)
# 4. Multi-Agent + Two-Phase Verification (our approach)

# Output: Detailed JSON results with metrics, fusion reasons, and per-question analysis
```

**Key Parameters**:
- `--num_questions`: Number of questions to test (10, 30, 100, 250)
- `--dataset`: Path to dataset JSON file
- `--seed`: Random seed for reproducibility (default: 42)

---

## 📊 Datasets

### Source Datasets

| Dataset | Size | Source | Language |
|---------|------|--------|----------|
| MedQA-USMLE | 12,723 | US Medical Licensing Exam | English |
| MedQA-MCMLE | 34,251 | Chinese Medical Exam | Chinese |
| MedQA-TWMLE | 14,123 | Taiwan Medical Exam | Traditional Chinese |
| MedMCQA | 193,155 | Indian Medical Exams | English |
| **Total** | **254,252** | Multiple regions | Cross-linguistic |

### Filtering Pipeline

**Input**: ~254,000 questions  
**Output**: ~10,000+ respiratory cases  
**Filter Rate**: ~4.0%

**Filtering Methodology** (Two-Tier Hybrid Approach):

Our filtering pipeline employs a two-tier hybrid approach optimized for medical examination datasets:

1. **Tier 1 - Metadata-Based Filtering** (High Precision)
   - MedQA-Mainland: Subject categorization ("第1篇　呼吸系统")
   - MedMCQA: Topic taxonomy (14 respiratory topics)
   - **Result**: 2,724 cases (26.8%) with high confidence

2. **Tier 2 - Keyword-Based Filtering** (Comprehensive Fallback)
   - 53 domain-specific respiratory terms across 4 categories:
     - Diseases (16 terms): pneumonia, asthma, COPD, etc.
     - Symptoms (13 terms): dyspnea, wheezing, hemoptysis, etc.
     - Diagnostic (13 terms): spirometry, chest X-ray, ABG, etc.
     - Anatomical (11 terms): bronchi, alveoli, pleura, etc.
   - **Result**: 8,149 cases across all datasets

**Clinical Scope**: ICD-10 Chapter X (J00-J99) - Diseases of the Respiratory System

**Note**: While ICD-10 codes define the clinical scope, they are not extracted from question text as medical licensing examinations present scenarios using natural language descriptions rather than diagnostic codes.

---

## 🧪 Validation Methodology

### Three-Metric Evaluation Framework

1. **Calibration Analysis** (Expected Calibration Error - ECE)
   - **What it measures**: How well confidence scores match actual correctness
   - **Goal**: ECE < 0.20 (well-calibrated)
   - **Our result**: **ECE 0.170** (BEST - Multi-Agent + 2P)
   - **Interpretation**: Confidence scores are reliable predictors of correctness

2. **Discrimination Analysis** (Area Under ROC Curve - AUROC)
   - **What it measures**: Ability to distinguish correct from incorrect predictions
   - **Goal**: AUROC > 0.60
   - **Our result**: **AUROC 0.599** (BEST - Multi-Agent + 2P)
   - **Interpretation**: System can identify uncertain/incorrect predictions

3. **Accuracy Comparison** (Diagnostic Accuracy)
   - **What it measures**: Percentage of correct diagnoses
   - **Baseline**: Single Specialist = 64%
   - **Our result**: Multi-Agent + 2P = 54%
   - **Interpretation**: 10% accuracy trade-off for superior calibration/discrimination

### Fairness Validation

All improvements must be **fair** (no configuration-specific bias):
- ✅ Temperature scaling: Same for all configurations (T=1.4)
- ✅ S-score calculation: Same Two-Phase Verification for all configs with 2P
- ✅ Fusion logic: Only affects Multi-Agent (Single Specialist has no fusion)
- ✅ No preferential treatment or skewed evaluation methods

---

## 📈 Results (100-Question Validation)

| Configuration | Accuracy | ECE | AUROC | Best Metric |
|--------------|----------|-----|-------|-------------|
| Single Specialist | 64.0% | 0.217 | 0.543 | Accuracy |
| Single + Two-Phase | 64.0% | 0.189 | 0.463 | - |
| Multi-Agent (No Verification) | 54.0% | 0.340 | 0.579 | - |
| **Multi-Agent + Two-Phase** | **54.0%** | **0.170** ⭐ | **0.599** ⭐ | **ECE & AUROC** |

**Key Findings**:
- ⭐ **Best Calibration**: Multi+2P achieves ECE 0.170 (10% better than Single+2P)
- ⭐ **Best Discrimination**: Multi+2P achieves AUROC 0.599 (29% better than Single+2P)
- **Trade-off**: 10% accuracy gap (54% vs 64%) for superior uncertainty quantification
- **Clinical Value**: Better calibration and discrimination are critical for medical AI safety

### Fusion Strategy Analysis

**Fusion Reason Distribution** (Multi-Agent + Two-Phase, 100q):
- `max_s_no_majority`: 48% (no majority, S-score tiebreaker)
- `max_s_yield_to_majority`: 37% (majority has comparable S-score)
- `max_s_override_majority`: 9% (high S-score overrides majority)
- `verified_consensus`: 2% (2+ verified specialists agree)
- `protected_minority_high_s`: 1% (minority protected by high S-score)
- Other reasons: 3%

**Interpretation**: Most decisions involve S-score-guided tiebreaking (48%) or yielding to consensus (37%), with explicit minority protection triggering rarely (1-2%) due to small S-score gaps in real data (~0.033 average).

---

## 🗓️ Development Timeline

- ✅ **Dec 2024**: Literature review complete
- ✅ **Dec 2024**: Data filtering pipeline complete
- ✅ **Jan 2025**: Multi-agent system implementation
- ✅ **Feb 2025**: Two-Phase Verification integration
- ✅ **Feb 2025**: Hierarchical fusion strategy development
- ✅ **Feb 2025**: Experiments and ablation studies (5 phases)
- ✅ **Feb 2025**: 100-question validation complete
- 🔄 **Feb 2025**: 250-question final validation (in progress)
- ⏳ **Mar 2025**: Analysis and paper writing
- 🎯 **Apr-May 2025**: Paper 1 submission

---

## 📚 Key References

- **Wu, J., et al. (2024).** "Uncertainty Estimation of Large Language Models in Medical Question Answering." *arXiv:2407.08662* [Our base method for Two-Phase Verification]
- **Singhal, K., et al. (2023).** "Large Language Models Encode Clinical Knowledge." *Nature*, 620, 172-180.
- **Wang, H., et al. (2024).** "Beyond Direct Diagnosis: LLM-based Multi-Specialist Agent Consultation." *arXiv:2401.16107*
- **Guo, C., et al. (2017).** "On Calibration of Modern Neural Networks." *ICML 2017* [ECE metric and temperature scaling]

## 📖 Documentation

Comprehensive documentation is available in the repository:

- **[FUSION_STRATEGIES_DOCUMENTATION.md](FUSION_STRATEGIES_DOCUMENTATION.md)**: Detailed explanation of hierarchical priority-based fusion vs weighted voting
- **[FUSION_REASONS_EXPLAINED.md](FUSION_REASONS_EXPLAINED.md)**: Complete guide to the 9 fusion reasons and interpretability
- **[HEURISTIC_VS_LEARNED_FUSION.md](HEURISTIC_VS_LEARNED_FUSION.md)**: Comparison of heuristic vs learned fusion approaches
- **[PUBLISHABILITY_HEURISTIC_VS_LEARNED.md](PUBLISHABILITY_HEURISTIC_VS_LEARNED.md)**: Why heuristic approaches are publishable in medical AI
- **[PHASE5_CONCLUSION.md](PHASE5_CONCLUSION.md)**: Summary of experimental phases and final results
- **[RUN_EXPERIMENTS.md](RUN_EXPERIMENTS.md)**: Guide to running parameterized experiments

---

## 📝 Citation
```bibtex
@phdthesis{martinez2026hierarchical,
  title={Hierarchical Verification Framework for Multi-Agent Medical Diagnosis},
  author={Martinez, John Ray},
  year={2026},
  school={Harrisburg University of Science and Technology},
  type={Dissertation Paper 1}
}
```

---

## 🔒 License

MIT License - See [LICENSE](https://github.com/jraymartinez/paper1-hierarchical-verification/blob/main/LICENSE.md) file for details

---

## 👤 Author

**John Ray Martinez**  
PhD Candidate, Data Science  
Harrisburg University of Science and Technology  
Email: jmartinez2@my.harrisburgu.edu  
Advisor: Dr. Vaida

---

## 🙏 Acknowledgments

- Dissertation Committee: Dr. Vaida and committee members
- Harrisburg University of Science and Technology
- Dataset providers: MedQA, MedMCQA

---

## 🎓 Research Methodology

### Fusion Strategy: Heuristic-Based

Our approach uses **hand-crafted rules with manually tuned thresholds** (heuristic approach) rather than learned models. This design choice is intentional and appropriate for medical AI because:

✅ **Interpretability**: Each decision has a clear fusion reason (9 categories)  
✅ **Transparency**: Rules are explicit and auditable (FDA-friendly)  
✅ **Reproducibility**: No training data needed, rules in paper  
✅ **Clinical Trust**: Doctors can understand and verify decision logic  
✅ **Limited Data**: Works with 100-250 questions (learned models need 1000+)  

**Publishability**: Heuristic approaches are standard and preferred in medical AI literature (Nature Medicine, NEJM AI, JAMIA). See [PUBLISHABILITY_HEURISTIC_VS_LEARNED.md](PUBLISHABILITY_HEURISTIC_VS_LEARNED.md) for detailed analysis.

### Experimental Phases

We conducted 5 experimental phases to optimize the fusion strategy:

- **Phase 1**: Relaxed fusion thresholds (max_s_override, minority_protection, majority_penalty)
- **Phase 2**: Aggressive S-score penalty (ROLLED BACK - too aggressive)
- **Phase 3**: Temperature scaling adjustment (1.3 → 1.4 for all configs)
- **Phase 4**: Further threshold relaxation (protection 0.65, penalty 0.75) - No effect due to verified_status blocking
- **Phase 5**: Removed verified_status requirement, reduced gaps (0.05/0.10) - Minimal effect due to small S-score gaps

**Key Insight**: S-score gaps in real data (~0.033 average) are too small to trigger most protection mechanisms, but the fusion strategy still achieves superior calibration and discrimination through S-score-guided tiebreaking and consensus evaluation.

---

**Status**: ✅ Experiments Complete  
**Current Phase**: 250-Question Final Validation 🔄 In Progress  
**Next Phase**: Paper Writing (Mar 2025)