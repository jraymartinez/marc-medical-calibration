"""
Test Suite for Respiratory Disease Filtering Pipeline
"""

import unittest
import sys
from pathlib import Path

# Add src to path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from filtering.respiratory_filter import RespiratoryFilter, FilterStats


class TestRespiratoryFilter(unittest.TestCase):
    """Test cases for RespiratoryFilter class"""
    
    def setUp(self):
        """Set up test filter instance"""
        self.filter = RespiratoryFilter()
    
    def test_icd10_extraction(self):
        """Test ICD-10 code extraction"""
        test_cases = [
            ("Patient has J45.9 asthma", {"J45.9"}),
            ("Diagnosed with J20 and J44.1", {"J20", "J44.1"}),
            ("No respiratory codes here M79.3", set()),
            ("ICD-10: J18.9, J96.0", {"J18.9", "J96.0"}),
        ]
        
        for text, expected in test_cases:
            result = self.filter._extract_icd10_codes(text)
            self.assertEqual(result, expected, 
                           f"Failed for: {text}")
    
    def test_is_respiratory_icd10(self):
        """Test respiratory ICD-10 code validation"""
        respiratory_codes = ["J00", "J45.9", "J96", "J84.1"]
        non_respiratory_codes = ["M79.3", "I50.9", "K21.9", "A15.0"]
        
        for code in respiratory_codes:
            self.assertTrue(self.filter._is_respiratory_icd10(code),
                          f"{code} should be respiratory")
        
        for code in non_respiratory_codes:
            self.assertFalse(self.filter._is_respiratory_icd10(code),
                           f"{code} should not be respiratory")
    
    def test_keyword_matching(self):
        """Test keyword matching"""
        test_cases = [
            ("Patient presents with cough and dyspnea", True),
            ("Diagnosed with pneumonia", True),
            ("COPD exacerbation with wheezing", True),
            ("Patient has diabetes mellitus", False),
            ("Chest X-ray shows infiltrates", True),
            ("Spirometry results abnormal", True),
        ]
        
        for text, should_match in test_cases:
            matches, keywords = self.filter._matches_keywords(text)
            self.assertEqual(matches, should_match,
                           f"Failed for: {text}")
            if should_match:
                self.assertGreater(len(keywords), 0)
    
    def test_filter_question_with_icd10(self):
        """Test filtering question with ICD-10 code"""
        question = {
            'question': 'A patient with J45.9 presents with acute symptoms.',
            'options': ['A', 'B', 'C', 'D'],
            'answer': 'A'
        }
        
        is_respiratory, metadata = self.filter.filter_question(question)
        
        self.assertTrue(is_respiratory)
        self.assertIn('icd10', metadata['match_type'])
        self.assertIn('J45.9', metadata['icd10_codes'])
    
    def test_filter_question_with_keywords(self):
        """Test filtering question with keywords only"""
        question = {
            'question': 'Patient complains of persistent cough and dyspnea.',
            'options': ['Asthma', 'COPD', 'Pneumonia', 'Normal'],
            'answer': 'Asthma'
        }
        
        is_respiratory, metadata = self.filter.filter_question(question)
        
        self.assertTrue(is_respiratory)
        self.assertIn('keywords', metadata['match_type'])
        self.assertGreater(len(metadata['matched_keywords']), 0)
    
    def test_filter_non_respiratory_question(self):
        """Test filtering non-respiratory question"""
        question = {
            'question': 'Patient presents with acute abdominal pain.',
            'options': ['Appendicitis', 'Cholecystitis', 'Pancreatitis', 'Gastritis'],
            'answer': 'Appendicitis'
        }
        
        is_respiratory, metadata = self.filter.filter_question(question)
        
        self.assertFalse(is_respiratory)
        self.assertEqual(len(metadata['match_type']), 0)
    
    def test_keyword_categorization(self):
        """Test keyword categorization"""
        keywords = {'pneumonia', 'dyspnea', 'chest x-ray', 'bronchi'}
        categorized = self.filter._categorize_matches(keywords)
        
        self.assertIn('pneumonia', categorized['diseases'])
        self.assertIn('dyspnea', categorized['symptoms'])
        self.assertIn('chest x-ray', categorized['diagnostic'])
        self.assertIn('bronchi', categorized['anatomical'])
    
    def test_dataset_filtering(self):
        """Test filtering complete dataset"""
        dataset = [
            {
                'question': 'Patient with J45.9 asthma',
                'answer': 'A'
            },
            {
                'question': 'COPD patient with dyspnea',
                'answer': 'B'
            },
            {
                'question': 'Patient with diabetes',
                'answer': 'C'
            },
            {
                'question': 'Pneumonia diagnosis',
                'answer': 'D'
            },
        ]
        
        filtered, stats = self.filter.filter_dataset(dataset, "Test Dataset")
        
        self.assertEqual(stats.total_questions, 4)
        self.assertEqual(stats.final_filtered, 3)
        self.assertGreater(stats.keyword_matches, 0)


class TestFilterStats(unittest.TestCase):
    """Test FilterStats dataclass"""
    
    def test_stats_initialization(self):
        """Test FilterStats initialization"""
        stats = FilterStats()
        self.assertEqual(stats.total_questions, 0)
        self.assertEqual(stats.final_filtered, 0)
        self.assertIsInstance(stats.by_disease, dict)
        self.assertIsInstance(stats.by_symptom, dict)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete pipeline"""
    
    def test_full_pipeline_workflow(self):
        """Test complete filtering workflow"""
        # Sample dataset
        sample_data = [
            {
                'id': 1,
                'question': 'A 45-year-old with J44.1 COPD presents with increased dyspnea',
                'options': {
                    'A': 'Antibiotics',
                    'B': 'Bronchodilators',
                    'C': 'Steroids',
                    'D': 'Observation'
                },
                'answer': 'B',
                'explanation': 'COPD exacerbation requires bronchodilators'
            },
            {
                'id': 2,
                'question': 'Patient with pneumonia and productive cough',
                'options': {
                    'A': 'Antibiotics',
                    'B': 'Antivirals',
                    'C': 'Observation',
                    'D': 'Surgery'
                },
                'answer': 'A'
            },
            {
                'id': 3,
                'question': 'Patient with type 2 diabetes mellitus',
                'options': {
                    'A': 'Metformin',
                    'B': 'Insulin',
                    'C': 'Lifestyle modification',
                    'D': 'All of the above'
                },
                'answer': 'D'
            }
        ]
        
        filter_pipeline = RespiratoryFilter()
        filtered, stats = filter_pipeline.filter_dataset(sample_data, "Sample")
        
        # Verify results
        self.assertEqual(len(filtered), 2)
        self.assertEqual(stats.total_questions, 3)
        self.assertEqual(stats.final_filtered, 2)
        
        # Verify metadata is added
        for question in filtered:
            self.assertIn('respiratory_metadata', question)
            metadata = question['respiratory_metadata']
            self.assertIn('match_type', metadata)
            self.assertGreater(len(metadata['match_type']), 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRespiratoryFilter))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterStats))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
