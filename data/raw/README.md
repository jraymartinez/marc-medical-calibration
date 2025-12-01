# Raw Datasets

## Download Instructions

### MedQA
1. Visit: https://github.com/jind11/MedQA
2. Download all subsets (US, Mainland, Taiwan)
3. Extract to:
   - `MedQA/US/` (phrases_no_exclude_dev.jsonl, phrases_no_exclude_test.jsonl, phrases_no_exclude_train.jsonl)
   - `MedQA/Mainland/` (dev.jsonl, test.jsonl, train.jsonl)
   - `MedQA/Taiwan/` (tw_dev.jsonl, tw_test.jsonl, tw_train.jsonl)

### MedMCQA
1. Visit: https://medmcqa.github.io/
2. Download train, dev, test splits
3. Extract to:
   - `MedMCQA/` (dev.json, test.json, train.json)

## Expected Structure

```
data/raw/
├── MedQA/
│   ├── US/
│   │   ├── phrases_no_exclude_dev.jsonl
│   │   ├── phrases_no_exclude_test.jsonl
│   │   └── phrases_no_exclude_train.jsonl
│   ├── Mainland/
│   │   ├── dev.jsonl
│   │   ├── test.jsonl
│   │   └── train.jsonl
│   └── Taiwan/
│       ├── tw_dev.jsonl
│       ├── tw_test.jsonl
│       └── tw_train.jsonl
└── MedMCQA/
    ├── dev.json
    ├── test.json
    └── train.json
```

## File Naming Notes

- **MedQA-US**: Uses `phrases_no_exclude_*.jsonl` format (includes metamap phrases)
- **MedQA-Mainland**: Standard naming with Chinese questions
- **MedQA-Taiwan**: Uses `tw_*.jsonl` prefix for Traditional Chinese questions
- **MedMCQA**: Standard naming with JSON Lines format (.json extension)

## Note
These files are git-ignored due to their large size (>50MB combined).
Each collaborator must download them separately.