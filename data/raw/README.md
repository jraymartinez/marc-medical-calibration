# Raw Datasets

## Download Instructions

### MedQA
1. Visit: https://github.com/jind11/MedQA
2. Download all subsets (US, Mainland, Taiwan)
3. Extract to:
   - `MedQA/US/` (dev.jsonl, test.jsonl, train.jsonl)
   - `MedQA/Mainland/` (dev.jsonl, test.jsonl, train.jsonl)
   - `MedQA/Taiwan/` (dev.jsonl, test.jsonl, train.jsonl)

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
│   │   ├── dev.jsonl
│   │   ├── test.jsonl
│   │   └── train.jsonl
│   ├── Mainland/
│   │   ├── dev.jsonl
│   │   ├── test.jsonl
│   │   └── train.jsonl
│   └── Taiwan/
│       ├── dev.jsonl
│       ├── test.jsonl
│       └── train.jsonl
└── MedMCQA/
    ├── dev.json
    ├── test.json
    └── train.json
```

## Note
These files are git-ignored due to their large size (>50MB combined).
Each collaborator must download them separately.