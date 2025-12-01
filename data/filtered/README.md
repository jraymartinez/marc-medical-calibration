# Filtered Respiratory Disease Dataset

This directory contains the filtered respiratory disease cases extracted from MedQA and MedMCQA datasets.

## 📊 Dataset Overview

| File | Questions | Description |
|------|-----------|-------------|
| `respiratory_cases_all.json` | 10,156 | Combined dataset (all sources) |
| `medqa_usmle_filtered.json` | 3,016 | MedQA US Medical Licensing Exam |
| `medqa_mcmle_filtered.json` | 513 | MedQA Chinese Medical Exam (Mainland) |
| `medqa_twmle_filtered.json` | 1,128 | MedQA Taiwan Medical Exam |
| `medmcqa_filtered.json` | 5,499 | MedMCQA Indian Medical Exams |

**Total**: 10,156 respiratory disease cases from 254,252 original questions (4.0% filter rate)

## 🔑 Important: Answer Field Formats

**⚠️ CRITICAL**: Questions from different sources use **different answer field formats**. Your code must handle both:

### Format 1: MedQA (4,657 questions)

**Sources**: MedQA-USMLE, MedQA-MCMLE, MedQA-TWMLE

**Answer Fields**:
- `answer_idx`: Single letter indicating correct answer (e.g., "A", "B", "C", "D", "E")
- `answer`: Full text of the correct answer
- `options`: Dictionary with keys "A", "B", "C", "D", etc.

**Example**:
```json
{
  "question": "Patient presents with dyspnea...",
  "options": {
    "A": "Asthma",
    "B": "COPD",
    "C": "Pneumonia",
    "D": "Bronchitis"
  },
  "answer": "COPD",
  "answer_idx": "B",
  "source_dataset": "MedQA-USMLE"
}
```

### Format 2: MedMCQA (5,499 questions)

**Source**: MedMCQA

**Answer Fields**:
- `cop`: Correct option position (integer 1-4, where 1=A, 2=B, 3=C, 4=D)
- `opa`, `opb`, `opc`, `opd`: Individual option text fields

**Example**:
```json
{
  "question": "Which of the following...",
  "opa": "Option A text",
  "opb": "Option B text",
  "opc": "Option C text",
  "opd": "Option D text",
  "cop": 2,
  "source_dataset": "MedMCQA"
}
```

**Note**: `cop=2` means the correct answer is option B (`opb`)

## 💡 Usage Examples

### Extracting Correct Answer

```python
def get_correct_answer(question):
    """Extract correct answer from either format"""
    
    # MedQA format
    if 'answer_idx' in question:
        return {
            'answer_idx': question['answer_idx'],
            'answer_text': question.get('answer', '')
        }
    
    # MedMCQA format
    elif 'cop' in question:
        cop = question['cop']
        option_map = {1: 'opa', 2: 'opb', 3: 'opc', 4: 'opd'}
        idx_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
        
        return {
            'answer_idx': idx_map.get(cop),
            'answer_text': question.get(option_map.get(cop, ''), '')
        }
    
    return None

# Example usage
import json

with open('respiratory_cases_all.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for question in data['filtered_questions'][:5]:
    answer = get_correct_answer(question)
    print(f"Question: {question['question'][:60]}...")
    print(f"Correct: {answer['answer_idx']} - {answer['answer_text'][:40]}...")
    print()
```

### Getting All Options

```python
def get_all_options(question):
    """Extract all options from either format"""
    
    # MedQA format
    if 'options' in question:
        return question['options']
    
    # MedMCQA format
    elif 'opa' in question:
        return {
            'A': question.get('opa', ''),
            'B': question.get('opb', ''),
            'C': question.get('opc', ''),
            'D': question.get('opd', '')
        }
    
    return {}
```

## 🏷️ Metadata Fields

All filtered questions include:

### Common Fields
- `question`: Question text
- `source_dataset`: Dataset origin (e.g., "MedQA-USMLE", "MedMCQA")
- `respiratory_metadata`: Filtering information
  - `matched_keywords`: List of respiratory keywords found
  - `match_type`: How question was filtered (`["metadata"]`, `["keywords"]`, or both)
  - `keyword_categories`: Categorized keywords (diseases, symptoms, diagnostic, anatomical)

### MedQA-Specific Fields
- `answer`: Full answer text
- `answer_idx`: Answer index (A/B/C/D/E)
- `options`: Dictionary of options
- `meta_info`: Exam type or subject category
- `metamap_phrases`: Extracted medical phrases (US version only)

### MedMCQA-Specific Fields
- `cop`: Correct option position (1-4)
- `opa`, `opb`, `opc`, `opd`: Option texts
- `subject_name`: Medical subject (e.g., "Medicine", "Surgery")
- `topic_name`: Specific topic (e.g., "Respiratory System")
- `id`: Unique question identifier
- `choice_type`: Type of question (e.g., "single", "multi")
- `exp`: Explanation (when available)

## 📈 Filtering Statistics

**Filter Version**: 2.0  
**Filter Method**: Hybrid (Metadata + Keywords)  
**Clinical Scope**: ICD-10 Chapter X (J00-J99) - Respiratory System

**Matching Methods**:
- Metadata matches: 2,724 questions (26.8%)
- Keyword matches: 8,149 questions (80.2%)
- Some questions match both criteria

**Top Disease Keywords**: asthma, pneumonia, tuberculosis, COPD, pulmonary embolism  
**Top Symptoms**: shortness of breath, dyspnea, wheezing, respiratory distress  
**Top Diagnostic**: spirometry, chest X-ray, ABG, pulse oximetry

## 📖 Documentation

For detailed filtering methodology and pipeline documentation, see:
- `docs/filtering_pipeline.md` - Complete filtering pipeline documentation
- `README.md` - Main project documentation
- `src/filtering/respiratory_filter.py` - Implementation with inline documentation

## ⚠️ Data Usage Notes

1. **Mixed Formats**: Always check which dataset a question is from before accessing answer fields
2. **Character Encoding**: Use `encoding='utf-8'` when loading JSON files (contains Chinese text)
3. **Large Files**: `respiratory_cases_all.json` is ~440K lines - use streaming or chunking for memory efficiency
4. **Metadata Reliability**: Questions with `match_type: ["metadata"]` have higher confidence than keyword-only matches

## 📝 Citation

When using this dataset, please cite:

```bibtex
@dataset{martinez2025respiratory,
  title={Filtered Respiratory Disease Cases from MedQA and MedMCQA},
  author={Martinez, John Ray},
  year={2025},
  institution={Harrisburg University of Science and Technology},
  note={Paper 1: Hierarchical Verification Framework}
}
```

## 🔗 Original Dataset Sources

- **MedQA**: Jin et al. (2021) - https://github.com/jind11/MedQA
- **MedMCQA**: Pal et al. (2022) - https://medmcqa.github.io/

---

**Last Updated**: November 30, 2025  
**Contact**: jmartinez2@my.harrisburgu.edu

