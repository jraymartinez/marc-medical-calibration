# Dataset Curation Script Fixed

## Date
2026-01-13

## Issue
**Error**: `ModuleNotFoundError: No module named 'src'`

## Fix Applied
Added project root to Python path at the beginning of the script:
```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

Also added a local `load_dataset` function since `respiratory_filter.py` doesn't export one.

## Status
✅ **Script is now running in background**

The script will:
1. Load all questions from `data/filtered/respiratory_cases_all.json` (9,578 questions)
2. Filter for Respiratory/Cardiology/Neurology keywords
3. Check each question for specialist disagreement
4. Curate to achieve 80% disagreement rate
5. Save to `data/filtered/curated_disagreement_100q.json`

## Estimated Time
2-4 hours (processing ~1000+ questions to find 80 disagreement cases)

## Monitoring
Check progress by looking at the output file:
```bash
ls -lh data/filtered/curated_disagreement_100q.json
```

Or check if process is still running:
```bash
Get-Process python | Where-Object {$_.CommandLine -like "*create_curated*"}
```
