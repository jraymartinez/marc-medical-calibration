"""
Multi-Specialist Consultation implementation.
Coordinates multiple specialist agents and synthesizes their opinions.
"""
import re
from typing import Dict, List, Optional, Any
from collections import Counter
from .specialist_agent import SpecialistAgent, create_specialist_team
from .llm_client import LocalLLMClient, get_llm_client
from .prompts import get_consultation_prompt


class MultiSpecialistConsultation:
    """
    Coordinates consultation among multiple specialist agents.
    Synthesizes their opinions into a unified recommendation.
    """
    
    def __init__(
        self,
        specialists: List[SpecialistAgent],
        llm_client: Optional[LocalLLMClient] = None,
        aggregation_method: str = "synthesis"
    ):
        """
        Initialize multi-specialist consultation.
        
        Args:
            specialists: List of specialist agents
            llm_client: LLM client for synthesis
            aggregation_method: Method for aggregating opinions
                - "synthesis": LLM-based synthesis
                - "voting": Weighted voting by confidence
                - "highest_confidence": Take highest confidence answer
        """
        self.specialists = specialists
        self.llm_client = llm_client or get_llm_client()
        self.aggregation_method = aggregation_method
    
    def consult(
        self,
        question: str,
        options: List[str],
        relevant_specialties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Conduct multi-specialist consultation on a question.
        
        Args:
            question: The medical question
            options: List of answer options
            relevant_specialties: Filter to specific specialties (optional)
            
        Returns:
            Dictionary with final answer, confidence, reasoning, and specialist opinions
        """
        # Filter specialists if needed
        active_specialists = self.specialists
        if relevant_specialties:
            active_specialists = [
                s for s in self.specialists 
                if s.specialty in relevant_specialties
            ]
        
        if not active_specialists:
            raise ValueError("No active specialists for consultation")
        
        # Collect opinions from all specialists
        specialist_opinions = []
        for specialist in active_specialists:
            try:
                opinion = specialist.analyze_question(question, options)
                specialist_opinions.append(opinion)
            except Exception as e:
                print(f"Warning: {specialist.specialty} failed: {e}")
        
        if not specialist_opinions:
            raise ValueError("No valid specialist opinions obtained")
        
        # Aggregate opinions
        if self.aggregation_method == "synthesis":
            result = self._synthesize_opinions(question, specialist_opinions)
        elif self.aggregation_method == "voting":
            result = self._voting_aggregation(specialist_opinions)
        elif self.aggregation_method == "highest_confidence":
            result = self._highest_confidence_aggregation(specialist_opinions)
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation_method}")
        
        # Add specialist opinions to result
        result["specialist_opinions"] = specialist_opinions
        result["num_specialists"] = len(specialist_opinions)
        result["aggregation_method"] = self.aggregation_method
        
        return result
    
    def _synthesize_opinions(
        self,
        question: str,
        specialist_opinions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Use LLM to synthesize specialist opinions.
        
        Args:
            question: The medical question
            specialist_opinions: List of specialist opinion dictionaries
            
        Returns:
            Synthesized result dictionary
        """
        # Format prompts
        prompts = get_consultation_prompt(question, specialist_opinions)
        
        # Generate synthesis
        response = self.llm_client.generate(
            system_prompt=prompts["system"],
            user_prompt=prompts["user"],
            temperature=0.3,  # Lower temperature for synthesis
            max_new_tokens=2000
        )
        
        # Parse synthesis
        result = self._parse_synthesis(response)
        result["synthesis_response"] = response
        
        return result
    
    def _voting_aggregation(self, specialist_opinions: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate opinions using weighted voting.
        
        Args:
            specialist_opinions: List of specialist opinion dictionaries
            
        Returns:
            Aggregated result dictionary
        """
        # Weight votes by confidence
        vote_weights = {}
        for opinion in specialist_opinions:
            answer = opinion.get("answer")
            confidence = opinion.get("confidence", 0.5)
            
            if answer:
                vote_weights[answer] = vote_weights.get(answer, 0) + confidence
        
        if not vote_weights:
            return {
                "answer": None,
                "confidence": 0.0,
                "reasoning": "No valid votes received"
            }
        
        # Find winner
        final_answer = max(vote_weights, key=vote_weights.get)
        total_weight = sum(vote_weights.values())
        final_confidence = vote_weights[final_answer] / total_weight
        
        # Build reasoning
        reasoning = f"Weighted voting result: {final_answer} with {final_confidence:.2f} confidence. "
        reasoning += f"Vote distribution: {vote_weights}"
        
        return {
            "answer": final_answer,
            "confidence": final_confidence,
            "reasoning": reasoning,
            "vote_distribution": vote_weights
        }
    
    def _highest_confidence_aggregation(
        self,
        specialist_opinions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Select answer from specialist with highest confidence.
        
        Args:
            specialist_opinions: List of specialist opinion dictionaries
            
        Returns:
            Result from highest confidence specialist
        """
        # Find opinion with highest confidence
        best_opinion = max(
            specialist_opinions,
            key=lambda x: x.get("confidence", 0)
        )
        
        return {
            "answer": best_opinion.get("answer"),
            "confidence": best_opinion.get("confidence", 0.5),
            "reasoning": f"Selected answer from {best_opinion.get('specialty')} "
                        f"(highest confidence: {best_opinion.get('confidence', 0.5):.2f}). "
                        f"{best_opinion.get('reasoning', '')}",
            "source_specialty": best_opinion.get("specialty")
        }
    
    def _parse_synthesis(self, response: str) -> Dict[str, Any]:
        """
        Parse synthesis response from LLM.
        
        Args:
            response: Raw synthesis response
            
        Returns:
            Parsed dictionary
        """
        result = {
            "answer": None,
            "confidence": 0.5,
            "reasoning": "",
            "specialist_agreement": "unknown"
        }
        
        # Extract final answer
        answer_match = re.search(
            r'FINAL_ANSWER:\s*([A-E]|[a-e]|\d+|.*?)(?:\n|$)',
            response,
            re.IGNORECASE
        )
        if answer_match:
            result["answer"] = answer_match.group(1).strip()
        
        # Extract confidence
        confidence_match = re.search(
            r'CONFIDENCE:\s*(0?\.\d+|\d+\.?\d*)',
            response,
            re.IGNORECASE
        )
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                result["confidence"] = max(0.0, min(1.0, confidence))
            except ValueError:
                pass
        
        # Extract reasoning
        reasoning_match = re.search(
            r'REASONING:\s*(.+?)(?=\n[A-Z_]+:|$)',
            response,
            re.IGNORECASE | re.DOTALL
        )
        if reasoning_match:
            result["reasoning"] = reasoning_match.group(1).strip()
        
        # Extract agreement level
        agreement_match = re.search(
            r'SPECIALIST_AGREEMENT:\s*(.+?)(?:\n|$)',
            response,
            re.IGNORECASE
        )
        if agreement_match:
            result["specialist_agreement"] = agreement_match.group(1).strip()
        
        return result
    
    def __repr__(self) -> str:
        specialties = [s.specialty for s in self.specialists]
        return f"MultiSpecialistConsultation(specialties={specialties})"


def create_consultation_system(
    specialties: List[str],
    llm_client: Optional[LocalLLMClient] = None,
    aggregation_method: str = "synthesis"
) -> MultiSpecialistConsultation:
    """
    Create a complete multi-specialist consultation system.
    
    Args:
        specialties: List of specialty names
        llm_client: Shared LLM client (optional)
        aggregation_method: Method for aggregating opinions
        
    Returns:
        MultiSpecialistConsultation instance
    """
    specialists = create_specialist_team(specialties, llm_client)
    return MultiSpecialistConsultation(
        specialists=specialists,
        llm_client=llm_client,
        aggregation_method=aggregation_method
    )

