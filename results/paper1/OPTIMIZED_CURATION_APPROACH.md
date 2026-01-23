# Optimized Dataset Curation Approach

## Date
2026-01-13

## Problem with Original Approach
- Processing **254K raw questions** sequentially
- 4 LLM calls per question = **1M+ LLM calls**
- Estimated time: **100+ hours**

## New Two-Phase Approach ✅

### Phase 1: Keyword Filtering (FAST)
**Script**: `src/filtering/multi_specialty_filter.py`

- Filters raw datasets for Respiratory/Cardiology/Neurology keywords
- Uses keyword matching (similar to respiratory filter)
- **No LLM calls** - just text matching
- Expected output: **10-20K questions** (5-10% of raw data)
- Estimated time: **5-10 minutes**

### Phase 2: Disagreement Finding (MANAGEABLE)
**Script**: `scripts/create_curated_disagreement_dataset.py` (updated)

- Uses filtered dataset from Phase 1
- Processes **10-20K questions** instead of 254K
- 4 LLM calls per question
- Expected time: **5-10 hours** (much more manageable!)

## Benefits

1. **10-20x faster**: Process 10-20K instead of 254K
2. **Same quality**: Keyword filtering ensures relevant questions
3. **Manageable time**: 5-10 hours instead of 100+ hours
4. **Reusable**: Filtered dataset can be used for other experiments

## Current Status

✅ **Phase 1 Running**: Filtering raw datasets
⏳ **Phase 2 Ready**: Script updated to use filtered dataset

## Next Steps

1. Wait for Phase 1 to complete (~5-10 minutes)
2. Run Phase 2 with filtered dataset (~5-10 hours)
3. Get curated 100-question dataset with 80% disagreement
