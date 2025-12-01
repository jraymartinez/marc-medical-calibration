"""
Dataset Filtering Script for Paper 1
Filters MedQA and MedMCQA datasets for respiratory disease cases

Dataset Structure:
- MedQA: 3 folders (Mainland, Taiwan, US) × 3 files (dev, test, train) = 9 JSONL files
- MedMCQA: 3 files (dev, test, train) = 3 JSON/JSONL files

Logging:
- All output is saved to: results/filtering_log_YYYYMMDD_HHMMSS.txt
- Console output is also displayed in real-time
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


class Logger:
    """Logger that writes to both console and file simultaneously"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create/overwrite log file with header
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("RESPIRATORY DISEASE FILTERING PIPELINE - EXECUTION LOG\n")
            f.write("="*70 + "\n")
            f.write(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Log File: {self.log_file}\n")
            f.write("="*70 + "\n\n")
    
    def log(self, message: str = "", to_console: bool = True, to_file: bool = True):
        """Write message to console and/or file"""
        if to_console:
            print(message)
        
        if to_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
    
    def section(self, title: str):
        """Write section header"""
        self.log("\n" + "="*70)
        self.log(title)
        self.log("="*70)
    
    def subsection(self, title: str):
        """Write subsection header"""
        self.log(f"\n{title}")
        self.log("-"*70)
    
    def finalize(self):
        """Write log footer"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*70 + "\n")
            f.write(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n")


def load_json_file(file_path: Path, logger: Logger) -> List[Dict]:
    """Load JSON file (handles both standard JSON and JSON Lines format)"""
    logger.log(f"  Loading: {file_path.name}")
    
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
                    logger.log(f"    ✓ Loaded {len(data):,} questions (standard JSON)")
                    return data
                elif isinstance(data, dict):
                    # Try common keys
                    for key in ['questions', 'data', 'train', 'test', 'dev']:
                        if key in data:
                            logger.log(f"    ✓ Loaded {len(data[key]):,} questions (JSON with '{key}' key)")
                            return data[key]
                    # Single question wrapped in dict
                    logger.log(f"    ✓ Loaded 1 question (single JSON object)")
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
                                logger.log(f"    ⚠ Line {line_num}: JSON parse error")
                
                if error_count > 3:
                    logger.log(f"    ⚠ Total JSON errors: {error_count} lines (skipped)")
                
                if line_count > 0:
                    logger.log(f"    ✓ Loaded {line_count:,} questions (JSON Lines format)")
                    return questions
        
        if not questions:
            logger.log(f"    ⚠ No data loaded from {file_path.name}")
        
        return questions
        
    except Exception as e:
        logger.log(f"    ⚠ Error loading {file_path.name}: {e}")
        return []


def load_jsonl_file(file_path: Path, logger: Logger) -> List[Dict]:
    """Load JSONL file (MedQA format - one JSON per line)"""
    logger.log(f"  Loading: {file_path.name}")
    
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
                            logger.log(f"    ⚠ Line {line_num}: JSON parse error")
        
        if error_count > 3:
            logger.log(f"    ⚠ Total JSON errors: {error_count} lines (skipped)")
        
        if questions:
            logger.log(f"    ✓ Loaded {len(questions):,} questions")
        else:
            logger.log(f"    ⚠ No questions loaded")
        
        return questions
        
    except Exception as e:
        logger.log(f"    ⚠ Error loading {file_path.name}: {e}")
        return []


def load_medqa_subset(subset_dir: Path, subset_name: str, logger: Logger) -> List[Dict]:
    """
    Load all files from a MedQA subset (US, Mainland, Taiwan)
    """
    logger.log(f"\n  Loading MedQA-{subset_name}:")
    
    all_questions = []
    
    # Taiwan uses different filenames (tw_*.jsonl)
    if subset_name == 'TWMLE':
        file_names = ['tw_dev.jsonl', 'tw_test.jsonl', 'tw_train.jsonl']
    # US uses phrases_no_exclude_*.jsonl
    elif subset_name == 'USMLE':
        file_names = ['phrases_no_exclude_dev.jsonl', 'phrases_no_exclude_test.jsonl', 'phrases_no_exclude_train.jsonl']
    else:
        # Mainland uses standard naming
        file_names = ['dev.jsonl', 'test.jsonl', 'train.jsonl']
    
    for file_name in file_names:
        file_path = subset_dir / file_name
        if file_path.exists():
            questions = load_jsonl_file(file_path, logger)
            all_questions.extend(questions)
        else:
            logger.log(f"    ⚠ {file_name}: Not found")
    
    logger.log(f"  Total for MedQA-{subset_name}: {len(all_questions):,} questions")
    return all_questions


def load_medmcqa_all(data_dir: Path, logger: Logger) -> List[Dict]:
    """
    Load all MedMCQA files (dev, test, train)
    """
    logger.log(f"\n  Loading MedMCQA:")
    
    all_questions = []
    file_names = ['dev.json', 'test.json', 'train.json']
    
    for file_name in file_names:
        file_path = data_dir / file_name
        if file_path.exists():
            questions = load_json_file(file_path, logger)
            all_questions.extend(questions)
        else:
            logger.log(f"    ⚠ {file_name}: Not found")
    
    logger.log(f"  Total for MedMCQA: {len(all_questions):,} questions")
    return all_questions


def process_dataset(data: List[Dict], dataset_name: str, output_dir: Path, logger: Logger) -> Tuple[List[Dict], FilterStats]:
    """
    Filter a dataset for respiratory cases
    """
    if not data:
        logger.log(f"  ⚠ No data to process for {dataset_name}")
        return [], None
    
    logger.section(f"Filtering: {dataset_name}")
    logger.log(f"Total questions: {len(data):,}")
    
    # Initialize filter
    filter_pipeline = RespiratoryFilter()
    
    # Filter dataset
    logger.log("Applying respiratory filter...")
    filtered, stats = filter_pipeline.filter_dataset(data, dataset_name)
    
    # Capture statistics output
    logger.log("")  # Blank line before stats
    logger.log("="*60)
    logger.log(f"Respiratory Filter Statistics - {dataset_name}")
    logger.log("="*60)
    logger.log(f"Total Questions:        {stats.total_questions:,}")
    logger.log(f"Filtered (Respiratory): {stats.final_filtered:,} "
               f"({stats.final_filtered/stats.total_questions*100:.1f}%)")
    logger.log(f"\nMatching Methods:")
    logger.log(f"  Metadata Matches:     {stats.metadata_matches:,}")
    logger.log(f"  Keyword Matches:      {stats.keyword_matches:,}")
    
    if stats.by_disease:
        logger.log(f"\nTop Disease Keywords:")
        sorted_diseases = sorted(stats.by_disease.items(), 
                               key=lambda x: x[1], reverse=True)[:10]
        for disease, count in sorted_diseases:
            logger.log(f"  {disease:30s}: {count:4d}")
    
    if stats.by_symptom:
        logger.log(f"\nTop Symptom Keywords:")
        sorted_symptoms = sorted(stats.by_symptom.items(), 
                               key=lambda x: x[1], reverse=True)[:10]
        for symptom, count in sorted_symptoms:
            logger.log(f"  {symptom:30s}: {count:4d}")
    
    logger.log("="*60)
    
    # Save filtered data
    output_file = output_dir / f"{dataset_name.lower().replace(' ', '_').replace('-', '_')}_filtered.json"
    
    save_filtered_dataset(
        filtered,
        str(output_file),
        metadata={
            'source': dataset_name,
            'filter_version': '2.0',
            'filter_method': 'Hybrid: Metadata + Keywords',
            'respiratory_scope': 'ICD-10 J00-J99 (Respiratory System)',
            'total_original': len(data),
            'filtered_count': len(filtered),
            'filter_date': datetime.now().isoformat(),
            'paper': 'Paper 1 - Hierarchical Verification Framework'
        }
    )
    
    logger.log(f"\n✓ Saved to: {output_file.name}")
    
    return filtered, stats


def main():
    """
    Main function to process all datasets
    """
    # Create log file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = project_root / "results"
    log_file = log_dir / f"filtering_log_{timestamp}.txt"
    
    # Initialize logger
    logger = Logger(log_file)
    
    logger.section("RESPIRATORY DISEASE FILTERING PIPELINE")
    logger.log("Paper 1: Hierarchical Verification Framework")
    
    # Define project paths
    data_dir = project_root / "data" / "raw"
    output_dir = project_root / "data" / "filtered"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.log(f"\nData directory: {data_dir}")
    logger.log(f"Output directory: {output_dir}")
    logger.log(f"Log file: {log_file}")
    
    # Check if data directory exists
    if not data_dir.exists():
        logger.log(f"\n⚠ ERROR: Data directory not found: {data_dir}")
        logger.log("Please create data/raw/ directory and add your datasets.")
        logger.finalize()
        return
    
    # ========================================
    # Process MedQA Datasets
    # ========================================
    logger.section("LOADING MEDQA DATASETS")
    
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
                data = load_medqa_subset(subset_path, subset_name.split('-')[1], logger)
                if data:
                    medqa_datasets[subset_name] = data
            else:
                logger.log(f"  ⚠ Directory not found: {subset_path}")
    else:
        logger.log(f"  ⚠ MedQA directory not found: {medqa_dir}")
        logger.log(f"  Expected structure: data/raw/MedQA/{{US,Mainland,Taiwan}}/{{dev,test,train}}.jsonl")
    
    # ========================================
    # Process MedMCQA Dataset
    # ========================================
    logger.section("LOADING MEDMCQA DATASET")
    
    medmcqa_dir = data_dir / "MedMCQA"
    
    if medmcqa_dir.exists():
        medmcqa_data = load_medmcqa_all(medmcqa_dir, logger)
        if medmcqa_data:
            medqa_datasets['MedMCQA'] = medmcqa_data
    else:
        logger.log(f"  ⚠ MedMCQA directory not found: {medmcqa_dir}")
        logger.log(f"  Expected structure: data/raw/MedMCQA/{{dev,test,train}}.json")
    
    # ========================================
    # Check if any datasets were loaded
    # ========================================
    if not medqa_datasets:
        logger.section("⚠ NO DATASETS FOUND")
        logger.log("\nExpected directory structure:")
        logger.log("data/raw/")
        logger.log("├── MedQA/")
        logger.log("│   ├── US/")
        logger.log("│   │   ├── dev.jsonl")
        logger.log("│   │   ├── test.jsonl")
        logger.log("│   │   └── train.jsonl")
        logger.log("│   ├── Mainland/")
        logger.log("│   │   ├── dev.jsonl")
        logger.log("│   │   ├── test.jsonl")
        logger.log("│   │   └── train.jsonl")
        logger.log("│   └── Taiwan/")
        logger.log("│       ├── dev.jsonl")
        logger.log("│       ├── test.jsonl")
        logger.log("│       └── train.jsonl")
        logger.log("└── MedMCQA/")
        logger.log("    ├── dev.json (or .jsonl)")
        logger.log("    ├── test.json (or .jsonl)")
        logger.log("    └── train.json (or .jsonl)")
        logger.log("\nDataset sources:")
        logger.log("  - MedQA: https://github.com/jind11/MedQA")
        logger.log("  - MedMCQA: https://medmcqa.github.io/")
        logger.finalize()
        return
    
    # ========================================
    # Filter all datasets
    # ========================================
    logger.section("FILTERING DATASETS")
    
    all_filtered = []
    all_stats = {}
    
    for dataset_name, data in medqa_datasets.items():
        filtered, stats = process_dataset(data, dataset_name, output_dir, logger)
        
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
        logger.section("SAVING COMBINED DATASET")
        
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
                'filter_version': '2.0',
                'filter_method': 'Hybrid: Metadata + Keywords',
                'respiratory_scope': 'ICD-10 J00-J99 (Respiratory System)',
                'filter_date': datetime.now().isoformat(),
                'paper': 'Paper 1 - Hierarchical Verification Framework',
                'per_dataset_stats': per_dataset_stats
            }
        )
        
        logger.log(f"\n✓ Combined dataset saved: {combined_file.name}")
        logger.log(f"✓ Total respiratory cases: {len(all_filtered):,}")
        
        # ========================================
        # Print summary statistics
        # ========================================
        logger.section("SUMMARY STATISTICS")
        
        logger.log(f"\n{'Dataset':<20} {'Total':<12} {'Filtered':<12} {'Rate':<10}")
        logger.log("-" * 70)
        
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
                
                logger.log(f"{dataset_name:<20} {stats.total_questions:>10,}  "
                          f"{stats.final_filtered:>10,}  {rate:>8.2f}%")
        
        logger.log("-" * 70)
        logger.log(f"{'TOTAL':<20} {total_original:>10,}  "
                  f"{total_filtered:>10,}  {total_filtered/total_original*100:>8.2f}%")
        logger.log("=" * 70)
        
        # ========================================
        # Validation check
        # ========================================
        logger.section("VALIDATION CHECK")
        
        target_min = 1200
        target_max = 1500
        
        logger.log(f"\nTarget range: {target_min:,} - {target_max:,} cases")
        logger.log(f"Actual count: {len(all_filtered):,} cases")
        
        if target_min <= len(all_filtered) <= target_max:
            logger.log(f"\n✓ PASS: Within target range!")
            status = "READY FOR EXPERIMENTS"
        elif len(all_filtered) < target_min:
            logger.log(f"\n⚠ WARNING: Below target range")
            logger.log(f"  Short by: {target_min - len(all_filtered):,} cases")
            status = "NEEDS MORE DATA"
        else:
            logger.log(f"\n✓ ABOVE TARGET: Exceeds target range")
            logger.log(f"  Extra: {len(all_filtered) - target_max:,} cases")
            logger.log(f"  This is fine - more data is better!")
            status = "READY FOR EXPERIMENTS"
        
        # ========================================
        # Final summary
        # ========================================
        logger.section("FILTERING COMPLETE")
        logger.log(f"\n✓ Status: {status}")
        logger.log(f"✓ Filtered datasets saved to: {output_dir}")
        logger.log(f"\nGenerated files:")
        for dataset_name in all_stats.keys():
            filename = f"{dataset_name.lower().replace(' ', '_').replace('-', '_')}_filtered.json"
            logger.log(f"  - {filename}")
        logger.log(f"  - respiratory_cases_all.json (combined)")
        
        logger.section("NEXT STEPS")
        logger.log("1. Review filtered data quality")
        logger.log("2. Validate sample cases manually (recommended: 30 random samples)")
        logger.log("3. Begin multi-agent system implementation (January 2025)")
        logger.log("4. Commit and push to GitHub")
        logger.log(f"\nTo commit:")
        logger.log(f"  git add data/filtered/ results/")
        logger.log(f"  git commit -m 'Add filtered respiratory disease datasets'")
        logger.log(f"  git push")
        
        logger.log(f"\n✓ Complete log saved to: {log_file}")
        
    else:
        logger.log("\n⚠ ERROR: No data was filtered")
        logger.log("Please check your dataset files and try again.")
    
    # Finalize log
    logger.finalize()


if __name__ == "__main__":
    main()