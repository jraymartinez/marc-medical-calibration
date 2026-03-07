# Filtered Evaluation Datasets

This directory contains the high-disagreement evaluation subsets used in the MARC paper experiments.
All datasets are pre-filtered to questions spanning four medical specialties: respiratory, cardiology,
neurology, and gastroenterology.

## Files

| File | Questions | Description |
|------|-----------|-------------|
| `medqa_us_100q_high_disagreement.json` | 100 | MedQA-USMLE high-disagreement subset (MedQA-100) |
| `medqa_us_250q_high_disagreement.json` | 250 | MedQA-USMLE high-disagreement subset (MedQA-250) |
| `medmcqa_100q_high_disagreement.json` | 100 | MedMCQA high-disagreement subset (MedMCQA-100) |
| `medmcqa_250q_high_disagreement.json` | 250 | MedMCQA high-disagreement subset (MedMCQA-250) |
| `curated_agreement_4specialty_medqa.json` | 60 | MedQA agreement pool (used in subset construction) |
| `curated_disagreement_4specialty_medqa.json` | 220 | MedQA disagreement pool (used in subset construction) |

## Dataset Construction

High-disagreement subsets are constructed by the three-step procedure described in Appendix A.1
of the paper: specialist curation, disagreement labelling, and stratified subset construction.
A question is labelled high-disagreement if at least two of the four specialist agents propose
different answers on a lightweight single-token curation pass.

## Answer Field Formats

| Source | Ground-truth field | Values |
|--------|--------------------|--------|
| MedQA-USMLE | `answer_idx` | `"A"`, `"B"`, `"C"`, `"D"` |
| MedMCQA | `cop` | `1`, `2`, `3`, `4` |

## Original Sources

- **MedQA-USMLE**: Jin et al. (2021) — https://github.com/jind11/MedQA
- **MedMCQA**: Pal et al. (2022) — https://medmcqa.github.io/

## Citation

If you use these filtered subsets, please cite the original datasets and the MARC paper:

```bibtex
@article{jin2021disease,
  title   = {What Disease Does This Patient Have?},
  author  = {Jin, Di and others},
  journal = {Applied Sciences},
  year    = {2021}
}

@inproceedings{pal2022medmcqa,
  title     = {{MedMCQA}: A Large-Scale Multi-Subject Multi-Choice Dataset},
  author    = {Pal, Ankit and others},
  booktitle = {CHIL},
  year      = {2022}
}
```

---

**Last Updated**: March 2026  
**Contact**: jmartinez2@my.harrisburgu.edu
