"""
Unit tests for verification components.
Tests Tier 1 verification and Tier 2 validation.
"""
import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.verification.tier1_verification import Tier1Verifier
from src.verification.tier2_validation import Tier2Validator
class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self, mock_response: str = None):
        if mock_response is None:
            mock_response = (
                "VERIFIED: YES\n"
                "CONFIDENCE: 0.85\n"
                "ISSUES_FOUND: None\n"
                "VERIFICATION_REASONING: The answer appears correct and well-reasoned."
            )
        self.mock_response = mock_response
    
    def generate(self, system_prompt, user_prompt, temperature=0.7, max_new_tokens=1000, **kwargs):
        return self.mock_response


class TestTier1Verification(unittest.TestCase):
    """Test Tier 1 verification functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MockLLMClient()
        self.verifier = Tier1Verifier(llm_client=self.mock_client)
    
    def test_verifier_initialization(self):
        """Test verifier initialization."""
        self.assertIsNotNone(self.verifier.llm_client)
        self.assertEqual(self.verifier.temperature, 0.3)
    
    def test_verify(self):
        """Test basic verification."""
        question = "What is the treatment for hypertension?"
        answer = "A"
        reasoning = "Beta-blockers are effective for hypertension with confidence 0.8"
        
        result = self.verifier.verify(question, answer, reasoning)
        
        self.assertIn("verified", result)
        self.assertIn("confidence", result)
        self.assertIn("issues_found", result)
        self.assertIn("verification_reasoning", result)
        self.assertEqual(result["tier"], 1)
    
    def test_parse_verification_yes(self):
        """Test parsing YES verification."""
        response = (
            "VERIFIED: YES\n"
            "CONFIDENCE: 0.9\n"
            "ISSUES_FOUND: None\n"
            "VERIFICATION_REASONING: Answer is correct."
        )
        
        parsed = self.verifier._parse_verification(response)
        
        self.assertEqual(parsed["verified"], "YES")
        self.assertAlmostEqual(parsed["confidence"], 0.9)
        self.assertEqual(len(parsed["issues_found"]), 0)
    
    def test_parse_verification_no(self):
        """Test parsing NO verification."""
        response = (
            "VERIFIED: NO\n"
            "CONFIDENCE: 0.7\n"
            "ISSUES_FOUND:\n- Incorrect reasoning\n- Missing key information\n"
            "VERIFICATION_REASONING: The answer has several issues."
        )
        
        parsed = self.verifier._parse_verification(response)
        
        self.assertEqual(parsed["verified"], "NO")
        self.assertAlmostEqual(parsed["confidence"], 0.7)
        self.assertGreater(len(parsed["issues_found"]), 0)
    
    def test_parse_verification_uncertain(self):
        """Test parsing UNCERTAIN verification."""
        response = (
            "VERIFIED: UNCERTAIN\n"
            "CONFIDENCE: 0.5\n"
            "ISSUES_FOUND: Some ambiguity in the question\n"
            "VERIFICATION_REASONING: Need more information."
        )
        
        parsed = self.verifier._parse_verification(response)
        
        self.assertEqual(parsed["verified"], "UNCERTAIN")
    
    def test_basic_checks(self):
        """Test basic automated checks."""
        question = "Test question"
        answer = "A"
        reasoning = "This is a detailed medical reasoning with the answer A mentioned explicitly."
        
        checks = self.verifier._perform_basic_checks(question, answer, reasoning)
        
        self.assertTrue(checks["has_answer"])
        self.assertTrue(checks["has_reasoning"])
        self.assertTrue(checks["reasoning_mentions_answer"])
        self.assertTrue(checks["sufficient_reasoning_length"])
    
    def test_basic_checks_failures(self):
        """Test basic checks with failures."""
        checks = self.verifier._perform_basic_checks("", "", "")
        
        self.assertFalse(checks["has_answer"])
        self.assertFalse(checks["has_reasoning"])
    
    def test_extract_confidence_from_reasoning(self):
        """Test extracting confidence from reasoning text."""
        reasoning = "The answer is correct with confidence: 0.85"
        confidence = self.verifier._extract_confidence_from_reasoning(reasoning)
        
        self.assertAlmostEqual(confidence, 0.85)
    
    def test_batch_verify(self):
        """Test batch verification."""
        items = [
            {
                "question": "Q1",
                "answer": "A",
                "reasoning": "Reasoning 1"
            },
            {
                "question": "Q2",
                "answer": "B",
                "reasoning": "Reasoning 2"
            }
        ]
        
        results = self.verifier.batch_verify(items)
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("verified", result)


class TestTier2Validation(unittest.TestCase):
    """Test Tier 2 validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        mock_response = (
            "VALIDATION_STATUS: APPROVED\n"
            "FINAL_CONFIDENCE: 0.88\n"
            "VALIDATION_NOTES: The answer has been thoroughly validated.\n"
            "RECOMMENDED_ACTION: Accept the answer."
        )
        self.mock_client = MockLLMClient(mock_response)
        self.validator = Tier2Validator(llm_client=self.mock_client)
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        self.assertIsNotNone(self.validator.llm_client)
        self.assertEqual(self.validator.temperature, 0.2)
    
    def test_validate(self):
        """Test basic validation."""
        question = "What is the treatment for diabetes?"
        answer = "A"
        reasoning = "Insulin is the primary treatment"
        tier1_result = {
            "verified": "YES",
            "confidence": 0.8,
            "issues_found": []
        }
        
        result = self.validator.validate(question, answer, reasoning, tier1_result)
        
        self.assertIn("validation_status", result)
        self.assertIn("final_confidence", result)
        self.assertIn("validation_notes", result)
        self.assertIn("quality_score", result)
        self.assertEqual(result["tier"], 2)
    
    def test_parse_validation_approved(self):
        """Test parsing APPROVED validation."""
        response = (
            "VALIDATION_STATUS: APPROVED\n"
            "FINAL_CONFIDENCE: 0.9\n"
            "VALIDATION_NOTES: All checks passed.\n"
            "RECOMMENDED_ACTION: Accept answer."
        )
        
        parsed = self.validator._parse_validation(response)
        
        self.assertEqual(parsed["validation_status"], "APPROVED")
        self.assertAlmostEqual(parsed["final_confidence"], 0.9)
    
    def test_parse_validation_rejected(self):
        """Test parsing REJECTED validation."""
        response = (
            "VALIDATION_STATUS: REJECTED\n"
            "FINAL_CONFIDENCE: 0.2\n"
            "VALIDATION_NOTES: Significant errors found.\n"
            "RECOMMENDED_ACTION: Reject answer."
        )
        
        parsed = self.validator._parse_validation(response)
        
        self.assertEqual(parsed["validation_status"], "REJECTED")
    
    def test_parse_validation_needs_review(self):
        """Test parsing NEEDS_REVIEW validation."""
        response = (
            "VALIDATION_STATUS: NEEDS_REVIEW\n"
            "FINAL_CONFIDENCE: 0.6\n"
            "VALIDATION_NOTES: Some concerns.\n"
            "RECOMMENDED_ACTION: Manual review recommended."
        )
        
        parsed = self.validator._parse_validation(response)
        
        self.assertEqual(parsed["validation_status"], "NEEDS_REVIEW")
    
    def test_compute_quality_score(self):
        """Test quality score computation."""
        tier1_result = {
            "verified": "YES",
            "confidence": 0.8
        }
        tier2_result = {
            "validation_status": "APPROVED",
            "final_confidence": 0.9
        }
        
        score = self.validator._compute_quality_score(tier1_result, tier2_result)
        
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)
        # Should be high since both tiers are positive
        self.assertGreater(score, 0.7)
    
    def test_compute_quality_score_rejected(self):
        """Test quality score with rejection."""
        tier1_result = {
            "verified": "NO",
            "confidence": 0.3
        }
        tier2_result = {
            "validation_status": "REJECTED",
            "final_confidence": 0.2
        }
        
        score = self.validator._compute_quality_score(tier1_result, tier2_result)
        
        # Should be low since both tiers are negative
        self.assertLess(score, 0.4)
    
    def test_should_accept_answer_approved(self):
        """Test answer acceptance with approval."""
        validation_result = {
            "validation_status": "APPROVED",
            "quality_score": 0.8
        }
        
        accept = self.validator.should_accept_answer(validation_result)
        self.assertTrue(accept)
    
    def test_should_accept_answer_rejected(self):
        """Test answer rejection."""
        validation_result = {
            "validation_status": "REJECTED",
            "quality_score": 0.3
        }
        
        accept = self.validator.should_accept_answer(validation_result)
        self.assertFalse(accept)
    
    def test_should_accept_answer_threshold(self):
        """Test answer acceptance based on threshold."""
        validation_result = {
            "validation_status": "NEEDS_REVIEW",
            "quality_score": 0.7
        }
        
        accept_default = self.validator.should_accept_answer(validation_result)
        accept_high_threshold = self.validator.should_accept_answer(validation_result, threshold=0.8)
        
        self.assertTrue(accept_default)
        self.assertFalse(accept_high_threshold)
    
    def test_batch_validate(self):
        """Test batch validation."""
        items = [
            {
                "question": "Q1",
                "answer": "A",
                "reasoning": "R1",
                "tier1_result": {"verified": "YES", "confidence": 0.8}
            },
            {
                "question": "Q2",
                "answer": "B",
                "reasoning": "R2",
                "tier1_result": {"verified": "YES", "confidence": 0.9}
            }
        ]
        
        results = self.validator.batch_validate(items)
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("validation_status", result)


if __name__ == '__main__':
    unittest.main()

