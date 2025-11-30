# Quick Start Guide: Respiratory Filtering Pipeline

## For Immediate Use in Your Dissertation

### Step 1: Integrate with Your Data Loading

```python
from respiratory_filter_pipeline import RespiratoryFilter, save_filtered_dataset
import json

# Load your MedQA data (adjust path as needed)
with open('path/to/medqa_data.json', 'r') as f:
    medqa_data = json.load(f)

# Initialize filter
filter_pipeline = RespiratoryFilter()

# Filter for respiratory cases
filtered_medqa, stats = filter_pipeline.filter_dataset(
    medqa_data, 
    dataset_name="MedQA-USMLE"
)

# Print statistics
filter_pipeline.print_statistics("MedQA-USMLE")

# Save filtered data
save_filtered_dataset(
    filtered_medqa,
    'medqa_respiratory_filtered.json',
    metadata={
        'source': 'MedQA-USMLE',
        'filter_version': '1.0',
        'icd10_range': 'J00-J99',
        'total_original': len(medqa_data),
        'date_filtered': '2024-11'
    }
)
```

### Step 2: Process All MedQA Variants

```python
# Process all three regional versions
datasets = {
    'MedQA-USMLE': 'path/to/usmle.json',
    'MedQA-MCMLE': 'path/to/mcmle.json', 
    'MedQA-TWMLE': 'path/to/twmle.json'
}

all_filtered = []
for name, path in datasets.items():
    with open(path, 'r') as f:
        data = json.load(f)
    
    filtered, stats = filter_pipeline.filter_dataset(data, name)
    filter_pipeline.print_statistics(name)
    all_filtered.extend(filtered)

# Save combined dataset
save_filtered_dataset(
    all_filtered,
    'medqa_all_respiratory.json',
    metadata={'source': 'MedQA-All', 'count': len(all_filtered)}
)
```

### Step 3: Process MedMCQA

```python
# Load MedMCQA (JSONL format)
medmcqa_data = []
with open('path/to/medmcqa.jsonl', 'r') as f:
    for line in f:
        if line.strip():
            medmcqa_data.append(json.loads(line))

# Filter
filtered_medmcqa, stats = filter_pipeline.filter_dataset(
    medmcqa_data,
    dataset_name="MedMCQA"
)

filter_pipeline.print_statistics("MedMCQA")

save_filtered_dataset(
    filtered_medmcqa,
    'medmcqa_respiratory_filtered.json'
)
```

### Step 4: Validate Your Results

```python
# Check expected counts (should be ~1,200-1,500 total)
print(f"MedQA filtered: {len(filtered_medqa)}")
print(f"MedMCQA filtered: {len(filtered_medmcqa)}")
print(f"Total: {len(filtered_medqa) + len(filtered_medmcqa)}")

# Inspect sample questions
for i, q in enumerate(filtered_medqa[:3]):
    print(f"\nQuestion {i+1}:")
    print(f"  {q['question'][:100]}...")
    print(f"  Match types: {q['respiratory_metadata']['match_type']}")
    print(f"  Keywords: {q['respiratory_metadata']['matched_keywords'][:5]}")
```

## For Paper 1 - Expected Statistics

Based on your diagram:
- **Total input**: ~254,000 questions
- **Expected output**: ~1,200-1,500 respiratory cases
- **Percentage**: ~0.5-0.6%

### Validation Checklist

✓ Respiratory-specific cases only  
✓ ICD-10 codes J00-J99 identified  
✓ Clinical terms matched (diseases, symptoms, diagnostics, anatomy)  
✓ Cross-linguistic coverage (USMLE, MCMLE, TWMLE)  
✓ Metadata tracked for reproducibility  
✓ Ready for hierarchical verification experiments  

## Integration with Your Methodology

This filtering pipeline directly supports your Paper 1 implementation:

1. **Data Preparation** (Current phase)
   - Use this pipeline to create your respiratory subset
   - Expected: ~1,200-1,500 cases from 254K total

2. **Specialist Assignment** (Next phase - January 2025)
   - Take filtered cases to your multi-agent system
   - Assign to Pulmonologist, Internist, Emergency Medicine specialists

3. **Verification Implementation** (January-March 2025)
   - Self-verification by each specialist
   - General practitioner validation
   - Agreement-weighted averaging

## Cost Estimation

With ~1,200-1,500 filtered cases:
- API calls: ~4,800-6,000 (4 agents × 1,200-1,500 cases)
- Estimated cost: $1,000-1,500 (as per your planning)

## Troubleshooting for Your Use Case

**If you get fewer than 1,000 cases:**
- Check that you're using all MedQA variants (USMLE, MCMLE, TWMLE)
- Verify MedMCQA is included
- Ensure dataset files are complete

**If you get more than 2,000 cases:**
- This is fine! More data is better
- Budget may need slight adjustment ($100-200 more)
- Consider using subset for initial experiments

**For quality verification:**
- Manually review 20-30 random filtered cases
- Verify they're actually respiratory-related
- Should see mix of pneumonia, COPD, asthma, ARDS cases

## Next Steps for Paper 1

1. ✅ **Complete** - Filtering pipeline implemented
2. **In Progress** - Run pipeline on full datasets
3. **Next Week** - Set up multi-agent architecture
4. **January** - Implement verification system
5. **February** - Run experiments
6. **March** - Analyze results
7. **April** - Write paper
8. **May** - Submit Paper 1

---

**Questions?** Review the full README.md for comprehensive documentation.

**Need modifications?** The pipeline is fully customizable:
- Edit keyword lists in `RespiratoryFilter` class
- Adjust ICD-10 ranges if needed
- Add custom validation rules
