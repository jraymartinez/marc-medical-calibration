"""
Dataset Filtering Script for Paper 1
Filters MedQA and MedMCQA datasets for respiratory disease cases

Dataset Structure:
- MedQA: 3 folders (Mainland, Taiwan, US) × 3 files (dev, test, train) = 9 JSONL files
- MedMCQA: 3 files (dev, test, train) = 3 JSON/JSONL files
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from filtering.respiratory_filter import (
    RespiratoryFilter,
    FilterStats,
    save_filtered_dataset
)
import json
from datetime import datetime
from typing import List, Dict, Tuple


def load_json_file(file_path: Path) -> List[Dict]:
    """Load JSON file (handles both standard JSON and JSON Lines format)"""
    print(f"  Loading: {file_path.name}")
    
    questions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # First, try to read entire file as standard JSON
            try:
                content = f.read()
                f.seek(0)
                data = json.loads(content)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    print(f"    OK Loaded {len(data):,} questions (standard JSON)")
                    return data
                elif isinstance(data, dict):
                    # Try common keys
                    for key in ['questions', 'data', 'train', 'test', 'dev']:
                        if key in data:
                            print(f"    OK Loaded {len(data[key]):,} questions (JSON with '{key}' key)")
                            return data[key]
                    # Single question wrapped in dict
                    print(f"    OK Loaded 1 question (single JSON object)")
                    return [data]
                
            except json.JSONDecodeError:
                # If standard JSON fails, try JSON Lines format (one JSON per line)
                f.seek(0)
                line_count = 0
                error_count = 0
                
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            questions.append(json.loads(line))
                            line_count += 1
                        except json.JSONDecodeError as e:
                            error_count += 1
                            if error_count <= 3:  # Only show first 3 errors
                                print(f"    WARNING Line {line_num}: JSON parse error")
                
                if error_count > 3:
                    print(f"    WARNING Total JSON errors: {error_count} lines (skipped)")
                
                if line_count > 0:
                    print(f"    OK Loaded {line_count:,} questions (JSON Lines format)")
                    return questions
        
        if not questions:
            print(f"    WARNING: No data loaded from {file_path.name}")
        
        return questions
        
    except Exception as e:
        print(f"    WARNING: Error loading {file_path.name}: {e}")
        return []


def load_jsonl_file(file_path: Path) -> List[Dict]:
    """Load JSONL file (MedQA format - one JSON per line)"""
    print(f"  Loading: {file_path.name}")
    
    questions = []
    error_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        questions.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        error_count += 1
                        if error_count <= 3:
                            print(f"    WARNING: Line {line_num}: JSON parse error")
        
        if error_count > 3:
            print(f"    WARNING: Total JSON errors: {error_count} lines (skipped)")
        
        if questions:
            print(f"    OK Loaded {len(questions):,} questions")
        else:
            print(f"    WARNING: No questions loaded")
        
        return questions
        
    except Exception as e:
        print(f"    WARNING: Error loading {file_path.name}: {e}")
        return []


def load_medqa_subset(subset_dir: Path, subset_name: str) -> List[Dict]:
    """
    Load all files from a MedQA subset (US, Mainland, Taiwan)
    
    Args:
        subset_dir: Path to subset directory
        subset_name: Name of subset (e.g., "US", "Mainland", "Taiwan")
    
    Returns:
        List of all questions from dev, test, train files
    """
    print(f"\n  Loading MedQA-{subset_name}:")
    
    all_questions = []
    
    # Different file naming conventions by region
    if subset_name == 'USMLE':
        # US MedQA uses phrases_no_exclude_* prefix
        file_names = [
            'phrases_no_exclude_dev.jsonl',
            'phrases_no_exclude_test.jsonl', 
            'phrases_no_exclude_train.jsonl'
        ]
    elif subset_name == 'TWMLE':
        # Taiwan MedQA uses tw_* prefix
        file_names = [
            'tw_dev.jsonl',
            'tw_test.jsonl',
            'tw_train.jsonl'
        ]
    else:
        # Mainland China uses standard naming
        file_names = ['dev.jsonl', 'test.jsonl', 'train.jsonl']
    
    for file_name in file_names:
        file_path = subset_dir / file_name
        if file_path.exists():
            questions = load_jsonl_file(file_path)
            all_questions.extend(questions)
        else:
            print(f"    WARNING: {file_name}: Not found")
    
    print(f"  Total for MedQA-{subset_name}: {len(all_questions):,} questions")
    return all_questions


def load_medmcqa_all(data_dir: Path) -> List[Dict]:
    """
    Load all MedMCQA files (dev, test, train)
    
    Args:
        data_dir: Path to MedMCQA directory
    
    Returns:
        List of all questions from dev, test, train files
    """
    print(f"\n  Loading MedMCQA:")
    
    all_questions = []
    file_names = ['dev.json', 'test.json', 'train.json']
    
    for file_name in file_names:
        file_path = data_dir / file_name
        if file_path.exists():
            questions = load_json_file(file_path)
            all_questions.extend(questions)
        else:
            print(f"    WARNING: {file_name}: Not found")
    
    print(f"  Total for MedMCQA: {len(all_questions):,} questions")
    return all_questions


def process_dataset(data: List[Dict], dataset_name: str, output_dir: Path) -> Tuple[List[Dict], FilterStats]:
    """
    Filter a dataset for respiratory cases
    
    Args:
        data: List of questions
        dataset_name: Name of dataset
        output_dir: Directory to save results
    
    Returns:
        Tuple of (filtered_data, statistics)
    """
    if not data:
        print(f"  WARNING: No data to process for {dataset_name}")
        return [], None
    
    print(f"\n{'='*70}")
    print(f"Filtering: {dataset_name}")
    print(f"{'='*70}")
    print(f"Total questions: {len(data):,}")
    
    # Initialize filter
    filter_pipeline = RespiratoryFilter()
    
    # Filter dataset
    print("Applying respiratory filter...")
    filtered, stats = filter_pipeline.filter_dataset(data, dataset_name)
    
    # Print statistics
    filter_pipeline.print_statistics(dataset_name)
    
    # Save filtered data
    output_file = output_dir / f"{dataset_name.lower().replace(' ', '_').replace('-', '_')}_filtered.json"
    
    save_filtered_dataset(
        filtered,
        str(output_file),
        metadata={
            'source': dataset_name,
            'filter_version': '1.0',
            'icd10_range': 'J00-J99',
            'total_original': len(data),
            'filtered_count': len(filtered),
            'filter_date': datetime.now().isoformat(),
            'paper': 'Paper 1 - Hierarchical Verification Framework'
        }
    )
    
    print(f"OK Saved to: {output_file.name}")
    
    return filtered, stats


def main():
    """
    Main function to process all datasets
    """
    print("\n" + "="*70)
    print("RESPIRATORY DISEASE FILTERING PIPELINE")
    print("Paper 1: Hierarchical Verification Framework")
    print("="*70)
    
    # Define project paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "raw"
    output_dir = project_root / "data" / "filtered"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nData directory: {data_dir}")
    print(f"Output directory: {output_dir}")
    
    # Check if data directory exists
    if not data_dir.exists():
        print(f"\nWARNING: ERROR: Data directory not found: {data_dir}")
        print("Please create data/raw/ directory and add your datasets.")
        return
    
    # ========================================
    # Process MedQA Datasets
    # ========================================
    print(f"\n{'='*70}")
    print("LOADING MEDQA DATASETS")
    print(f"{'='*70}")
    
    medqa_dir = data_dir / "MedQA"
    medqa_datasets = {}
    
    if medqa_dir.exists():
        # Define MedQA subsets
        medqa_subsets = {
            'MedQA-USMLE': medqa_dir / "US",
            'MedQA-MCMLE': medqa_dir / "Mainland",
            'MedQA-TWMLE': medqa_dir / "Taiwan"
        }
        
        # Load each subset
        for subset_name, subset_path in medqa_subsets.items():
            if subset_path.exists():
                data = load_medqa_subset(subset_path, subset_name.split('-')[1])
                if data:
                    medqa_datasets[subset_name] = data
            else:
                print(f"  WARNING: Directory not found: {subset_path}")
    else:
        print(f"  WARNING: MedQA directory not found: {medqa_dir}")
        print(f"  Expected structure: data/raw/MedQA/{{US,Mainland,Taiwan}}/{{dev,test,train}}.jsonl")
    
    # ========================================
    # Process MedMCQA Dataset
    # ========================================
    print(f"\n{'='*70}")
    print("LOADING MEDMCQA DATASET")
    print(f"{'='*70}")
    
    medmcqa_dir = data_dir / "MedMCQA"
    medmcqa_data = None
    
    if medmcqa_dir.exists():
        medmcqa_data = load_medmcqa_all(medmcqa_dir)
        if medmcqa_data:
            medqa_datasets['MedMCQA'] = medmcqa_data
    else:
        print(f"  WARNING: MedMCQA directory not found: {medmcqa_dir}")
        print(f"  Expected structure: data/raw/MedMCQA/{{dev,test,train}}.json")
    
    # ========================================
    # Check if any datasets were loaded
    # ========================================
    if not medqa_datasets:
        print(f"\n{'='*70}")
        print("WARNING: NO DATASETS FOUND")
        print(f"{'='*70}")
        print("\nExpected directory structure:")
        print("data/raw/")
        print("├── MedQA/")
        print("│   ├── US/")
        print("│   │   ├── dev.jsonl")
        print("│   │   ├── test.jsonl")
        print("│   │   └── train.jsonl")
        print("│   ├── Mainland/")
        print("│   │   ├── dev.jsonl")
        print("│   │   ├── test.jsonl")
        print("│   │   └── train.jsonl")
        print("│   └── Taiwan/")
        print("│       ├── dev.jsonl")
        print("│       ├── test.jsonl")
        print("│       └── train.jsonl")
        print("└── MedMCQA/")
        print("    ├── dev.json (or .jsonl)")
        print("    ├── test.json (or .jsonl)")
        print("    └── train.json (or .jsonl)")
        print("\nDataset sources:")
        print("  - MedQA: https://github.com/jind11/MedQA")
        print("  - MedMCQA: https://medmcqa.github.io/")
        return
    
    # ========================================
    # Filter all datasets
    # ========================================
    print(f"\n{'='*70}")
    print("FILTERING DATASETS")
    print(f"{'='*70}")
    
    all_filtered = []
    all_stats = {}
    
    for dataset_name, data in medqa_datasets.items():
        filtered, stats = process_dataset(data, dataset_name, output_dir)
        
        if filtered:
            # Add source information to each question
            for item in filtered:
                item['source_dataset'] = dataset_name
            
            all_filtered.extend(filtered)
            all_stats[dataset_name] = stats
    
    # ========================================
    # Save combined dataset
    # ========================================
    if all_filtered:
        print(f"\n{'='*70}")
        print("SAVING COMBINED DATASET")
        print(f"{'='*70}")
        
        combined_file = output_dir / "respiratory_cases_all.json"
        
        # Calculate per-dataset statistics
        per_dataset_stats = {}
        for name, stats in all_stats.items():
            per_dataset_stats[name] = {
                'total_questions': stats.total_questions,
                'filtered_questions': stats.final_filtered,
                'filter_rate': f"{stats.final_filtered/stats.total_questions*100:.2f}%",
                'metadata_matches': stats.metadata_matches,
                'keyword_matches': stats.keyword_matches
            }
        
        save_filtered_dataset(
            all_filtered,
            str(combined_file),
            metadata={
                'datasets': list(all_stats.keys()),
                'total_cases': len(all_filtered),
                'filter_version': '1.0',
                'icd10_range': 'J00-J99',
                'filter_date': datetime.now().isoformat(),
                'paper': 'Paper 1 - Hierarchical Verification Framework',
                'per_dataset_stats': per_dataset_stats
            }
        )
        
        print(f"OK Combined dataset saved: {combined_file.name}")
        print(f"OK Total respiratory cases: {len(all_filtered):,}")
        
        # ========================================
        # Print summary statistics
        # ========================================
        print(f"\n{'='*70}")
        print("SUMMARY STATISTICS")
        print(f"{'='*70}")
        
        print(f"\n{'Dataset':<20} {'Total':<12} {'Filtered':<12} {'Rate':<10}")
        print("-" * 70)
        
        total_original = 0
        total_filtered = 0
        
        # Sort datasets for consistent display
        dataset_order = ['MedQA-USMLE', 'MedQA-MCMLE', 'MedQA-TWMLE', 'MedMCQA']
        
        for dataset_name in dataset_order:
            if dataset_name in all_stats:
                stats = all_stats[dataset_name]
                total_original += stats.total_questions
                total_filtered += stats.final_filtered
                rate = stats.final_filtered / stats.total_questions * 100
                
                print(f"{dataset_name:<20} {stats.total_questions:>10,}  "
                      f"{stats.final_filtered:>10,}  {rate:>8.2f}%")
        
        print("-" * 70)
        print(f"{'TOTAL':<20} {total_original:>10,}  "
              f"{total_filtered:>10,}  {total_filtered/total_original*100:>8.2f}%")
        print("=" * 70)
        
        # ========================================
        # Validation check
        # ========================================
        print(f"\n{'='*70}")
        print("VALIDATION CHECK")
        print(f"{'='*70}")
        
        target_min = 1200
        target_max = 1500
        
        print(f"\nTarget range: {target_min:,} - {target_max:,} cases")
        print(f"Actual count: {len(all_filtered):,} cases")
        
        if target_min <= len(all_filtered) <= target_max:
            print(f"\nOK PASS: Within target range!")
            status = "READY FOR EXPERIMENTS"
        elif len(all_filtered) < target_min:
            print(f"\nWARNING: WARNING: Below target range")
            print(f"  Short by: {target_min - len(all_filtered):,} cases")
            status = "NEEDS MORE DATA"
        else:
            print(f"\nOK ABOVE TARGET: Exceeds target range")
            print(f"  Extra: {len(all_filtered) - target_max:,} cases")
            print(f"  This is fine - more data is better!")
            status = "READY FOR EXPERIMENTS"
        
        # ========================================
        # Final summary
        # ========================================
        print(f"\n{'='*70}")
        print("FILTERING COMPLETE")
        print(f"{'='*70}")
        print(f"\nOK Status: {status}")
        print(f"OK Filtered datasets saved to: {output_dir}")
        print(f"\nGenerated files:")
        for dataset_name in all_stats.keys():
            filename = f"{dataset_name.lower().replace(' ', '_').replace('-', '_')}_filtered.json"
            print(f"  - {filename}")
        print(f"  - respiratory_cases_all.json (combined)")
        
        print(f"\n{'='*70}")
        print("NEXT STEPS")
        print(f"{'='*70}")
        print("1. Review filtered data quality")
        print("2. Validate sample cases manually (recommended: 30 random samples)")
        print("3. Begin multi-agent system implementation (January 2025)")
        print("4. Commit and push to GitHub")
        print(f"\nTo commit:")
        print(f"  git add data/filtered/")
        print(f"  git commit -m 'Add filtered respiratory disease datasets'")
        print(f"  git push")
        
    else:
        print("\nWARNING: ERROR: No data was filtered")
        print("Please check your dataset files and try again.")


if __name__ == "__main__":
    main()