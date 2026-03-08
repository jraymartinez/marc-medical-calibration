# Scripts

## Experiment runner

| Script | Description |
|---|---|
| `run_4_configs.py` | Runs all four ablation configurations on a given dataset |

## Dataset construction

| Script | Description |
|---|---|
| `create_100q_high_disagreement_dataset.py` | Builds MedQA-100 high-disagreement subset |
| `create_250q_high_disagreement_dataset.py` | Builds MedQA-250 high-disagreement subset |
| `create_curated_disagreement_medmcqa.py` | Curation pass on MedMCQA (step 1) |
| `create_medmcqa_100q_high_disagreement.py` | Builds MedMCQA-100 high-disagreement subset |
| `create_medmcqa_250q_high_disagreement.py` | Builds MedMCQA-250 high-disagreement subset |

## Figure generation

| Script | Description |
|---|---|
| `generate_paper_figures_qwen250.py` | Accuracy/ECE/AUROC figures for MedQA-250 |
| `generate_paper_figures_medmcqa250.py` | Accuracy/ECE/AUROC figures for MedMCQA-250 |
| `generate_combined_figures.py` | Combined 4-dataset figures (Figures 2–6 in the paper) |
| `generate_calibration_grid.py` | Calibration grid figure |
| `compare_100q_vs_250q.py` | Consistency check between 100q and 250q results |

## Usage

All scripts should be run from the repository root:

```bash
python scripts/run_4_configs.py \
    --model models/Qwen2.5-7B-Instruct \
    --dataset data/filtered/medqa_us_250q_high_disagreement.json \
    --num_questions 250
```

See `README.md` at the repository root for the full reproduction workflow.
