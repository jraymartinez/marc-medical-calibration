"""
Tier 2 Validation implementation.
GP Medical Validation (General Practitioner Cross-Check).

The GP validates specialist diagnoses by checking:
- Basic Medical Facts
- Symptom-Disease Consistency
- Medical Contradictions
- General Plausibility

Output: G score (GP validation confidence)
"""
import re
from typing import Dict, Any, Optional, List
from ..agents.llm_client import LocalLLMClient, get_llm_client
from ..agents.prompts import get_verification_prompt


class Tier2Validator:
    """
    GP Medical Validation agent.
    
    Acts as a General Practitioner cross-checking specialist diagnoses.
    Validates medical accuracy, symptom consistency, and flags contradictions.
    Outputs GP validation confidence score (G).
    """
    
    def __init__(
        self,
        llm_client: Optional[LocalLLMClient] = None,
        temperature: float = 0.2,  # OPTIMIZED: 0.15 -> 0.2 for more nuanced validation judgments
        gp_knowledge_base: Optional[str] = None,
        rejected_penalty: float = 0.4,  # Penalty multiplier for REJECTED status (ECE IMPROVEMENT: more aggressive)
        needs_review_penalty: float = 0.7  # Penalty multiplier for NEEDS_REVIEW status (ECE IMPROVEMENT: more aggressive)
    ):
        """
        Initialize Tier 2 GP validator.
        
        Args:
            llm_client: LLM client for validation
            temperature: Temperature for LLM generation (very low for rigorous validation)
            gp_knowledge_base: Optional GP medical knowledge context
            rejected_penalty: Penalty multiplier for REJECTED status (default: 0.35)
            needs_review_penalty: Penalty multiplier for NEEDS_REVIEW status (default: 0.65)
        """
        self.llm_client = llm_client or get_llm_client()
        self.temperature = temperature
        self.gp_knowledge_base = gp_knowledge_base or self._get_default_gp_knowledge()
        self.rejected_penalty = rejected_penalty
        self.needs_review_penalty = needs_review_penalty
    
    def _get_default_gp_knowledge(self) -> str:
        """Get default GP medical knowledge context."""
        return """
        As a General Practitioner, you have broad medical knowledge across specialties.
        Your role is to cross-check specialist diagnoses for:
        - Basic medical fact accuracy
        - Symptom-disease consistency
        - Medical contradictions or impossibilities
        - General clinical plausibility
        """
    
    def validate_specialist_diagnosis(
        self,
        specialist_name: str,
        question: str,
        answer: str,
        reasoning: str,
        tier1_result: Dict[str, Any],
        options: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        GP validates a specific specialist's diagnosis.
        
        Args:
            specialist_name: Name of the specialist whose diagnosis is being validated
            question: The medical question
            answer: Specialist's proposed answer
            reasoning: Specialist's reasoning
            tier1_result: Tier 1 self-verification result for this specialist
            options: Answer options (optional)
            
        Returns:
            Validation result with GP confidence score (G)
        """
        # Generate GP validation prompt
        prompt = get_verification_prompt(
            tier=2,
            question=question,
            answer=answer,
            reasoning=reasoning,
            tier1_result=tier1_result,
            options=options
        )
        
        # GP cross-check validation
        response = self.llm_client.generate(
            system_prompt=f"You are a General Practitioner reviewing a {specialist_name}'s diagnosis.\n{self.gp_knowledge_base}",
            user_prompt=prompt,
            temperature=self.temperature,
            max_new_tokens=2000
        )
        
        # Parse validation result
        validation_result = self._parse_validation(response)
        
        # Extract checks performed
        checks = self._extract_validation_checks(response)
        
        # Compute GP confidence score (G)
        G_score = validation_result["final_confidence"]
        validation_status = validation_result["validation_status"]
        
        # INDEPENDENT VALIDATION: Don't trust Tier 1's correctness assessment
        # Tier 2 validates independently, but we can use Tier 1 correctness as a signal
        tier1_correctness = tier1_result.get('correctness_score', 0.5)
        tier1_status = tier1_result.get('verified_status', 'UNKNOWN')
        
        # Adjust G score based on validation status
        # VERY AGGRESSIVE: When Tier 1 says NO, Tier 2 should strongly consider REJECTING
        if validation_status == "REJECTED":
            if tier1_correctness < 0.4 or tier1_status == "NO":
                # Tier 1 found answer is wrong → very aggressive penalty
                G_score *= 0.15  # Very aggressive (lowered from 0.2)
            else:
                G_score *= self.rejected_penalty  # Normal penalty (0.4)
        elif validation_status == "NEEDS_REVIEW":
            if tier1_correctness < 0.4 or tier1_status == "NO":
                # CRITICAL FIX: When Tier 1 says NO, Tier 2 should REJECT, not NEEDS_REVIEW
                # Apply very aggressive penalty to push towards REJECTED
                G_score *= 0.3  # Very aggressive penalty for NO (was 0.4)
            elif tier1_status == "UNCERTAIN":
                # CRITICAL FIX: When Tier 1 says UNCERTAIN, be more aggressive
                # UNCERTAIN means Tier 1 has doubts - Tier 2 should be skeptical
                G_score *= 0.35  # VERY aggressive penalty for UNCERTAIN (was 0.5) - should prevent wrong answers
            else:
                G_score *= self.needs_review_penalty  # Normal penalty (0.7)
        # If APPROVED, check if Tier 1 found issues (should be rare)
        # CRITICAL FIX: When Tier 1 says NO, Tier 2 MUST REJECT (not just apply penalty)
        elif validation_status == "APPROVED":
            if tier1_status == "NO":
                # CRITICAL FIX: When Tier 1 says NO, Tier 2 should NOT APPROVE at all
                # Force REJECTED status or apply extremely aggressive penalty
                # Option 1: Force REJECTED status
                validation_status = "REJECTED"
                G_score *= 0.05  # Extremely aggressive penalty (was 0.2) - should be <0.1
            elif tier1_correctness < 0.4:
                # Tier 1 found answer is wrong (low correctness) but didn't say NO explicitly
                # Apply very aggressive penalty
                G_score *= 0.15  # Very aggressive penalty (was 0.2)
            elif tier1_correctness < 0.6 or tier1_status == "UNCERTAIN":
                # CRITICAL FIX: When Tier 1 says UNCERTAIN, Tier 2 should REJECT, not APPROVE
                # If Tier 2 approved despite Tier 1 UNCERTAIN, apply very aggressive penalty
                if tier1_status == "UNCERTAIN":
                    G_score *= 0.25  # VERY aggressive penalty for UNCERTAIN (was 0.4) - should prevent wrong answers
                else:
                    G_score *= 0.6  # Significant penalty (lowered from 0.7)
            elif tier1_correctness < 0.75 or tier1_status != "YES":
                # Tier 1 not fully confident but Tier 2 approved → moderate penalty
                G_score *= 0.85  # Moderate penalty (new check)
            # CRITICAL FIX: Even if Tier 1 says high correctness (>0.8), be skeptical
            # High correctness scores can be wrong (e.g., Question 1: Cardiology got 0.842 for wrong answer)
            elif tier1_correctness > 0.8:
                # Tier 1 says very high correctness, but we need to validate independently
                # Reduce confidence slightly to account for possibility of error
                G_score *= 0.9  # Small penalty even for high correctness (new check)
            # Only if Tier 1 says YES and correctness is moderate (0.75-0.8), minimal penalty
        
        G_score = max(0.0, min(1.0, G_score))
        
        # CRITICAL FIX: If we forced REJECTED status, ensure G score is very low
        if validation_status == "REJECTED" and (tier1_status == "NO" or tier1_correctness < 0.4):
            G_score = min(G_score, 0.1)  # Cap at 0.1 for wrong answers
        
        # Compute quality score
        quality_score = self._compute_quality_score(tier1_result, validation_result)
        
        return {
            "tier": 2,
            "specialist": specialist_name,
            "gp_validation_confidence_G": G_score,  # Final G score
            "validation_status": validation_status,
            "validation_checks": checks,
            "validation_notes": validation_result["validation_notes"],
            "recommended_action": validation_result["recommended_action"],
            "quality_score": quality_score,
            "tier1_S_score": tier1_result.get("specialist_confidence_S", 0.5),
            "raw_validation_response": response
        }
    
    def validate(
        self,
        question: str,
        answer: str,
        reasoning: str,
        tier1_result: Dict[str, Any],
        options: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility.
        Use validate_specialist_diagnosis() for proper GP validation.
        """
        specialist_name = tier1_result.get("specialist", "Unknown Specialist")
        
        return self.validate_specialist_diagnosis(
            specialist_name=specialist_name,
            question=question,
            answer=answer,
            reasoning=reasoning,
            tier1_result=tier1_result,
            options=options
        )
    
    def _extract_validation_checks(self, response: str) -> Dict[str, bool]:
        """Extract which validation checks passed/failed."""
        checks = {
            "medical_facts_accurate": "medical facts" in response.lower() and "accurate" in response.lower(),
            "symptom_consistency": "symptom" in response.lower() and "consistent" in response.lower(),
            "no_contradictions": "contradiction" in response.lower() and ("no" in response.lower() or "none" in response.lower()),
            "clinically_plausible": "plausible" in response.lower() or "reasonable" in response.lower()
        }
        return checks
    
    def _parse_validation(self, response: str) -> Dict[str, Any]:
        """
        Parse validation response from LLM.
        
        Args:
            response: Raw validation response
            
        Returns:
            Parsed validation result
        """
        result = {
            "validation_status": "NEEDS_REVIEW",
            "final_confidence": 0.5,
            "validation_notes": "",
            "recommended_action": ""
        }
        
        # Extract validation status
        status_match = re.search(
            r'VALIDATION_STATUS:\s*(APPROVED|REJECTED|NEEDS_REVIEW)',
            response,
            re.IGNORECASE
        )
        if status_match:
            result["validation_status"] = status_match.group(1).upper()
        
        # Extract final confidence
        confidence_match = re.search(
            r'FINAL_CONFIDENCE:\s*(0?\.\d+|\d+\.?\d*)',
            response,
            re.IGNORECASE
        )
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                result["final_confidence"] = max(0.0, min(1.0, confidence))
            except ValueError:
                pass
        
        # Extract validation notes
        notes_match = re.search(
            r'VALIDATION_NOTES:\s*(.+?)(?=\n[A-Z_]+:|$)',
            response,
            re.IGNORECASE | re.DOTALL
        )
        if notes_match:
            result["validation_notes"] = notes_match.group(1).strip()
        
        # Extract recommended action
        action_match = re.search(
            r'RECOMMENDED_ACTION:\s*(.+?)(?=\n[A-Z_]+:|$)',
            response,
            re.IGNORECASE | re.DOTALL
        )
        if action_match:
            result["recommended_action"] = action_match.group(1).strip()
        
        return result
    
    def _compute_quality_score(
        self,
        tier1_result: Dict[str, Any],
        tier2_result: Dict[str, Any]
    ) -> float:
        """
        Compute aggregate quality score from both verification tiers.
        
        Args:
            tier1_result: Tier 1 verification result
            tier2_result: Tier 2 validation result
            
        Returns:
            Quality score (0.0-1.0)
        """
        score = 0.0
        
        # Tier 1 contributions (40%)
        tier1_verified = tier1_result.get("verified", "UNCERTAIN")
        if tier1_verified == "YES":
            score += 0.25
        elif tier1_verified == "UNCERTAIN":
            score += 0.10
        
        tier1_confidence = tier1_result.get("confidence", 0.5)
        score += 0.15 * tier1_confidence
        
        # Tier 2 contributions (60%)
        tier2_status = tier2_result.get("validation_status", "NEEDS_REVIEW")
        if tier2_status == "APPROVED":
            score += 0.35
        elif tier2_status == "NEEDS_REVIEW":
            score += 0.15
        
        tier2_confidence = tier2_result.get("final_confidence", 0.5)
        score += 0.25 * tier2_confidence
        
        return min(1.0, max(0.0, score))
    
    def should_accept_answer(
        self,
        validation_result: Dict[str, Any],
        threshold: float = 0.6
    ) -> bool:
        """
        Determine if answer should be accepted based on validation.
        
        Args:
            validation_result: Result from validate()
            threshold: Quality score threshold for acceptance
            
        Returns:
            True if answer should be accepted
        """
        status = validation_result.get("validation_status")
        quality_score = validation_result.get("quality_score", 0.0)
        
        if status == "APPROVED" and quality_score >= threshold:
            return True
        elif status == "REJECTED":
            return False
        else:
            # NEEDS_REVIEW - use quality score
            return quality_score >= threshold
    
    def batch_validate(
        self,
        validation_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate multiple answers in batch.
        
        Args:
            validation_items: List of dicts with question, answer, reasoning, tier1_result
            
        Returns:
            List of validation results
        """
        results = []
        for item in validation_items:
            result = self.validate(
                question=item["question"],
                answer=item["answer"],
                reasoning=item["reasoning"],
                tier1_result=item["tier1_result"],
                options=item.get("options")
            )
            results.append(result)
        
        return results
    
    def __repr__(self) -> str:
        return "Tier2Validator()"

