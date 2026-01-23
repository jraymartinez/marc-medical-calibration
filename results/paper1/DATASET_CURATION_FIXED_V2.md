# Dataset Curation Script Fixed (Version 2)

## Date
2026-01-13

## Issue Fixed
**Problem**: Script was loading from `data/filtered/respiratory_cases_all.json` which only contains respiratory questions.

**Solution**: Now loads from **raw datasets** (MedQA + MedMCQA) and filters for:
- **Respiratory** OR **Cardiology** OR **Neurology** questions

## Changes Made

### 1. Load from Raw Datasets ✅
- Added `load_all_raw_datasets()` function
- Loads from:
  - MedQA-US (dev/test/train)
  - MedQA-Mainland (dev/test/train)
  - MedQA-Taiwan (dev/test/train)
  - MedMCQA (dev/test/train)

### 2. Filter for Three Specialties ✅
- Updated `has_specialty_keywords()` to accept full question dict
- Handles different dataset formats (MedQA vs MedMCQA)
- Filters for Respiratory **OR** Cardiology **OR** Neurology

### 3. Handle Different Formats ✅
- MedQA: `question`, `options` fields
- MedMCQA: `Question`, `opa`, `opb`, `opc`, `opd` fields

## Expected Behavior

1. Loads all raw datasets (~250K+ questions)
2. Filters for Respiratory/Cardiology/Neurology keywords
3. Checks each question for specialist disagreement
4. Curates to achieve 80% disagreement rate
5. Saves 100 questions to `data/filtered/curated_disagreement_100q.json`

## Status
✅ **Fixed and ready to run**
