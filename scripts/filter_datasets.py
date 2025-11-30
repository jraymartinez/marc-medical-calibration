"""
Example Usage: Respiratory Disease Filtering Pipeline
Demonstrates practical usage with realistic datasets
"""

from respiratory_filter_pipeline import (
    RespiratoryFilter, 
    load_medqa_dataset,
    load_medmcqa_dataset,
    save_filtered_dataset
)
import json


def create_sample_datasets():
    """Create sample datasets for demonstration"""
    
    # Sample MedQA-style questions
    medqa_sample = [
        {
            'id': 'medqa_001',
            'question': 'A 55-year-old man with a 30-pack-year smoking history presents with progressive dyspnea and chronic cough. Spirometry shows FEV1/FVC ratio of 0.65. Chest X-ray reveals hyperinflation. What is the most likely diagnosis?',
            'options': {
                'A': 'Asthma',
                'B': 'Chronic obstructive pulmonary disease',
                'C': 'Interstitial lung disease',
                'D': 'Congestive heart failure'
            },
            'answer': 'B',
            'explanation': 'FEV1/FVC < 0.70 with smoking history indicates COPD (ICD-10: J44)'
        },
        {
            'id': 'medqa_002',
            'question': 'A 3-year-old child presents with sudden onset of fever, cough, and difficulty breathing. Chest X-ray shows bilateral infiltrates. Diagnosis: J18.9 pneumonia.',
            'options': {
                'A': 'Bacterial pneumonia',
                'B': 'Viral pneumonia', 
                'C': 'Aspiration pneumonia',
                'D': 'Atypical pneumonia'
            },
            'answer': 'B'
        },
        {
            'id': 'medqa_003',
            'question': 'A 28-year-old presents with recurrent episodes of wheezing and dyspnea, particularly at night. Peak flow variability is 25%. Diagnosis consistent with J45.9.',
            'options': {
                'A': 'COPD',
                'B': 'Asthma',
                'C': 'Bronchitis',
                'D': 'Pneumonia'
            },
            'answer': 'B'
        },
        {
            'id': 'medqa_004',
            'question': 'A 65-year-old with type 2 diabetes mellitus presents with polyuria and polydipsia. HbA1c is 9.2%.',
            'options': {
                'A': 'Increase metformin',
                'B': 'Add insulin',
                'C': 'Lifestyle modification only',
                'D': 'Add SGLT2 inhibitor'
            },
            'answer': 'B'
        },
        {
            'id': 'medqa_005',
            'question': 'Patient presents with hemoptysis and weight loss. CT scan shows cavitary lesion in upper lobe. Sputum AFB positive.',
            'options': {
                'A': 'Lung cancer',
                'B': 'Tuberculosis',
                'C': 'Fungal infection',
                'D': 'Bronchiectasis'
            },
            'answer': 'B'
        }
    ]
    
    # Sample MedMCQA-style questions
    medmcqa_sample = [
        {
            'id': 'medmcqa_001',
            'question': 'Which of the following is the first-line treatment for acute COPD exacerbation?',
            'opa': 'Antibiotics only',
            'opb': 'Bronchodilators and corticosteroids',
            'opc': 'Oxygen therapy only',
            'opd': 'Mechanical ventilation',
            'cop': 2,  # correct option
            'subject': 'Medicine',
            'topic': 'Respiratory'
        },
        {
            'id': 'medmcqa_002',
            'question': 'A patient with ARDS (J80) requires mechanical ventilation. What is the target tidal volume?',
            'opa': '10-12 mL/kg',
            'opb': '8-10 mL/kg',
            'opc': '6-8 mL/kg',
            'opd': '4-6 mL/kg',
            'cop': 3,
            'subject': 'Medicine',
            'topic': 'Critical Care'
        },
        {
            'id': 'medmcqa_003',
            'question': 'Most common cause of community-acquired pneumonia in adults?',
            'opa': 'Streptococcus pneumoniae',
            'opb': 'Haemophilus influenzae',
            'opc': 'Mycoplasma pneumoniae',
            'opd': 'Staphylococcus aureus',
            'cop': 1,
            'subject': 'Medicine',
            'topic': 'Infectious Disease'
        },
        {
            'id': 'medmcqa_004',
            'question': 'What is the gold standard for diagnosing osteoporosis?',
            'opa': 'X-ray',
            'opb': 'DEXA scan',
            'opc': 'MRI',
            'opd': 'CT scan',
            'cop': 2,
            'subject': 'Medicine',
            'topic': 'Endocrinology'
        }
    ]
    
    return medqa_sample, medmcqa_sample


def example_1_basic_filtering():
    """Example 1: Basic filtering with statistics"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Filtering")
    print("="*70)
    
    # Create sample data
    medqa_sample, medmcqa_sample = create_sample_datasets()
    
    # Initialize filter
    filter_pipeline = RespiratoryFilter()
    
    # Filter MedQA sample
    print("\nFiltering MedQA sample...")
    filtered_medqa, stats = filter_pipeline.filter_dataset(
        medqa_sample,
        dataset_name="MedQA Sample"
    )
    filter_pipeline.print_statistics("MedQA Sample")
    
    # Show filtered questions
    print("Filtered MedQA Questions:")
    for q in filtered_medqa:
        print(f"  - {q['id']}: {q['question'][:80]}...")
        print(f"    Match types: {q['respiratory_metadata']['match_type']}")
        if q['respiratory_metadata']['icd10_codes']:
            print(f"    ICD-10 codes: {q['respiratory_metadata']['icd10_codes']}")
        print()


def example_2_detailed_metadata():
    """Example 2: Examining detailed metadata"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Detailed Metadata Analysis")
    print("="*70)
    
    medqa_sample, _ = create_sample_datasets()
    filter_pipeline = RespiratoryFilter()
    
    # Filter one question with detailed analysis
    question = medqa_sample[0]  # COPD question
    is_respiratory, metadata = filter_pipeline.filter_question(question)
    
    print(f"\nQuestion: {question['question'][:100]}...")
    print(f"\nIs Respiratory: {is_respiratory}")
    print(f"\nMetadata:")
    print(f"  Match Types: {metadata['match_type']}")
    print(f"  ICD-10 Codes: {metadata['icd10_codes']}")
    print(f"  Matched Keywords: {metadata['matched_keywords']}")
    
    if 'keyword_categories' in metadata:
        print(f"\nKeyword Categories:")
        for category, keywords in metadata['keyword_categories'].items():
            if keywords:
                print(f"  {category.capitalize()}: {', '.join(keywords)}")


def example_3_cross_linguistic():
    """Example 3: Cross-linguistic filtering capability"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Cross-Linguistic Capability")
    print("="*70)
    
    # Simulate different language versions (all English in this demo)
    datasets = {
        'MedQA-USMLE': [
            {'question': 'Patient with COPD exacerbation and dyspnea', 'answer': 'A'},
            {'question': 'Asthma with wheezing', 'answer': 'B'}
        ],
        'MedQA-MCMLE': [
            {'question': 'Pneumonia with productive cough', 'answer': 'A'},
            {'question': 'Tuberculosis with hemoptysis', 'answer': 'B'}
        ],
        'MedQA-TWMLE': [
            {'question': 'ARDS requiring mechanical ventilation', 'answer': 'A'},
            {'question': 'Bronchitis with chronic cough', 'answer': 'B'}
        ]
    }
    
    filter_pipeline = RespiratoryFilter()
    
    all_results = {}
    for dataset_name, data in datasets.items():
        filtered, stats = filter_pipeline.filter_dataset(data, dataset_name)
        all_results[dataset_name] = {
            'total': stats.total_questions,
            'filtered': stats.final_filtered,
            'percentage': stats.final_filtered / stats.total_questions * 100
        }
    
    print("\nFiltering Results by Dataset:")
    print(f"{'Dataset':<20} {'Total':<10} {'Filtered':<10} {'Percentage':<10}")
    print("-" * 50)
    for dataset_name, results in all_results.items():
        print(f"{dataset_name:<20} {results['total']:<10} "
              f"{results['filtered']:<10} {results['percentage']:.1f}%")


def example_4_validation_pipeline():
    """Example 4: Validation against dataset metadata"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Validation Pipeline")
    print("="*70)
    
    # Create questions with ground truth respiratory labels
    validation_dataset = [
        {'question': 'COPD with dyspnea', 'answer': 'A', 'is_respiratory_ground_truth': True},
        {'question': 'Diabetes mellitus management', 'answer': 'B', 'is_respiratory_ground_truth': False},
        {'question': 'Pneumonia diagnosis J18.9', 'answer': 'C', 'is_respiratory_ground_truth': True},
        {'question': 'Hypertension treatment', 'answer': 'D', 'is_respiratory_ground_truth': False},
        {'question': 'Asthma with wheezing', 'answer': 'E', 'is_respiratory_ground_truth': True},
    ]
    
    filter_pipeline = RespiratoryFilter()
    
    # Validate predictions
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    
    for question in validation_dataset:
        is_respiratory, _ = filter_pipeline.filter_question(question)
        ground_truth = question['is_respiratory_ground_truth']
        
        if is_respiratory and ground_truth:
            true_positives += 1
        elif not is_respiratory and not ground_truth:
            true_negatives += 1
        elif is_respiratory and not ground_truth:
            false_positives += 1
        else:
            false_negatives += 1
    
    # Calculate metrics
    total = len(validation_dataset)
    accuracy = (true_positives + true_negatives) / total
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print("\nValidation Metrics:")
    print(f"  True Positives:  {true_positives}")
    print(f"  True Negatives:  {true_negatives}")
    print(f"  False Positives: {false_positives}")
    print(f"  False Negatives: {false_negatives}")
    print(f"\n  Accuracy:  {accuracy:.3f}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall:    {recall:.3f}")
    print(f"  F1 Score:  {f1:.3f}")


def example_5_save_and_load():
    """Example 5: Save and load filtered datasets"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Save and Load Filtered Data")
    print("="*70)
    
    medqa_sample, medmcqa_sample = create_sample_datasets()
    filter_pipeline = RespiratoryFilter()
    
    # Filter and save
    filtered, stats = filter_pipeline.filter_dataset(medqa_sample, "MedQA")
    
    output_file = '/home/claude/sample_filtered_respiratory.json'
    save_filtered_dataset(
        filtered,
        output_file,
        metadata={
            'source': 'MedQA Sample',
            'filter_version': '1.0',
            'icd10_range': 'J00-J99',
            'total_original': len(medqa_sample),
            'filtered_count': len(filtered),
            'keyword_categories': list(filter_pipeline.all_keywords)[:10]  # Sample
        }
    )
    
    # Load and verify
    with open(output_file, 'r') as f:
        loaded_data = json.load(f)
    
    print(f"\nLoaded Data Summary:")
    print(f"  Original dataset size: {loaded_data['metadata']['total_original']}")
    print(f"  Filtered dataset size: {loaded_data['count']}")
    print(f"  Filter version: {loaded_data['metadata']['filter_version']}")
    print(f"  ICD-10 range: {loaded_data['metadata']['icd10_range']}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("RESPIRATORY DISEASE FILTERING PIPELINE - EXAMPLES")
    print("="*70)
    
    try:
        example_1_basic_filtering()
        example_2_detailed_metadata()
        example_3_cross_linguistic()
        example_4_validation_pipeline()
        example_5_save_and_load()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
