"""
Unit tests for agent components.
Tests specialist agents, multi-specialist consultation, and LLM clients.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.llm_client import LocalLLMClient, get_llm_client
from src.agents.knowledge_bases import (
    KnowledgeBase,
    RespiratoryKnowledgeBase,
    get_knowledge_base
)
from src.agents.specialist_agent import SpecialistAgent, create_specialist_team
from src.agents.multi_specialist_consultation import (
    MultiSpecialistConsultation,
    create_consultation_system
)


class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self, mock_response: str = "ANSWER: A\nCONFIDENCE: 0.8\nREASONING: Test reasoning"):
        self.mock_response = mock_response
        self.call_count = 0
    
    def generate(self, system_prompt, user_prompt, temperature=0.7, max_new_tokens=1000, **kwargs):
        self.call_count += 1
        return self.mock_response


class TestLLMClient(unittest.TestCase):
    """Test LLM client functionality."""
    
    def test_mock_client(self):
        """Test mock LLM client."""
        client = MockLLMClient()
        response = client.generate("System", "User prompt")
        self.assertIn("ANSWER:", response)
        self.assertEqual(client.call_count, 1)


class TestKnowledgeBases(unittest.TestCase):
    """Test knowledge base functionality."""
    
    def test_respiratory_knowledge_base(self):
        """Test respiratory medicine knowledge base."""
        kb = RespiratoryKnowledgeBase()
        self.assertEqual(kb.specialty, "Respiratory Medicine")
        self.assertIn("Asthma", kb.key_concepts)
        
        context = kb.get_context()
        self.assertIn("Respiratory", context)
    
    def test_get_knowledge_base(self):
        """Test knowledge base factory."""
        kb = get_knowledge_base("respiratory")
        self.assertIsInstance(kb, RespiratoryKnowledgeBase)
        
        with self.assertRaises(ValueError):
            get_knowledge_base("nonexistent_specialty")


class TestSpecialistAgent(unittest.TestCase):
    """Test specialist agent functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MockLLMClient()
        self.agent = SpecialistAgent(
            specialty="respiratory",
            llm_client=self.mock_client
        )
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.specialty, "respiratory")
        self.assertIsNotNone(self.agent.knowledge_base)
    
    def test_analyze_question(self):
        """Test question analysis."""
        question = "What is the best treatment for asthma?"
        options = ["A. Antibiotics", "B. Bronchodilators", "C. Surgery"]
        
        result = self.agent.analyze_question(question, options)
        
        self.assertIn("answer", result)
        self.assertIn("confidence", result)
        self.assertIn("reasoning", result)
        self.assertIn("specialty", result)
        self.assertEqual(result["specialty"], "respiratory")
    
    def test_response_parsing(self):
        """Test parsing of LLM responses."""
        response = "ANSWER: B\nCONFIDENCE: 0.85\nREASONING: This is the correct answer because..."
        parsed = self.agent._parse_response(response)
        
        self.assertEqual(parsed["answer"], "B")
        self.assertAlmostEqual(parsed["confidence"], 0.85)
        self.assertIn("correct answer", parsed["reasoning"])
    
    def test_create_specialist_team(self):
        """Test creating team of specialists."""
        specialties = ["respiratory", "cardiology"]
        team = create_specialist_team(specialties, llm_client=self.mock_client)
        
        self.assertEqual(len(team), 2)
        self.assertEqual(team[0].specialty, "respiratory")
        self.assertEqual(team[1].specialty, "cardiology")


class TestMultiSpecialistConsultation(unittest.TestCase):
    """Test multi-specialist consultation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MockLLMClient()
        
        # Create specialists with different mock responses
        self.specialist1 = SpecialistAgent(
            specialty="respiratory",
            llm_client=MockLLMClient("ANSWER: A\nCONFIDENCE: 0.8\nREASONING: Respiratory reasoning")
        )
        self.specialist2 = SpecialistAgent(
            specialty="cardiology",
            llm_client=MockLLMClient("ANSWER: A\nCONFIDENCE: 0.9\nREASONING: Cardiology reasoning")
        )
        
        self.consultation = MultiSpecialistConsultation(
            specialists=[self.specialist1, self.specialist2],
            llm_client=self.mock_client,
            aggregation_method="voting"
        )
    
    def test_consultation_initialization(self):
        """Test consultation initialization."""
        self.assertEqual(len(self.consultation.specialists), 2)
        self.assertEqual(self.consultation.aggregation_method, "voting")
    
    def test_voting_aggregation(self):
        """Test voting aggregation."""
        specialist_opinions = [
            {"specialty": "respiratory", "answer": "A", "confidence": 0.8, "reasoning": "Test 1"},
            {"specialty": "cardiology", "answer": "A", "confidence": 0.9, "reasoning": "Test 2"}
        ]
        
        result = self.consultation._voting_aggregation(specialist_opinions)
        
        self.assertEqual(result["answer"], "A")
        self.assertGreater(result["confidence"], 0.8)
    
    def test_highest_confidence_aggregation(self):
        """Test highest confidence aggregation."""
        specialist_opinions = [
            {"specialty": "respiratory", "answer": "A", "confidence": 0.7, "reasoning": "Test 1"},
            {"specialty": "cardiology", "answer": "B", "confidence": 0.9, "reasoning": "Test 2"}
        ]
        
        result = self.consultation._highest_confidence_aggregation(specialist_opinions)
        
        self.assertEqual(result["answer"], "B")
        self.assertEqual(result["confidence"], 0.9)
        self.assertEqual(result["source_specialty"], "cardiology")
    
    def test_consult(self):
        """Test full consultation process."""
        question = "What is the treatment for pneumonia?"
        options = ["A. Antibiotics", "B. Surgery", "C. Observation"]
        
        result = self.consultation.consult(question, options)
        
        self.assertIn("answer", result)
        self.assertIn("confidence", result)
        self.assertIn("specialist_opinions", result)
        self.assertEqual(result["num_specialists"], 2)
    
    def test_create_consultation_system(self):
        """Test consultation system factory."""
        specialties = ["respiratory", "cardiology"]
        system = create_consultation_system(
            specialties,
            llm_client=self.mock_client,
            aggregation_method="synthesis"
        )
        
        self.assertIsInstance(system, MultiSpecialistConsultation)
        self.assertEqual(len(system.specialists), 2)


class TestPrompts(unittest.TestCase):
    """Test prompt generation."""
    
    def test_specialist_prompt(self):
        """Test specialist prompt formatting."""
        from src.agents.prompts import get_specialist_prompt
        
        prompts = get_specialist_prompt(
            specialty="respiratory",
            question="Test question",
            options=["A", "B", "C"],
            knowledge_context="Test context"
        )
        
        self.assertIn("system", prompts)
        self.assertIn("user", prompts)
        self.assertIn("respiratory", prompts["system"].lower())
        self.assertIn("Test question", prompts["user"])


if __name__ == '__main__':
    unittest.main()

