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

**Can a two-tier hierarchical verification system effectively identify and quantify uncertainty in multi-specialist diagnosis?**

**Focus Area**: Respiratory Disease Diagnosis

---

## 📋 Abstract

This research addresses the critical gap in multi-agent medical diagnosis systems where multiple specialist AI agents generate diagnoses without mechanisms to assess individual agent reliability. We propose a novel two-tier hierarchical verification framework combining:

1. **Tier 1**: Specialist self-verification using two-phase validation
2. **Tier 2**: General practitioner medical validation

The system is validated on respiratory disease diagnosis using ~1,200-1,500 filtered cases from MedQA and MedMCQA datasets.

**Key Contributions**:
- Novel hierarchical verification architecture for multi-agent medical AI
- Mathematical frameworks for confidence-weighted fusion (4 methods)
- Comprehensive uncertainty quantification methodology
- Benchmark validation on respiratory disease diagnosis

---

## 🏗️ System Architecture
```
Patient Query
     ↓
Multi-Specialist Response Generation
     ├─ Pulmonologist
     ├─ Internist  
     ├─ General Surgeon
     └─ Emergency Medicine
     ↓
TIER 1: Two-Phase Self-Verification
     ├─ Generate & Explain
     └─ Verify & Check
     ↓
TIER 2: GP Medical Validation
     ├─ Basic Medical Facts
     ├─ Symptom-Disease Consistency
     ├─ Medical Contradictions
     └─ General Plausibility
     ↓
Hierarchical Confidence Integration
     ├─ Linear Fusion
     ├─ Multiplicative Fusion
     ├─ Bayesian Fusion
     └─ Threshold Fusion
     ↓
Final Verified Diagnosis
```

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
python scripts/filter_datasets.py

# Expected output: ~1,200-1,500 cases
```

### Run Experiments
```bash
# Run baseline (single agent, no verification)
python experiments/run_baseline.py

# Run with Tier 1 only
python experiments/run_tier1_only.py

# Run with Tier 2 only  
python experiments/run_tier2_only.py

# Run full system (Tier 1 + Tier 2)
python experiments/run_full_system.py
```

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
**Output**: ~1,200-1,500 respiratory cases  
**Filter Rate**: ~0.5-0.6%

**Filtering Criteria**:
- ICD-10 Chapter X (J00-J99) codes
- 53 keyword terms across 4 categories:
  - Diseases (16 terms)
  - Symptoms (13 terms)
  - Diagnostic (13 terms)
  - Anatomical (11 terms)

---

## 🧪 Validation Methodology

### Three-Component Framework

1. **Calibration Analysis** (Primary Validation)
   - Metric: Expected Calibration Error (ECE)
   - Goal: ECE < 0.05 (well-calibrated)
   - Validates: Confidence = Accuracy

2. **Discrimination Analysis** (Error Detection)
   - Metric: Area Under ROC Curve (AUROC)
   - Goal: AUROC > 0.85
   - Validates: Low confidence identifies errors

3. **Accuracy Comparison** (Baseline Performance)
   - Metric: Diagnostic accuracy
   - Test: Statistical significance (McNemar)
   - Validates: Hierarchical improvement

---

## 📈 Expected Results

| System Configuration | Expected Accuracy | ECE Target |
|---------------------|------------------|------------|
| Baseline (Single Agent) | ~72% | N/A |
| Multi-Agent (No Verification) | ~77% | N/A |
| Tier 1 Only | ~82% | < 0.05 |
| **Full System (Tier 1 + 2)** | **~87%** | **< 0.05** |

---

## 🗓️ Development Timeline

- ✅ **Dec 2024**: Literature review complete
- ✅ **Dec 2024**: Data filtering pipeline complete
- 🔄 **Jan 2025**: Multi-agent system implementation
- ⏳ **Feb 2025**: Verification system implementation
- ⏳ **Mar 2025**: Experiments and baseline comparisons
- ⏳ **Apr 2025**: Analysis and paper writing
- 🎯 **May 2025**: Paper 1 submission

---

## 📚 Key References

- Singhal, K., et al. (2023). "Large Language Models Encode Clinical Knowledge." *Nature*, 620, 172-180.
- Wang, H., et al. (2024). "Beyond Direct Diagnosis: LLM-based Multi-Specialist Agent Consultation." *arXiv:2401.16107*
- Wu, J., et al. (2024). "Uncertainty Estimation of Large Language Models in Medical Question Answering." *arXiv:2407.08662*
- Dhuliawala, S., et al. (2023). "Chain-of-Verification Reduces Hallucination in Large Language Models." *arXiv:2309.11495*

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

MIT License - See [LICENSE](LICENSE) file for details

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

**Status**: 🔄 In Development  
**Current Phase**: Data Preparation ✅ Complete  
**Next Phase**: Multi-Agent Implementation (Jan 2025)