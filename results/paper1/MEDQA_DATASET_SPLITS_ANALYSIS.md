# MedQA Dataset Splits Analysis

## Date
2026-01-13

## Standard ML Dataset Split Conventions

### Train Set
- **Purpose**: Training/development of models
- **Usage**: Used to train models, tune hyperparameters, develop features
- **Size**: Usually largest (60-80% of data)
- **Can be used for**: Experimentation, model development, ablation studies

### Dev Set (Development/Validation)
- **Purpose**: Model selection and hyperparameter tuning
- **Usage**: Evaluate during training to select best model/parameters
- **Size**: Usually 10-20% of data
- **Can be used for**: Validation during training, early stopping

### Test Set
- **Purpose**: Final evaluation only
- **Usage**: Evaluate final model performance (should only be used once)
- **Size**: Usually 10-20% of data
- **Should NOT be used for**: Training, tuning, or repeated experimentation

## MedQA-US Split Sizes

Based on file counts:
- **Train**: ~10,178 questions (largest)
- **Test**: ~1,273 questions
- **Dev**: ~1,272 questions

## For Our Use Case

### Our Goal
- **Find questions with specialist disagreement**
- **Create curated dataset for experiments**
- **Test verification mechanisms**

### Recommendation: **USE TRAIN SET** ✅

**Reasons**:
1. **Largest dataset**: More questions = better chance of finding disagreement cases
2. **Standard practice**: Train set is for development/experimentation (which is what we're doing)
3. **Better balance**: More questions = better specialty balance
4. **Not final evaluation**: We're developing/testing our system, not doing final evaluation
5. **Test set preservation**: Keep test set untouched for final evaluation later

### When to Use Test Set
- **Only for final evaluation** after all development/tuning is complete
- **One-time use** to report final results in paper
- **Not for experimentation** or finding disagreement cases

## Conclusion

**Use TRAIN set** for:
- Filtering for specialty questions
- Finding disagreement cases
- Creating curated datasets
- Running experiments
- Tuning parameters

**Reserve TEST set** for:
- Final evaluation (after all development is done)
- Reporting final results in paper
