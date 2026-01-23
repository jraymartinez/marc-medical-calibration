# Dataset Curation Status

## Date
2026-01-13

## Current Status
⏳ **IN PROGRESS** - Process is running

## What Happened

### Latest Run:
- ✅ Successfully loaded **254,252 questions** from raw datasets:
  - MedQA-US: 12,723 questions
  - MedQA-Mainland: 34,251 questions
  - MedQA-Taiwan: 14,123 questions
  - MedMCQA: 193,155 questions

- ✅ Model loaded successfully
- ✅ Specialist team created (4 specialists)
- ⏳ Started filtering and checking for disagreement

## Expected Process

1. **Filter by specialty** (Respiratory OR Cardiology OR Neurology)
   - Processing 254K questions
   - Estimated: 5-10% match = ~12,000-25,000 questions

2. **Check for specialist disagreement**
   - For each specialty-filtered question:
     - Get answers from 4 specialists
     - Check if they disagree
   - Estimated time: 2-4 hours per 1000 questions
   - Total: **20-100 hours** (depending on match rate)

3. **Curate to 80% disagreement**
   - Select 80 disagreement questions
   - Select 20 agreement questions
   - Save to `data/filtered/curated_disagreement_100q.json`

## Why It's Taking So Long

- **254K questions** to process
- **4 LLM calls per question** (one per specialist)
- **~1-2 seconds per question** = 254K × 1.5s = **~106 hours** if processing all

## Recommendation

The process needs to be **optimized** or **sampled**:
1. **Sample first**: Randomly sample 10K questions before filtering
2. **Early stopping**: Stop once we have enough disagreement cases
3. **Parallel processing**: Process multiple questions simultaneously

## Next Steps

1. Check if process is still running
2. If not, optimize the script to sample first
3. Re-run with optimized approach
