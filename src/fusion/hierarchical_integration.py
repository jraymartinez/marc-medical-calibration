"""
Hierarchical Integration implementation.
Integrates outputs from multiple levels: specialists, verification, and validation.
"""
from typing import Dict, Any, List, Optional
from ..agents.llm_client import LocalLLMClient, get_llm_client
from ..agents.prompts import HIERARCHICAL_INTEGRATION_PROMPT


class HierarchicalIntegrator:
    """
    Integrates information across multiple hierarchical levels:
    Level 1: Multiple specialist outputs
    Level 2: Verification results
    Level 3: Validation results
    """
    
    def __init__(
        self,
        llm_client: Optional[LocalLLMClient] = None,
        use_llm_integration: bool = True,
        confidence_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize hierarchical integrator.
        
        Args:
            llm_client: LLM client for integration synthesis
            use_llm_integration: Whether to use LLM for integration (vs rule-based)
            confidence_weights: Weights for different levels in confidence computation
        """
        self.llm_client = llm_client or get_llm_client()
        self.use_llm_integration = use_llm_integration
        self.confidence_weights = confidence_weights or {
            "specialist": 0.3,
            "verification": 0.3,
            "validation": 0.4
        }
    
    def integrate(
        self,
        question: str,
        specialist_outputs: List[Dict[str, Any]],
        consultation_result: Optional[Dict[str, Any]] = None,
        verification_result: Optional[Dict[str, Any]] = None,
        validation_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Integrate outputs from all hierarchical levels.
        
        Args:
            question: The original question
            specialist_outputs: Individual specialist outputs
            consultation_result: Multi-specialist consultation result
            verification_result: Tier 1 verification result
            validation_result: Tier 2 validation result
            
        Returns:
            Integrated result with final answer, confidence, and comprehensive reasoning
        """
        if self.use_llm_integration:
            result = self._llm_integration(
                question=question,
                specialist_outputs=specialist_outputs,
                consultation_result=consultation_result,
                verification_result=verification_result,
                validation_result=validation_result
            )
        else:
            result = self._rule_based_integration(
                specialist_outputs=specialist_outputs,
                consultation_result=consultation_result,
                verification_result=verification_result,
                validation_result=validation_result
            )
        
        # Add metadata
        result["integration_method"] = "llm" if self.use_llm_integration else "rule_based"
        result["question"] = question
        result["num_specialists"] = len(specialist_outputs)
        
        return result
    
    def _llm_integration(
        self,
        question: str,
        specialist_outputs: List[Dict[str, Any]],
        consultation_result: Optional[Dict[str, Any]],
        verification_result: Optional[Dict[str, Any]],
        validation_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use LLM to perform hierarchical integration.
        
        Args:
            question: The question
            specialist_outputs: Specialist outputs
            consultation_result: Consultation result
            verification_result: Verification result
            validation_result: Validation result
            
        Returns:
            Integrated result
        """
        # Format inputs for prompt
        specialist_text = self._format_specialist_outputs(specialist_outputs)
        verification_text = self._format_verification(verification_result)
        validation_text = self._format_validation(validation_result)
        
        # If consultation result exists, include it
        if consultation_result:
            specialist_text += f"\n\nConsultation Synthesis:\n{consultation_result}"
        
        # Generate integration prompt
        prompt = HIERARCHICAL_INTEGRATION_PROMPT.format(
            question=question,
            specialist_outputs=specialist_text,
            verification_results=verification_text,
            validation_results=validation_text
        )
        
        # Get integration response
        response = self.llm_client.generate(
            system_prompt="You are a medical decision integration expert.",
            user_prompt=prompt,
            temperature=0.2,
            max_new_tokens=2000
        )
        
        # Parse response
        result = self._parse_integration_response(response)
        result["integration_response"] = response
        
        return result
    
    def _rule_based_integration(
        self,
        specialist_outputs: List[Dict[str, Any]],
        consultation_result: Optional[Dict[str, Any]],
        verification_result: Optional[Dict[str, Any]],
        validation_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use rule-based logic for hierarchical integration.
        
        Args:
            specialist_outputs: Specialist outputs
            consultation_result: Consultation result
            verification_result: Verification result
            validation_result: Validation result
            
        Returns:
            Integrated result
        """
        # Start with consultation result or highest confidence specialist
        if consultation_result:
            final_answer = consultation_result.get("answer")
            base_confidence = consultation_result.get("confidence", 0.5)
            reasoning = consultation_result.get("reasoning", "")
        else:
            # Use highest confidence specialist
            best = max(specialist_outputs, key=lambda x: x.get("confidence", 0))
            final_answer = best.get("answer")
            base_confidence = best.get("confidence", 0.5)
            reasoning = best.get("reasoning", "")
        
        # Adjust confidence based on verification
        confidence_adjustments = []
        if verification_result:
            tier1_conf = verification_result.get("confidence", 0.5)
            verified = verification_result.get("verified", "UNCERTAIN")
            
            if verified == "YES":
                confidence_adjustments.append(tier1_conf * self.confidence_weights["verification"])
            elif verified == "NO":
                confidence_adjustments.append(-tier1_conf * self.confidence_weights["verification"])
            else:
                confidence_adjustments.append(0)
        
        # Adjust confidence based on validation
        if validation_result:
            tier2_conf = validation_result.get("final_confidence", 0.5)
            status = validation_result.get("validation_status", "NEEDS_REVIEW")
            
            if status == "APPROVED":
                confidence_adjustments.append(tier2_conf * self.confidence_weights["validation"])
            elif status == "REJECTED":
                confidence_adjustments.append(-tier2_conf * self.confidence_weights["validation"])
            else:
                confidence_adjustments.append(0)
        
        # Compute final confidence
        final_confidence = base_confidence * self.confidence_weights["specialist"]
        final_confidence += sum(confidence_adjustments)
        final_confidence = max(0.0, min(1.0, final_confidence))
        
        # Compute quality score
        quality_score = validation_result.get("quality_score", 0.5) if validation_result else 0.5
        
        return {
            "answer": final_answer,
            "confidence": final_confidence,
            "reasoning": reasoning,
            "quality_score": quality_score,
            "confidence_adjustments": confidence_adjustments
        }
    
    def _format_specialist_outputs(self, specialist_outputs: List[Dict[str, Any]]) -> str:
        """Format specialist outputs for prompt."""
        lines = []
        for i, output in enumerate(specialist_outputs, 1):
            specialty = output.get("specialty", f"Specialist {i}")
            answer = output.get("answer", "N/A")
            confidence = output.get("confidence", 0.0)
            reasoning = output.get("reasoning", "")
            
            lines.append(f"{specialty}:")
            lines.append(f"  Answer: {answer}")
            lines.append(f"  Confidence: {confidence:.2f}")
            lines.append(f"  Reasoning: {reasoning[:200]}...")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_verification(self, verification_result: Optional[Dict[str, Any]]) -> str:
        """Format verification result for prompt."""
        if not verification_result:
            return "No verification performed"
        
        verified = verification_result.get("verified", "UNCERTAIN")
        confidence = verification_result.get("confidence", 0.0)
        reasoning = verification_result.get("verification_reasoning", "")
        issues = verification_result.get("issues_found", [])
        
        text = f"Verification Status: {verified}\n"
        text += f"Confidence: {confidence:.2f}\n"
        text += f"Issues: {', '.join(issues) if issues else 'None'}\n"
        text += f"Reasoning: {reasoning[:300]}"
        
        return text
    
    def _format_validation(self, validation_result: Optional[Dict[str, Any]]) -> str:
        """Format validation result for prompt."""
        if not validation_result:
            return "No validation performed"
        
        status = validation_result.get("validation_status", "NEEDS_REVIEW")
        confidence = validation_result.get("final_confidence", 0.0)
        quality = validation_result.get("quality_score", 0.0)
        notes = validation_result.get("validation_notes", "")
        
        text = f"Validation Status: {status}\n"
        text += f"Final Confidence: {confidence:.2f}\n"
        text += f"Quality Score: {quality:.2f}\n"
        text += f"Notes: {notes[:300]}"
        
        return text
    
    def _parse_integration_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM integration response."""
        import re
        
        result = {
            "answer": None,
            "confidence": 0.5,
            "reasoning": "",
            "quality_score": 0.5
        }
        
        # Extract answer
        answer_match = re.search(r'FINAL_ANSWER:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        if answer_match:
            result["answer"] = answer_match.group(1).strip()
        
        # Extract confidence
        conf_match = re.search(r'OVERALL_CONFIDENCE:\s*(0?\.\d+|\d+\.?\d*)', response, re.IGNORECASE)
        if conf_match:
            try:
                result["confidence"] = float(conf_match.group(1))
            except ValueError:
                pass
        
        # Extract reasoning
        reasoning_match = re.search(
            r'INTEGRATION_REASONING:\s*(.+?)(?=\n[A-Z_]+:|$)',
            response,
            re.IGNORECASE | re.DOTALL
        )
        if reasoning_match:
            result["reasoning"] = reasoning_match.group(1).strip()
        
        # Extract quality score
        quality_match = re.search(r'QUALITY_SCORE:\s*(0?\.\d+|\d+\.?\d*)', response, re.IGNORECASE)
        if quality_match:
            try:
                result["quality_score"] = float(quality_match.group(1))
            except ValueError:
                pass
        
        return result
    
    def __repr__(self) -> str:
        method = "LLM" if self.use_llm_integration else "Rule-based"
        return f"HierarchicalIntegrator(method={method})"

