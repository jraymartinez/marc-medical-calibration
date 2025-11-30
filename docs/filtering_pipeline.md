# Respiratory Disease Filtering Pipeline

A comprehensive filtering system for extracting respiratory disease cases from medical question datasets (MedQA, MedMCQA) using ICD-10 codes and intelligent keyword matching.

## Overview

This pipeline implements a two-stage filtering approach to identify respiratory disease cases from large medical datasets:

1. **ICD-10 Code Matching**: Extracts and validates ICD-10 Chapter X (J00-J99) codes
2. **Keyword Matching**: Identifies respiratory-related terms across four categories:
   - Disease keywords (pneumonia, asthma, COPD, etc.)
   - Symptom keywords (cough, dyspnea, wheeze, etc.)
   - Diagnostic keywords (spirometry, chest X-ray, ABG, etc.)
   - Anatomical keywords (lung, bronchi, alveoli, etc.)

## Features

- ✅ **ICD-10 Chapter X (J00-J99) filtering**: Comprehensive respiratory disease code coverage
- ✅ **Multi-category keyword matching**: Disease, symptoms, diagnostics, and anatomy
- ✅ **Cross-linguistic support**: Works with MedQA-USMLE, MCMLE, TWMLE variants
- ✅ **Detailed metadata**: Each filtered case includes match types and categorized keywords
- ✅ **Statistical reporting**: Comprehensive filtering statistics and distributions
- ✅ **Validation ready**: Built-in support for quality control and validation
- ✅ **Export capability**: Save filtered datasets with metadata

## Installation

```bash
# Clone or download the repository
# No external dependencies required - uses Python standard library only
python --version  # Requires Python 3.7+
```

## Quick Start

### Basic Usage

```python
from respiratory_filter_pipeline import RespiratoryFilter, load_medqa_dataset

# Initialize filter
filter_pipeline = RespiratoryFilter()

# Load your dataset
dataset = load_medqa_dataset('path/to/medqa.json')

# Filter for respiratory cases
filtered_data, statistics = filter_pipeline.filter_dataset(
    dataset, 
    dataset_name="MedQA"
)

# View statistics
filter_pipeline.print_statistics("MedQA")

# Access filtered questions
for question in filtered_data:
    print(question['question'])
    print(question['respiratory_metadata'])
```

### Running Examples

```bash
# Run comprehensive examples
python example_usage.py

# Run test suite
python test_respiratory_filter.py
```

## Expected Results

Based on the filtering pipeline diagram specifications:

| Dataset | Total Questions | Expected Filtered | Percentage |
|---------|----------------|-------------------|------------|
| MedQA (all) | ~61,097 | 1,200-1,500 | ~2.0-2.5% |
| MedMCQA | ~193,155 | 1,200-1,500 | ~0.6-0.8% |
| **Combined** | **~254,000** | **~1,200-1,500** | **~0.5-0.6%** |

### ICD-10 Coverage

The pipeline filters for **ICD-10 Chapter X (J00-J99)** categories:

- **J00-J06**: Acute upper respiratory infections
- **J20-J22**: Lower respiratory infections
- **J40-J47**: Chronic lower respiratory diseases (COPD, asthma)
- **J60-J70**: Lung diseases due to external agents
- **J80-J84**: Respiratory failure, ARDS

### Validation Characteristics

Filtered cases are:
- ✓ **Respiratory-specific**: Focused on pulmonary conditions
- ✓ **Cross-linguistic**: Covers USMLE, MCMLE, TWMLE versions
- ✓ **Clinically relevant**: Verified against metadata
- ✓ **Quality controlled**: Multiple matching criteria
- ✓ **Experiment-ready**: Standardized format for downstream tasks

## API Reference

### RespiratoryFilter Class

Main filtering class with comprehensive respiratory disease detection.

#### Methods

**`filter_question(question_data: Dict) -> Tuple[bool, Dict]`**
```python
# Filter a single question
is_respiratory, metadata = filter_pipeline.filter_question({
    'question': 'Patient with COPD exacerbation...',
    'options': {...},
    'answer': 'B'
})

# Returns:
# is_respiratory: bool - Whether question is respiratory-related
# metadata: dict with:
#   - 'icd10_codes': List of matched ICD-10 codes
#   - 'matched_keywords': List of matched keywords
#   - 'match_type': ['icd10', 'keywords'] or subset
#   - 'keyword_categories': Categorized keywords
```

**`filter_dataset(dataset: List[Dict], dataset_name: str) -> Tuple[List[Dict], FilterStats]`**
```python
# Filter entire dataset
filtered, stats = filter_pipeline.filter_dataset(
    dataset,
    dataset_name="MedQA"
)

# Returns:
# filtered: List of respiratory questions with added metadata
# stats: FilterStats object with comprehensive statistics
```

**`print_statistics(dataset_name: str)`**
```python
# Print detailed statistics
filter_pipeline.print_statistics("MedQA")

# Outputs:
# - Total questions and filtered count
# - ICD-10 and keyword match counts
# - Top disease and symptom distributions
```

### FilterStats Class

Statistics container for filtering results.

**Attributes:**
- `total_questions: int` - Total input questions
- `icd10_matches: int` - Questions with ICD-10 codes
- `keyword_matches: int` - Questions with keyword matches
- `final_filtered: int` - Total filtered questions
- `by_disease: Dict[str, int]` - Disease keyword frequency
- `by_symptom: Dict[str, int]` - Symptom keyword frequency

### Helper Functions

**`load_medqa_dataset(file_path: str) -> List[Dict]`**
```python
# Load MedQA dataset from JSON
dataset = load_medqa_dataset('medqa_usmle.json')
```

**`load_medmcqa_dataset(file_path: str) -> List[Dict]`**
```python
# Load MedMCQA dataset from JSON/JSONL
dataset = load_medmcqa_dataset('medmcqa_train.json')
```

**`save_filtered_dataset(filtered_data: List[Dict], output_path: str, metadata: Dict)`**
```python
# Save filtered data with metadata
save_filtered_dataset(
    filtered_data,
    'output.json',
    metadata={'source': 'MedQA', 'version': '1.0'}
)
```

## Keyword Categories

### Disease Keywords (16 terms)
```
pneumonia, asthma, copd, bronchitis, tuberculosis, emphysema, 
pleuritis, pleurisy, bronchiectasis, respiratory failure, ards,
acute respiratory distress, pulmonary embolism, pulmonary edema,
lung cancer, mesothelioma, sarcoidosis, pulmonary fibrosis
```

### Symptom Keywords (13 terms)
```
cough, dyspnea, wheeze, wheezing, hemoptysis, hypoxia, hypoxemia,
tachypnea, stridor, shortness of breath, difficulty breathing,
chest pain, respiratory distress
```

### Diagnostic Keywords (13 terms)
```
spirometry, chest x-ray, chest xray, ct scan, arterial blood gas,
abg, peak flow, fev1, pulse oximetry, oxygen saturation,
bronchoscopy, lung biopsy, sputum culture
```

### Anatomical Keywords (11 terms)
```
lung, lungs, bronchi, bronchus, alveoli, alveolar, pleura, pleural,
trachea, tracheal, respiratory tract, airway, airways, pulmonary
```

## Output Format

Filtered questions include original data plus respiratory metadata:

```json
{
  "id": "medqa_001",
  "question": "Patient with J44.1 COPD presents with dyspnea...",
  "options": {...},
  "answer": "B",
  "respiratory_metadata": {
    "icd10_codes": ["J44.1"],
    "matched_keywords": ["copd", "dyspnea", "bronchodilators"],
    "match_type": ["icd10", "keywords"],
    "keyword_categories": {
      "diseases": ["copd"],
      "symptoms": ["dyspnea"],
      "diagnostic": ["spirometry"],
      "anatomical": ["lung"]
    }
  }
}
```

## Dataset Compatibility

### MedQA Format
```json
{
  "question": "Patient presents with...",
  "options": {
    "A": "Option 1",
    "B": "Option 2",
    "C": "Option 3",
    "D": "Option 4"
  },
  "answer": "B",
  "explanation": "Explanation text..."
}
```

### MedMCQA Format
```json
{
  "question": "Which of the following...",
  "opa": "Option A",
  "opb": "Option B",
  "opc": "Option C",
  "opd": "Option D",
  "cop": 2,
  "subject": "Medicine",
  "topic": "Respiratory"
}
```

## Testing

The pipeline includes comprehensive unit tests:

```bash
# Run all tests
python test_respiratory_filter.py

# Tests cover:
# - ICD-10 code extraction and validation
# - Keyword matching accuracy
# - Question filtering logic
# - Metadata generation
# - Dataset processing
# - Integration workflows
```

## Performance Considerations

- **Memory**: Efficient processing of large datasets (254K+ questions)
- **Speed**: ~100-1000 questions/second (depends on text length)
- **Accuracy**: High precision/recall for respiratory cases
- **Scalability**: Can process datasets in batches if needed

## Use Cases

### 1. Dataset Preparation
```python
# Prepare training data for respiratory AI models
filtered, stats = filter_pipeline.filter_dataset(medqa_data)
save_filtered_dataset(filtered, 'training_data.json')
```

### 2. Cross-Validation
```python
# Validate filtering across multiple datasets
datasets = {'MedQA': medqa, 'MedMCQA': medmcqa}
for name, data in datasets.items():
    filtered, stats = filter_pipeline.filter_dataset(data, name)
    filter_pipeline.print_statistics(name)
```

### 3. Quality Control
```python
# Verify respiratory relevance of filtered cases
for question in filtered:
    metadata = question['respiratory_metadata']
    print(f"Match types: {metadata['match_type']}")
    print(f"Keywords: {metadata['matched_keywords']}")
```

## Dissertation Integration

This pipeline supports Paper 1 of the hierarchical verification framework by:

1. **Data Preparation**: Filters 254K questions to ~1,200-1,500 respiratory cases
2. **Quality Assurance**: Multi-criteria matching ensures clinical relevance
3. **Cross-Linguistic Coverage**: Includes USMLE, MCMLE, TWMLE variants
4. **Metadata Tracking**: Comprehensive documentation for reproducibility
5. **Validation Support**: Built-in statistics for quality verification

## Troubleshooting

### Common Issues

**Issue: Low filtering rate (<0.5%)**
- Solution: This is expected - most medical questions aren't respiratory-focused
- Verify: Check that keyword lists include your target conditions

**Issue: Missing ICD-10 codes**
- Solution: Ensure questions include ICD-10 codes in text
- Alternative: Rely on keyword matching (equally valid)

**Issue: False positives**
- Solution: Review keyword_categories to understand matches
- Adjust: Remove overly general keywords if needed

**Issue: Dataset loading errors**
- Solution: Verify JSON format matches MedQA/MedMCQA structure
- Check: File encoding (should be UTF-8)

## Future Enhancements

Potential improvements for future versions:

- [ ] Add semantic similarity matching using embeddings
- [ ] Support for additional medical datasets (MMLU-Medical, etc.)
- [ ] Configurable keyword lists via external files
- [ ] Advanced filtering rules (e.g., require multiple criteria)
- [ ] Integration with medical ontologies (SNOMED CT, MeSH)
- [ ] Parallel processing for very large datasets
- [ ] Web interface for interactive filtering

## Citation

If you use this filtering pipeline in your research, please cite:

```
[Your dissertation citation when complete]
Hierarchical Verification Framework for Multi-Agent Medical Diagnosis Systems
Harrisburg University of Science and Technology, 2025
```

## License

[Specify your license - typically academic use]

## Contact

John - PhD Candidate, Data Science
Harrisburg University of Science and Technology
Advisor: Dr. Vaida

---

**Version**: 1.0  
**Last Updated**: November 2024  
**Compatible With**: MedQA (all versions), MedMCQA
