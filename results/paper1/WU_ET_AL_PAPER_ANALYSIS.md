# Wu et al. Paper Analysis: What They Actually Do

## From the Paper

Wu et al.'s Two-phase Verification method:

1. **Generate explanation + answer** (Phase 1)
2. **Formulate verification questions** from the explanation
3. **Answer questions independently** (without reference to explanation)
4. **Answer questions again** with reference to the explanation
5. **Measure inconsistencies** between the two sets of answers
6. **Use inconsistency as uncertainty measure**

## Key Quote from Paper

> "The inconsistencies between the two sets of answers serve as a measure of uncertainty in the answer."

## What the Paper Does NOT Specify

The paper does **NOT** mention:
- ❌ **YES/NO/UNCERTAIN statuses** - This is our addition
- ❌ **Adjustment factors** (0.3, 0.6, 0.85) - This is our addition
- ❌ **Specific thresholds** (0.15, 0.5, 0.6) - This is our addition
- ❌ **How to combine initial confidence with verification confidence** - The paper doesn't show the exact formula

## What the Paper Actually Shows

The paper focuses on:
- **Measuring inconsistency** between independent and reference answers
- **Using inconsistency as uncertainty** (lower inconsistency = lower uncertainty = higher confidence)
- **Comparing against baseline methods** (entropy-based, fact-checking, etc.)

But it doesn't provide:
- Exact formula for converting inconsistency to final confidence
- Thresholds for categorizing inconsistency levels
- How to combine with initial confidence

## Our Implementation vs Paper

### What We Added (Not in Paper):
1. **YES/NO/UNCERTAIN statuses** based on inconsistency thresholds
2. **Adjustment factors** based on status
3. **Weighted combination** of initial_confidence and verification_confidence
4. **Specific thresholds** (0.15, 0.5, 0.6)

### What Matches the Paper:
1. ✅ Two-phase verification process
2. ✅ Formulate verification questions
3. ✅ Answer independently, then with reference
4. ✅ Measure inconsistencies
5. ✅ Use inconsistency as uncertainty measure

## Conclusion

**NO, Wu et al.'s paper does NOT use adjustment factors or YES/NO/UNCERTAIN statuses.**

These are **our additions** to make the method work in our system. The paper only describes:
- How to measure inconsistency
- That inconsistency indicates uncertainty

But it doesn't specify:
- How to convert inconsistency to final confidence
- How to combine with initial confidence
- What thresholds to use

We had to make these decisions ourselves, which is why we're having issues!
