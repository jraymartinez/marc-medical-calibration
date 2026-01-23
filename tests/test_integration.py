"""
Unit tests for integration and fusion components.
Tests hierarchical integration and end-to-end pipelines.
"""
import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.fusion.hierarchical_integration import HierarchicalIntegrator
class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self, mock_response: str = None):
        if mock_response is None:
            mock_response = (
                "FINAL_ANSWER: A\n"
                "OVERALL_CONFIDENCE: 0.87\n"
                "INTEGRATION_REASONING: Integrated from all sources.\n"
                "QUALITY_SCORE: 0.85"
            )
        self.mock_response = mock_response
    
    def generate(self, system_prompt, user_prompt, temperature=0.7, max_new_tokens=1000, **kwargs):
        return self.mock_response


class TestHierarchicalIntegration(unittest.TestCase):
    """Test hierarchical integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MockLLMClient()
        self.integrator = HierarchicalIntegrator(
            llm_client=self.mock_client,
            use_llm_integration=True
        )
    
    def test_integrator_initialization(self):
        """Test integrator initialization."""
        self.assertTrue(self.integrator.use_llm_integration)
        self.assertIn("specialist", self.integrator.confidence_weights)
        self.assertIn("verification", self.integrator.confidence_weights)
        self.assertIn("validation", self.integrator.confidence_weights)
    
    def test_llm_integration(self):
        """Test LLM-based integration."""
        question = "Test question"
        specialist_outputs = [
            {"specialty": "respiratory", "answer": "A", "confidence": 0.8, "reasoning": "Test 1"},
            {"specialty": "cardiology", "answer": "A", "confidence": 0.9, "reasoning": "Test 2"}
        ]
        consultation_result = {
            "answer": "A",
            "confidence": 0.85,
            "reasoning": "Consultation reasoning"
        }
        verification_result = {
            "verified": "YES",
            "confidence": 0.8
        }
        validation_result = {
            "validation_status": "APPROVED",
            "final_confidence": 0.88,
            "quality_score": 0.85
        }
        
        result = self.integrator._llm_integration(
            question=question,
            specialist_outputs=specialist_outputs,
            consultation_result=consultation_result,
            verification_result=verification_result,
            validation_result=validation_result
        )
        
        self.assertIn("answer", result)
        self.assertIn("confidence", result)
        self.assertIn("reasoning", result)
    
    def test_rule_based_integration(self):
        """Test rule-based integration."""
        specialist_outputs = [
            {"specialty": "respiratory", "answer": "A", "confidence": 0.8, "reasoning": "Test 1"},
            {"specialty": "cardiology", "answer": "B", "confidence": 0.7, "reasoning": "Test 2"}
        ]
        consultation_result = {
            "answer": "A",
            "confidence": 0.75,
            "reasoning": "Consultation reasoning"
        }
        verification_result = {
            "verified": "YES",
            "confidence": 0.85
        }
        validation_result = {
            "validation_status": "APPROVED",
            "final_confidence": 0.9,
            "quality_score": 0.88
        }
        
        result = self.integrator._rule_based_integration(
            specialist_outputs=specialist_outputs,
            consultation_result=consultation_result,
            verification_result=verification_result,
            validation_result=validation_result
        )
        
        self.assertEqual(result["answer"], "A")
        self.assertIn("confidence", result)
        self.assertIn("quality_score", result)
        # Should have high confidence due to positive verification and validation
        self.assertGreater(result["confidence"], 0.5)
    
    def test_rule_based_integration_negative(self):
        """Test rule-based integration with negative verification."""
        specialist_outputs = [
            {"specialty": "respiratory", "answer": "A", "confidence": 0.8, "reasoning": "Test"}
        ]
        consultation_result = {
            "answer": "A",
            "confidence": 0.8,
            "reasoning": "Test"
        }
        verification_result = {
            "verified": "NO",
            "confidence": 0.9
        }
        validation_result = {
            "validation_status": "REJECTED",
            "final_confidence": 0.2,
            "quality_score": 0.25
        }
        
        result = self.integrator._rule_based_integration(
            specialist_outputs=specialist_outputs,
            consultation_result=consultation_result,
            verification_result=verification_result,
            validation_result=validation_result
        )
        
        # Should have lower confidence due to negative verification and validation
        self.assertLess(result["confidence"], 0.5)
    
    def test_integrate_full(self):
        """Test full integration process."""
        question = "What is the treatment for COPD?"
        specialist_outputs = [
            {"specialty": "respiratory", "answer": "A", "confidence": 0.85, "reasoning": "Test 1"}
        ]
        
        result = self.integrator.integrate(
            question=question,
            specialist_outputs=specialist_outputs
        )
        
        self.assertIn("answer", result)
        self.assertIn("confidence", result)
        self.assertIn("integration_method", result)
        self.assertEqual(result["num_specialists"], 1)
    
    def test_format_specialist_outputs(self):
        """Test formatting of specialist outputs."""
        specialist_outputs = [
            {"specialty": "respiratory", "answer": "A", "confidence": 0.8, "reasoning": "Test reasoning"},
            {"specialty": "cardiology", "answer": "B", "confidence": 0.75, "reasoning": "Another test"}
        ]
        
        formatted = self.integrator._format_specialist_outputs(specialist_outputs)
        
        self.assertIn("respiratory", formatted)
        self.assertIn("cardiology", formatted)
        self.assertIn("Answer: A", formatted)
        self.assertIn("Answer: B", formatted)
    
    def test_format_verification(self):
        """Test formatting of verification results."""
        verification_result = {
            "verified": "YES",
            "confidence": 0.85,
            "verification_reasoning": "All checks passed",
            "issues_found": []
        }
        
        formatted = self.integrator._format_verification(verification_result)
        
        self.assertIn("YES", formatted)
        self.assertIn("0.85", formatted)
        self.assertIn("None", formatted)
    
    def test_format_validation(self):
        """Test formatting of validation results."""
        validation_result = {
            "validation_status": "APPROVED",
            "final_confidence": 0.9,
            "quality_score": 0.88,
            "validation_notes": "Validation successful"
        }
        
        formatted = self.integrator._format_validation(validation_result)
        
        self.assertIn("APPROVED", formatted)
        self.assertIn("0.9", formatted)
        self.assertIn("0.88", formatted)
    
    def test_parse_integration_response(self):
        """Test parsing of integration response."""
        response = (
            "FINAL_ANSWER: B\n"
            "OVERALL_CONFIDENCE: 0.92\n"
            "INTEGRATION_REASONING: Based on all evidence, B is correct.\n"
            "QUALITY_SCORE: 0.89"
        )
        
        parsed = self.integrator._parse_integration_response(response)
        
        self.assertEqual(parsed["answer"], "B")
        self.assertAlmostEqual(parsed["confidence"], 0.92)
        self.assertAlmostEqual(parsed["quality_score"], 0.89)
        self.assertIn("evidence", parsed["reasoning"])
    
    def test_different_confidence_weights(self):
        """Test integration with different confidence weights."""
        custom_weights = {
            "specialist": 0.5,
            "verification": 0.2,
            "validation": 0.3
        }
        
        integrator = HierarchicalIntegrator(
            llm_client=self.mock_client,
            use_llm_integration=False,
            confidence_weights=custom_weights
        )
        
        self.assertEqual(integrator.confidence_weights["specialist"], 0.5)
        self.assertEqual(integrator.confidence_weights["verification"], 0.2)
        self.assertEqual(integrator.confidence_weights["validation"], 0.3)


class TestEndToEndIntegration(unittest.TestCase):
    """Test end-to-end integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MockLLMClient()
    
    def test_minimal_integration(self):
        """Test integration with minimal inputs."""
        integrator = HierarchicalIntegrator(
            llm_client=self.mock_client,
            use_llm_integration=False
        )
        
        specialist_outputs = [
            {"answer": "A", "confidence": 0.8, "reasoning": "Test"}
        ]
        
        result = integrator.integrate(
            question="Test?",
            specialist_outputs=specialist_outputs
        )
        
        self.assertIsNotNone(result["answer"])
    
    def test_integration_with_all_levels(self):
        """Test integration with all hierarchical levels."""
        integrator = HierarchicalIntegrator(
            llm_client=self.mock_client,
            use_llm_integration=False
        )
        
        specialist_outputs = [
            {"answer": "A", "confidence": 0.8, "reasoning": "Test 1"},
            {"answer": "A", "confidence": 0.85, "reasoning": "Test 2"}
        ]
        consultation_result = {
            "answer": "A",
            "confidence": 0.82,
            "reasoning": "Consensus"
        }
        verification_result = {
            "verified": "YES",
            "confidence": 0.9
        }
        validation_result = {
            "validation_status": "APPROVED",
            "final_confidence": 0.92,
            "quality_score": 0.9
        }
        
        result = integrator.integrate(
            question="Test?",
            specialist_outputs=specialist_outputs,
            consultation_result=consultation_result,
            verification_result=verification_result,
            validation_result=validation_result
        )
        
        # Should have high confidence with all positive signals
        self.assertGreater(result["confidence"], 0.7)
        self.assertGreater(result["quality_score"], 0.7)


if __name__ == '__main__':
    unittest.main()

