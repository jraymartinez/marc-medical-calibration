"""
Respiratory Disease Filtering Pipeline
Filters medical question datasets (MedQA, MedMCQA) for respiratory disease cases
using ICD-10 codes and keyword matching.

Version: 1.1
- Refined keywords to reduce false positives
- Added primary/secondary keyword distinction
- Improved matching logic requiring disease/symptom/diagnostic keywords
"""

import json
import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FilterStats:
    """Statistics for the filtering process"""
    total_questions: int = 0
    icd10_matches: int = 0
    keyword_matches: int = 0
    final_filtered: int = 0
    by_disease: Dict[str, int] = None
    by_symptom: Dict[str, int] = None
    
    def __post_init__(self):
        if self.by_disease is None:
            self.by_disease = {}
        if self.by_symptom is None:
            self.by_symptom = {}


class RespiratoryFilter:
    """
    Filters medical datasets for respiratory disease cases using:
    1. ICD-10 Chapter X (J00-J99) codes
    2. Keyword matching for respiratory terms (disease, symptom, diagnostic, anatomical)
    
    Filtering Logic:
    - Must match ICD-10 code OR primary keywords (disease/symptom/diagnostic)
    - Anatomical keywords alone are insufficient
    - Keywords are specific to respiratory conditions
    """
    
    # ICD-10 Chapter X (J00-J99): Diseases of the respiratory system
    ICD10_RANGES = {
        'J00-J06': 'Acute upper respiratory infections',
        'J20-J22': 'Lower respiratory infections', 
        'J40-J47': 'Chronic lower respiratory diseases (COPD, asthma)',
        'J60-J70': 'Lung diseases due to external agents',
        'J80-J84': 'Respiratory failure, ARDS'
    }
    
    # Disease keywords - SPECIFIC respiratory diseases only
    # Removed generic terms that appear in non-respiratory contexts
    DISEASE_KEYWORDS = {
        # Common respiratory diseases
        'pneumonia', 'asthma', 'copd', 'bronchitis', 'tuberculosis',
        'emphysema', 'bronchiectasis',
        
        # Respiratory failure and acute conditions
        'respiratory failure', 'ards', 
        'acute respiratory distress syndrome',
        
        # Pulmonary vascular and structural
        'pulmonary embolism', 'pulmonary edema',
        'pulmonary fibrosis', 'interstitial lung disease',
        
        # Chronic conditions
        'chronic obstructive pulmonary disease',
        'cystic fibrosis', 'bronchiolitis',
        
        # Other specific respiratory diseases
        'mesothelioma', 'sarcoidosis',
        'respiratory syncytial virus', 'rsv',
        'pertussis', 'whooping cough',
        
        # Pneumonia variants (more specific)
        'bacterial pneumonia', 'viral pneumonia',
        'aspiration pneumonia', 'atypical pneumonia'
    }
    
    # Symptom keywords - SPECIFIC to respiratory
    # Removed generic symptoms like 'cough' alone
    SYMPTOM_KEYWORDS = {
        # Specific respiratory symptoms
        'dyspnea', 'wheeze', 'wheezing', 'hemoptysis', 
        'stridor', 'tachypnea',
        
        # Oxygen-related (very specific)
        'hypoxia', 'hypoxemia', 
        
        # Descriptive breathing symptoms
        'shortness of breath', 'difficulty breathing',
        'respiratory distress',
        
        # Specific cough descriptions (not just "cough")
        'productive cough', 'nonproductive cough', 
        'chronic cough', 'persistent cough',
        
        # Breathing patterns
        'labored breathing', 'rapid breathing'
    }
    
    # Diagnostic keywords - SPECIFIC respiratory tests and procedures
    DIAGNOSTIC_KEYWORDS = {
        # Pulmonary function tests
        'spirometry', 'pulmonary function test', 'pft',
        'peak flow', 'fev1', 'fvc', 'fev1/fvc',
        
        # Imaging (when combined with respiratory context)
        'chest x-ray', 'chest xray', 'chest radiograph',
        
        # Blood gases
        'arterial blood gas', 'abg', 
        
        # Oxygen measurement
        'pulse oximetry', 'oxygen saturation', 'spo2',
        
        # Procedures
        'bronchoscopy', 'lung biopsy', 
        'sputum culture', 'sputum analysis',
        'thoracentesis', 'chest tube',
        
        # Specialized tests
        'ventilation perfusion scan', 'v/q scan',
        'diffusing capacity', 'dlco'
    }
    
    # Anatomical keywords - Secondary (require primary keyword match)
    # These alone won't trigger a match
    ANATOMICAL_KEYWORDS = {
        # Specific respiratory anatomy
        'bronchi', 'bronchus', 'bronchial',
        'alveoli', 'alveolar',
        'pleura', 'pleural', 'pleural effusion',
        'trachea', 'tracheal',
        'bronchioles', 'bronchiolar',
        
        # Respiratory tract terms
        'respiratory tract', 'upper respiratory tract',
        'lower respiratory tract'
    }
    
    def __init__(self):
        """Initialize the filter with combined keyword set"""
        # Primary keywords that can trigger a match
        self.primary_keywords = (
            self.DISEASE_KEYWORDS | 
            self.SYMPTOM_KEYWORDS | 
            self.DIAGNOSTIC_KEYWORDS
        )
        
        # All keywords including anatomical (for metadata)
        self.all_keywords = self.primary_keywords | self.ANATOMICAL_KEYWORDS
        
        self.stats = FilterStats()
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for matching
        
        Args:
            text: Input text
            
        Returns:
            Normalized lowercase text
        """
        return text.lower().strip()
    
    def _extract_icd10_codes(self, text: str) -> Set[str]:
        """
        Extract ICD-10 codes from text
        
        Matches patterns like:
        - J00 (2 digits)
        - J20.1 (2 digits + decimal + 1-2 digits)
        - J45.9 (2 digits + decimal + 1-2 digits)
        
        Args:
            text: Text to search for ICD-10 codes
            
        Returns:
            Set of found ICD-10 codes
        """
        # Match patterns like J00, J20.1, J45.9
        pattern = r'\bJ\d{2}(?:\.\d{1,2})?\b'
        matches = re.findall(pattern, text.upper())
        return set(matches)
    
    def _is_respiratory_icd10(self, code: str) -> bool:
        """
        Check if ICD-10 code is in respiratory range (J00-J99)
        
        Args:
            code: ICD-10 code to check
            
        Returns:
            True if code is in respiratory range, False otherwise
        """
        if not code or not code.startswith('J'):
            return False
        
        try:
            # Extract numeric part (e.g., "J20.1" -> 20)
            numeric = int(code[1:3])
            return 0 <= numeric <= 99
        except (ValueError, IndexError):
            return False
    
    def _matches_keywords(self, text: str) -> Tuple[bool, Set[str]]:
        """
        Check if text matches respiratory keywords
        
        NEW LOGIC (v1.1):
        - Must match at least one PRIMARY keyword (disease/symptom/diagnostic)
        - Anatomical keywords alone are NOT sufficient
        - This reduces false positives from generic anatomical mentions
        
        Args:
            text: Text to search for keywords
            
        Returns:
            Tuple of (has_match, set of all matched keywords)
        """
        normalized = self._normalize_text(text)
        matched_keywords = set()
        matched_primary = set()
        
        # Check all keywords
        for keyword in self.all_keywords:
            # Use word boundaries for accurate matching
            # This prevents matching "coughing" when looking for "cough"
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, normalized):
                matched_keywords.add(keyword)
                
                # Track if this is a primary keyword
                if keyword in self.primary_keywords:
                    matched_primary.add(keyword)
        
        # Must have at least one primary keyword match
        # (disease, symptom, or diagnostic - not just anatomical)
        has_match = len(matched_primary) > 0
        
        return has_match, matched_keywords
    
    def _categorize_matches(self, matched_keywords: Set[str]) -> Dict[str, List[str]]:
        """
        Categorize matched keywords by type
        
        Args:
            matched_keywords: Set of matched keywords
            
        Returns:
            Dictionary with categorized keywords
        """
        categorized = {
            'diseases': [],
            'symptoms': [],
            'diagnostic': [],
            'anatomical': []
        }
        
        for keyword in matched_keywords:
            if keyword in self.DISEASE_KEYWORDS:
                categorized['diseases'].append(keyword)
            if keyword in self.SYMPTOM_KEYWORDS:
                categorized['symptoms'].append(keyword)
            if keyword in self.DIAGNOSTIC_KEYWORDS:
                categorized['diagnostic'].append(keyword)
            if keyword in self.ANATOMICAL_KEYWORDS:
                categorized['anatomical'].append(keyword)
        
        return categorized
    
    def filter_question(self, question_data: Dict) -> Tuple[bool, Dict]:
        """
        Filter a single question for respiratory relevance
        
        Args:
            question_data: Dictionary with 'question', 'options', 'answer', etc.
            
        Returns:
            Tuple of (is_respiratory, metadata_dict)
            
        Example:
            >>> filter_pipeline = RespiratoryFilter()
            >>> question = {'question': 'Patient with COPD...', 'answer': 'A'}
            >>> is_respiratory, metadata = filter_pipeline.filter_question(question)
        """
        # Combine all text fields for analysis
        text_parts = [
            question_data.get('question', ''),
            str(question_data.get('options', '')),
            str(question_data.get('explanation', ''))
        ]
        full_text = ' '.join(text_parts)
        
        # Extract ICD-10 codes
        icd10_codes = self._extract_icd10_codes(full_text)
        respiratory_codes = [code for code in icd10_codes if self._is_respiratory_icd10(code)]
        
        # Check keyword matches
        has_keywords, matched_keywords = self._matches_keywords(full_text)
        
        # Determine if question is respiratory-related
        # Either has ICD-10 code OR primary keywords
        is_respiratory = len(respiratory_codes) > 0 or has_keywords
        
        # Build metadata
        metadata = {
            'icd10_codes': respiratory_codes,
            'matched_keywords': list(matched_keywords),
            'match_type': []
        }
        
        if respiratory_codes:
            metadata['match_type'].append('icd10')
        if has_keywords:
            metadata['match_type'].append('keywords')
        
        # Categorize matched keywords
        if matched_keywords:
            categorized = self._categorize_matches(matched_keywords)
            metadata['keyword_categories'] = categorized
        
        return is_respiratory, metadata
    
    def filter_dataset(self, dataset: List[Dict], 
                      dataset_name: str = "Unknown") -> Tuple[List[Dict], FilterStats]:
        """
        Filter entire dataset for respiratory cases
        
        Args:
            dataset: List of question dictionaries
            dataset_name: Name of the dataset (for statistics)
            
        Returns:
            Tuple of (filtered_questions, statistics)
            
        Example:
            >>> filter_pipeline = RespiratoryFilter()
            >>> filtered, stats = filter_pipeline.filter_dataset(medqa_data, "MedQA")
            >>> filter_pipeline.print_statistics("MedQA")
        """
        filtered = []
        stats = FilterStats()
        stats.total_questions = len(dataset)
        
        for question in dataset:
            is_respiratory, metadata = self.filter_question(question)
            
            if is_respiratory:
                # Add metadata to question
                question['respiratory_metadata'] = metadata
                filtered.append(question)
                
                stats.final_filtered += 1
                
                # Update statistics
                if 'icd10' in metadata['match_type']:
                    stats.icd10_matches += 1
                if 'keywords' in metadata['match_type']:
                    stats.keyword_matches += 1
                
                # Track disease and symptom frequencies
                if 'keyword_categories' in metadata:
                    for disease in metadata['keyword_categories'].get('diseases', []):
                        stats.by_disease[disease] = stats.by_disease.get(disease, 0) + 1
                    for symptom in metadata['keyword_categories'].get('symptoms', []):
                        stats.by_symptom[symptom] = stats.by_symptom.get(symptom, 0) + 1
        
        self.stats = stats
        return filtered, stats
    
    def print_statistics(self, dataset_name: str = "Dataset"):
        """
        Print filtering statistics
        
        Args:
            dataset_name: Name of dataset for display
        """
        stats = self.stats
        
        print(f"\n{'='*60}")
        print(f"Respiratory Filter Statistics - {dataset_name}")
        print(f"{'='*60}")
        print(f"Total Questions:        {stats.total_questions:,}")
        print(f"Filtered (Respiratory): {stats.final_filtered:,} "
              f"({stats.final_filtered/stats.total_questions*100:.1f}%)")
        print(f"\nMatching Methods:")
        print(f"  ICD-10 Matches:       {stats.icd10_matches:,}")
        print(f"  Keyword Matches:      {stats.keyword_matches:,}")
        
        if stats.by_disease:
            print(f"\nTop Disease Keywords:")
            sorted_diseases = sorted(stats.by_disease.items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
            for disease, count in sorted_diseases:
                print(f"  {disease:30s}: {count:4d}")
        
        if stats.by_symptom:
            print(f"\nTop Symptom Keywords:")
            sorted_symptoms = sorted(stats.by_symptom.items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
            for symptom, count in sorted_symptoms:
                print(f"  {symptom:30s}: {count:4d}")
        
        print(f"{'='*60}\n")


def load_medqa_dataset(file_path: str) -> List[Dict]:
    """
    Load MedQA dataset from JSON file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of question dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # MedQA format varies, handle common structures
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Try common keys
        for key in ['questions', 'data', 'train', 'test', 'dev']:
            if key in data:
                return data[key]
    
    return []


def load_medmcqa_dataset(file_path: str) -> List[Dict]:
    """
    Load MedMCQA dataset from JSON/JSONL file
    
    Args:
        file_path: Path to JSON or JSONL file
        
    Returns:
        List of question dictionaries
    """
    questions = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Try JSONL format first (one JSON per line)
        try:
            for line in f:
                if line.strip():
                    questions.append(json.loads(line))
            return questions
        except json.JSONDecodeError:
            # Try regular JSON
            f.seek(0)
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                for key in ['questions', 'data']:
                    if key in data:
                        return data[key]
    
    return questions


def save_filtered_dataset(filtered_data: List[Dict], 
                         output_path: str,
                         metadata: Dict = None):
    """
    Save filtered dataset with metadata
    
    Args:
        filtered_data: List of filtered questions
        output_path: Path to save JSON file
        metadata: Optional metadata dictionary
    """
    output = {
        'metadata': metadata or {},
        'filtered_questions': filtered_data,
        'count': len(filtered_data)
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(filtered_data)} filtered questions to {output_path}")


def main():
    """
    Example usage of the filtering pipeline
    Demonstrates basic functionality with placeholder paths
    """
    
    print("Respiratory Disease Filtering Pipeline v1.1")
    print("=" * 60)
    
    # Initialize filter
    filter_pipeline = RespiratoryFilter()
    
    print(f"\nFilter Configuration:")
    print(f"  Total keywords: {len(filter_pipeline.all_keywords)}")
    print(f"  Primary keywords: {len(filter_pipeline.primary_keywords)}")
    print(f"    - Diseases: {len(filter_pipeline.DISEASE_KEYWORDS)}")
    print(f"    - Symptoms: {len(filter_pipeline.SYMPTOM_KEYWORDS)}")
    print(f"    - Diagnostic: {len(filter_pipeline.DIAGNOSTIC_KEYWORDS)}")
    print(f"  Anatomical keywords: {len(filter_pipeline.ANATOMICAL_KEYWORDS)}")
    
    # Example: Process MedQA dataset
    print("\nProcessing MedQA dataset...")
    try:
        # Adjust path to your dataset location
        medqa_data = load_medqa_dataset('medqa_dataset.json')
        
        if medqa_data:
            filtered_medqa, stats = filter_pipeline.filter_dataset(
                medqa_data, 
                dataset_name="MedQA"
            )
            filter_pipeline.print_statistics("MedQA")
            
            # Save filtered data
            save_filtered_dataset(
                filtered_medqa,
                'medqa_respiratory_filtered.json',
                metadata={
                    'source': 'MedQA',
                    'filter_version': '1.1',
                    'icd10_range': 'J00-J99',
                    'total_original': len(medqa_data)
                }
            )
    except FileNotFoundError:
        print("  MedQA dataset file not found (expected 'medqa_dataset.json')")
        print("  Use scripts/filter_datasets.py for full dataset processing")
    
    # Example: Process MedMCQA dataset
    print("\nProcessing MedMCQA dataset...")
    try:
        medmcqa_data = load_medmcqa_dataset('medmcqa_dataset.json')
        
        if medmcqa_data:
            filtered_medmcqa, stats = filter_pipeline.filter_dataset(
                medmcqa_data,
                dataset_name="MedMCQA"
            )
            filter_pipeline.print_statistics("MedMCQA")
            
            save_filtered_dataset(
                filtered_medmcqa,
                'medmcqa_respiratory_filtered.json',
                metadata={
                    'source': 'MedMCQA',
                    'filter_version': '1.1',
                    'icd10_range': 'J00-J99',
                    'total_original': len(medmcqa_data)
                }
            )
    except FileNotFoundError:
        print("  MedMCQA dataset file not found (expected 'medmcqa_dataset.json')")
        print("  Use scripts/filter_datasets.py for full dataset processing")
    
    print("\nFiltering pipeline completed!")
    print("\nFor full dataset processing, use: python scripts/filter_datasets.py")


if __name__ == "__main__":
    main()