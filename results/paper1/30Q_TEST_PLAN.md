# 30-Question Test Plan

## Date: 2026-01-17

## Test Configuration

- **Questions**: 30 (from 100-question curated dataset)
- **Random Seed**: 42 (for reproducibility)
- **Configurations**: 4
  - Single Specialist
  - Single Specialist + Tier 1
  - Multi-Agent (No Verification)
  - Multi-Agent + Tier 1 (Two-Phase Verification)

## Expected Runtime

| Configuration | Questions | Est. Time per Question | Total Time |
|--------------|-----------|----------------------|------------|
| Single Specialist | 30 | ~30 seconds | ~15 minutes |
| Single Specialist + Tier 1 | 30 | ~1.5 minutes | ~45 minutes |
| Multi-Agent (No Verification) | 30 | ~1 minute | ~30 minutes |
| Multi-Agent + Tier 1 | 30 | ~2 minutes | ~60 minutes |
| **TOTAL** | **120 runs** | | **~2.5 hours** |

## Purpose

1. **Verify everything works**: Check that all configurations run correctly
2. **Quick validation**: See if results match expectations
3. **Debug any issues**: Catch problems before full 100-question run
4. **Initial results**: Get preliminary metrics

## After 30-Question Test

If successful:
- **Run full 100-question experiment** for final results
- Use 30-question results for initial analysis/validation

If issues found:
- **Fix problems** before full run
- Re-test with 30 questions
- Then proceed to 100 questions

## Next Steps

1. Run 30-question test now
2. Analyze results
3. If good, proceed to 100-question full experiment
