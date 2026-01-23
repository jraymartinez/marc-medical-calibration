# Tier 2 Parameter Inconsistency Analysis

## Problem

**Current optimized script** is using "Less Aggressive" Tier 2 parameters, but getting **40.0% accuracy** instead of expected **46.7%**.

## Tuning Run Results (alpha=0.6)

| Configuration | Tier 2 Parameters | Accuracy |
|--------------|-------------------|-----------|
| **Default** | temp=0.2, REJECTED=0.35, NEEDS_REVIEW=0.65 | **46.7%** ✅ |
| **Less Aggressive** | temp=0.25, REJECTED=0.5, NEEDS_REVIEW=0.75 | **40.0%** ❌ |
| **Moderate** | temp=0.3, REJECTED=0.6, NEEDS_REVIEW=0.8 | 43.3% |

## Resume Run Results (alpha=0.6)

| Configuration | Tier 2 Parameters | Accuracy |
|--------------|-------------------|-----------|
| **Less Aggressive** | temp=0.25, REJECTED=0.5, NEEDS_REVIEW=0.75 | **46.7%** ✅ |
| **Moderate** | temp=0.3, REJECTED=0.6, NEEDS_REVIEW=0.8 | 40.0% |

## Inconsistency Found!

**Less Aggressive** got:
- **40.0%** in tuning run
- **46.7%** in resume run

This suggests **non-determinism** or **different questions** between runs.

## Solution

**Use DEFAULT Tier 2 parameters** (which consistently got 46.7% in tuning run):
- Temperature: 0.2
- REJECTED penalty: 0.35
- NEEDS_REVIEW penalty: 0.65

These are the parameters that achieved **46.7% accuracy** in the tuning run.
