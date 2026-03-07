# MARC: Multi-Agent Reasoning with Consistency Verification

Code and evaluation datasets for the paper:

> **Multi-Agent Reasoning with Consistency Verification Improves Uncertainty Calibration in Medical MCQA**  
> Under review at TMLR.

---

## Overview

MARC combines four domain-specific specialist agents with Two-Phase Verification (Wu et al., 2024) and S-Score Weighted Fusion to improve both calibration and discrimination in medical multiple-choice question answering (MCQA). On MedQA-250, the full system achieves 59.2% accuracy, ECE = 0.091 (74% reduction over the single-specialist baseline), and AUROC = 0.630.

**System components:**
1. **Specialist Agent Team** — Respiratory, Cardiology, Neurology, Gastroenterology specialists powered by Qwen2.5-7B-Instruct
2. **Two-Phase Consistency Verification** — Measures internal consistency of each specialist's reasoning to produce an S-score
3. **S-Score Weighted Fusion** — Aggregates specialist votes weighted by verified confidence

---

## Repository Structure

```
.
├── src/
│   ├── agents/
│   │   ├── llm_client.py            # LLM loading and generation
│   │   ├── specialist_agent.py      # Specialist agent implementation
│   │   ├── prompts.py               # All prompt templates
│   │   └── knowledge_bases.py       # Specialty knowledge contexts
│   ├── verification/
│   │   └── tier1_verification.py    # Two-Phase Verification + S-score
│   ├── fusion/
│   │   └── agreement_based_fusion.py # S-Score Weighted Fusion
│   └── evaluation/
│       └── metrics.py               # ECE, AUROC, accuracy
├── scripts/
│   ├── run_4_configs.py                       # Main experiment runner (all 4 configs)
│   ├── create_curated_disagreement_medmcqa.py # Step 1: curation pass (MedMCQA)
│   ├── create_medmcqa_100q_high_disagreement.py  # Step 2: build MedMCQA-100
│   ├── create_medmcqa_250q_high_disagreement.py  # Step 2: build MedMCQA-250
│   ├── create_100q_high_disagreement_dataset.py  # Step 2: build MedQA-100
│   ├── create_250q_high_disagreement_dataset.py  # Step 2: build MedQA-250
│   ├── generate_paper_figures_qwen250.py      # Figures for MedQA-250
│   ├── generate_paper_figures_medmcqa250.py   # Figures for MedMCQA-250
│   ├── generate_combined_figures.py           # Combined 4-dataset figures
│   ├── generate_calibration_grid.py           # Calibration grid figure
│   └── compare_100q_vs_250q.py               # 100q vs 250q consistency check
├── data/
│   ├── raw/                         # Not tracked — download instructions below
│   └── filtered/                    # The 4 evaluation sets used in the paper
│       ├── medqa_us_100q_high_disagreement.json    # MedQA-100
│       ├── medqa_us_250q_high_disagreement.json    # MedQA-250
│       ├── medmcqa_100q_high_disagreement.json     # MedMCQA-100
│       └── medmcqa_250q_high_disagreement.json     # MedMCQA-250
├── results/
│   └── 4_config_comparison/         # Raw result JSONs for all 4 datasets
├── docs/
│   ├── LOCAL_LLM_SETUP.md           # Model download and setup
│   └── HARDWARE_CONFIG.md           # Hardware requirements
├── tests/                           # Unit tests
├── requirements.txt
└── main.tex / main.bib              # Paper source
```

---

## Hardware Requirements

- **GPU**: NVIDIA GPU with ≥ 24 GB VRAM (tested on RTX 5090 Laptop 24 GB)
- **RAM**: ≥ 32 GB system RAM recommended
- **Storage**: ≥ 20 GB for model weights + datasets

See `docs/HARDWARE_CONFIG.md` for details.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/jraymartinez/marc-medical-calibration.git
cd marc-medical-calibration
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the model

Download **Qwen2.5-7B-Instruct** from Hugging Face:

```bash
python -c "
from huggingface_hub import snapshot_download
snapshot_download('Qwen/Qwen2.5-7B-Instruct', local_dir='./models/Qwen2.5-7B-Instruct')
"
```

See `docs/LOCAL_LLM_SETUP.md` for full setup instructions.

### 4. Download raw datasets (optional — evaluation sets already provided)

The four evaluation sets used in the paper are included in `data/filtered/`. If you want to rebuild them from scratch, download the source datasets:

**MedQA-USMLE:**
```bash
# Download from: https://github.com/jind11/MedQA
# Place the US split at: data/raw/MedQA/US/phrases_no_exclude_train.jsonl
```

**MedMCQA:**
```bash
# Download from: https://huggingface.co/datasets/medmcqa
# Place train split at: data/raw/MedMCQA/train.json
```

---

## Reproducing the Paper Results

### Option A: Run experiments using the provided evaluation sets

The 4 evaluation sets are already in `data/filtered/`. Run all 4 configurations directly:

```bash
# MedQA-100
python scripts/run_4_configs.py \
    --dataset data/filtered/medqa_us_100q_high_disagreement.json \
    --dataset_type medqa \
    --output_dir results/4_config_comparison

# MedQA-250
python scripts/run_4_configs.py \
    --dataset data/filtered/medqa_us_250q_high_disagreement.json \
    --dataset_type medqa \
    --output_dir results/4_config_comparison

# MedMCQA-100
python scripts/run_4_configs.py \
    --dataset data/filtered/medmcqa_100q_high_disagreement.json \
    --dataset_type medmcqa \
    --output_dir results/4_config_comparison

# MedMCQA-250
python scripts/run_4_configs.py \
    --dataset data/filtered/medmcqa_250q_high_disagreement.json \
    --dataset_type medmcqa \
    --output_dir results/4_config_comparison
```

Expected wall-clock time on a single RTX 5090 (Config 4, full system):

| Dataset | Time |
|---|---|
| MedQA-100 | ~249 min |
| MedQA-250 | ~833 min |
| MedMCQA-100 | ~288 min |
| MedMCQA-250 | ~712 min |

### Option B: Rebuild evaluation sets from raw data

```bash
# Build MedQA high-disagreement subsets
python scripts/create_100q_high_disagreement_dataset.py
python scripts/create_250q_high_disagreement_dataset.py

# Build MedMCQA high-disagreement subsets
python scripts/create_curated_disagreement_medmcqa.py
python scripts/create_medmcqa_100q_high_disagreement.py
python scripts/create_medmcqa_250q_high_disagreement.py
```

### Reproduce figures from saved results

```bash
python scripts/generate_paper_figures_qwen250.py
python scripts/generate_paper_figures_medmcqa250.py
python scripts/generate_combined_figures.py
python scripts/generate_calibration_grid.py
```

Figures are saved to `results/paper1/figures/no_grid/`.

---

## Ablation Configurations

| Config | Description |
|---|---|
| C1 | Single Specialist (respiratory only, no verification) — baseline |
| C2 | Single + Two-Phase Verification |
| C3 | Multi-Agent + S-Score Fusion (no verification) |
| C4 | Multi-Agent + Two-Phase + S-Score Fusion — full system |

---

## Key Results

| Dataset | Config | Accuracy | ECE | AUROC |
|---|---|---|---|---|
| MedQA-250 | C1 (baseline) | 54.4% | 0.355 | 0.574 |
| MedQA-250 | C4 (full system) | **59.2%** | **0.091** | **0.630** |
| MedMCQA-250 | C1 (baseline) | 42.8% | 0.469 | 0.536 |
| MedMCQA-250 | C4 (full system) | 44.0% | **0.176** | **0.594** |

---

## Citation

```bibtex
@article{martinez2026marc,
  title   = {Multi-Agent Reasoning with Consistency Verification Improves
             Uncertainty Calibration in Medical MCQA},
  author  = {Martinez, John Ray},
  journal = {Transactions on Machine Learning Research},
  year    = {2026},
  note    = {Under review}
}
```

---

## License

This code is released under the MIT License. The datasets (MedQA-USMLE, MedMCQA) are subject to their original licenses; see their respective repositories for terms.
