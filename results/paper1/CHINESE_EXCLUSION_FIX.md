# Chinese Dataset Exclusion Fix

## Date
2026-01-13

## Issue
The multi-specialty filter was including MedQA-Mainland (Chinese) which Llama struggles with.

## Verification

### Taiwan (TWMLE) - KEPT ✅
- **Language**: English (verified by checking sample questions)
- **Status**: Included, but filters out any Chinese characters
- **Reason**: Questions are in English, Llama can handle them

### Mainland (MCMLE) - EXCLUDED ❌
- **Language**: Simplified Chinese
- **Status**: Excluded from filtering
- **Reason**: Llama 3.1 8B struggles with Chinese medical terminology

## Changes Made

1. **Excluded MedQA-Mainland** completely
   - Comment added explaining exclusion
   - No processing of Mainland dataset

2. **Kept MedQA-Taiwan** with Chinese character filtering
   - Processes Taiwan dataset
   - Filters out any questions containing Chinese characters
   - Keeps only English questions

## Datasets Included

- ✅ **MedQA-USMLE**: English
- ✅ **MedQA-Taiwan**: English (Chinese filtered out)
- ✅ **MedMCQA**: English/Hindi
- ❌ **MedQA-Mainland**: Excluded (Chinese)

## Expected Impact

- More accurate filtering (no Chinese questions)
- Better LLM performance (English only)
- Similar dataset size (Taiwan has English questions)
