"""
Specialist Agent implementation.
Each agent represents a medical specialist with domain expertise.
"""
import re
import hashlib
from typing import Dict, List, Optional, Any
from .llm_client import LocalLLMClient, get_llm_client
from .knowledge_bases import get_knowledge_base, KnowledgeBase
from .prompts import get_specialist_prompt


class SpecialistAgent:
    """
    A specialist agent that provides expert medical opinions.
    Each agent has a specific medical specialty and knowledge base.
    """
    
    def __init__(
        self,
        specialty: str,
        llm_client: Optional[LocalLLMClient] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        temperature: float = 0.4,  # IMPROVED: 0.3 -> 0.4 for more exploration and better reasoning
        use_deterministic: bool = True  # NEW: Cache answers for reproducibility
    ):
        """
        Initialize a specialist agent.
        
        Args:
            specialty: Medical specialty (e.g., "respiratory", "cardiology")
            llm_client: LLM client for generation
            knowledge_base: Knowledge base for the specialty
            temperature: Temperature for LLM generation (optimized: 0.3 for medical QA)
            use_deterministic: If True, cache answers to ensure same question → same answer
        """
        self.specialty = specialty
        self.llm_client = llm_client or get_llm_client()
        self.knowledge_base = knowledge_base or get_knowledge_base(specialty)
        self.temperature = temperature
        self.use_deterministic = use_deterministic
        self._answer_cache: Dict[str, Dict[str, Any]] = {}  # Cache for deterministic answers
    
    def analyze_question(
        self,
        question: str,
        options: List[str],
        return_raw: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze a medical question and provide expert opinion.
        
        Args:
            question: The medical question
            options: List of answer options
            return_raw: Whether to return raw LLM response
            
        Returns:
            Dictionary with answer, confidence, reasoning, and metadata
        """
        # Create cache key for deterministic behavior
        if self.use_deterministic:
            cache_key = self._create_cache_key(question, options)
            if cache_key in self._answer_cache:
                # Return cached answer for reproducibility
                cached = self._answer_cache[cache_key].copy()
                if return_raw:
                    return {"raw_response": cached.get("raw_response", "")}
                return cached
        
        # Get knowledge context
        knowledge_context = self.knowledge_base.get_context()
        
        # Format prompts
        prompts = get_specialist_prompt(
            specialty=self.specialty,
            question=question,
            options=options,
            knowledge_context=knowledge_context
        )
        
        # Generate response
        # Use deterministic settings when caching is enabled
        if self.use_deterministic:
            # Greedy decoding (deterministic) - don't pass temperature/top_p
            response = self.llm_client.generate(
                system_prompt=prompts["system"],
                user_prompt=prompts["user"],
                temperature=0.0,  # Ignored but kept for clarity
                do_sample=False,  # Greedy decoding
                max_new_tokens=1500
            )
        else:
            # Sampling mode (non-deterministic)
            response = self.llm_client.generate(
                system_prompt=prompts["system"],
                user_prompt=prompts["user"],
                temperature=self.temperature,
                do_sample=True,
                max_new_tokens=1500
            )
        
        if return_raw:
            return {"raw_response": response}
        
        # Parse response
        parsed = self._parse_response(response)
        
        # Add metadata
        parsed["specialty"] = self.specialty
        parsed["raw_response"] = response
        
        # Cache the result for deterministic behavior
        if self.use_deterministic:
            cache_key = self._create_cache_key(question, options)
            self._answer_cache[cache_key] = parsed.copy()
        
        return parsed
    
    def _create_cache_key(self, question: str, options: List[str]) -> str:
        """Create a cache key from question and options."""
        # Normalize inputs for consistent hashing
        normalized_question = question.strip().lower()
        normalized_options = tuple(sorted(opt.strip().lower() for opt in options))
        cache_string = f"{self.specialty}:{normalized_question}:{normalized_options}"
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()
    
    def clear_cache(self):
        """Clear the answer cache (useful for testing)."""
        self._answer_cache.clear()
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse structured response from LLM.
        
        Improved parsing to handle:
        - Letter format answers (A, B, C, D)
        - Full text answers
        - Answers embedded in reasoning
        - Chain-of-thought format
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed dictionary with answer, confidence, reasoning
        """
        result = {
            "answer": None,
            "confidence": 0.5,
            "reasoning": ""
        }
        
        # Extract answer - try multiple patterns
        answer_text = None
        
        # Pattern 1: Explicit ANSWER: field (preferred)
        answer_match = re.search(r'ANSWER:\s*(.+?)(?:\n\n|\n[A-Z]+:|$)', response, re.IGNORECASE | re.DOTALL)
        if answer_match:
            answer_text = answer_match.group(1).strip()
        else:
            # Pattern 2: Match until end of line
            answer_match = re.search(r'ANSWER:\s*(.*)$', response, re.IGNORECASE | re.MULTILINE)
            if answer_match:
                answer_text = answer_match.group(1).strip()
        
        # Pattern 3: If no explicit ANSWER field, look for common answer patterns
        if not answer_text or not answer_text.strip():
            # Look for single letter (A, B, C, D) at end of response
            letter_match = re.search(r'\b([A-D])\b\s*$', response, re.IGNORECASE | re.MULTILINE)
            if letter_match:
                answer_text = letter_match.group(1).upper()
            else:
                # Look for "Final answer:" or "Selected answer:" patterns
                final_answer_match = re.search(r'(?:Final|Selected|Chosen)\s+answer[:\s]+(.+?)(?:\n|$)', response, re.IGNORECASE)
                if final_answer_match:
                    answer_text = final_answer_match.group(1).strip()
        
        # Clean up answer text
        if answer_text:
            # Remove common prefixes like "Option", "Answer is", etc.
            answer_text = re.sub(r'^(Option\s*[A-D]?[:\s]*|Answer\s*(is|:)?\s*)', '', answer_text, flags=re.IGNORECASE).strip()
            # Remove trailing punctuation that might be part of sentence
            answer_text = re.sub(r'[.,;:]+$', '', answer_text).strip()
            # If answer is very long (likely reasoning text), try to extract just the option
            if len(answer_text) > 200:
                # Try to find a letter or short option text at the end
                short_match = re.search(r'\b([A-D]|.{1,50})\s*$', answer_text, re.IGNORECASE)
                if short_match:
                    answer_text = short_match.group(1).strip()
        
        result["answer"] = answer_text if answer_text and answer_text.strip() else None
        
        # Extract confidence
        confidence_match = re.search(r'CONFIDENCE:\s*(0?\.\d+|\d+\.?\d*)', response, re.IGNORECASE)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                result["confidence"] = max(0.0, min(1.0, confidence))
            except ValueError:
                pass
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*(.+?)(?=\n[A-Z]+:|$)', response, re.IGNORECASE | re.DOTALL)
        if reasoning_match:
            result["reasoning"] = reasoning_match.group(1).strip()
        else:
            # If no explicit reasoning section, use full response (but exclude answer if found)
            if answer_text and answer_text in response:
                # Remove answer from reasoning to avoid duplication
                reasoning = response.replace(f"ANSWER: {answer_text}", "").strip()
                result["reasoning"] = reasoning
            else:
                result["reasoning"] = response
        
        return result
    
    def __repr__(self) -> str:
        return f"SpecialistAgent(specialty='{self.specialty}')"


def create_specialist_team(
    specialties: List[str],
    llm_client: Optional[LocalLLMClient] = None,
    temperature: float = 0.3,  # OPTIMIZED: 0.7 -> 0.3 for better accuracy
    use_deterministic: bool = True  # NEW: Enable deterministic answers for reproducibility
) -> List[SpecialistAgent]:
    """
    Create a team of specialist agents.
    
    Args:
        specialties: List of specialty names
        llm_client: Shared LLM client (optional)
        temperature: Temperature for generation (ignored if use_deterministic=True)
        use_deterministic: If True, cache answers to ensure same question → same answer
        
    Returns:
        List of SpecialistAgent instances
    """
    team = []
    for specialty in specialties:
        agent = SpecialistAgent(
            specialty=specialty,
            llm_client=llm_client,
            temperature=temperature,
            use_deterministic=use_deterministic
        )
        team.append(agent)
    
    return team

