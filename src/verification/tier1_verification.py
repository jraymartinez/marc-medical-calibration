"""
Tier 1 Verification implementation.
Two-Phase Self-Verification at specialist level (Wu et al. 2024).

Based on: Wu et al. "Uncertainty Estimation of Large Language Models in Medical Question Answering"

Phase 1: Generate & Explain - Specialist generates diagnosis with step-by-step explanation
Phase 2: Two-Phase Verification
  - Step 2a: Formulate verification questions from the explanation
  - Step 2b: Answer verification questions independently (without reference)
  - Step 2c: Answer verification questions again, referencing the original explanation
  - Step 2d: Compare inconsistencies between independent and reference answers
Output: Specialist Confidence Score (S) based on inconsistency measure
"""
import re
import torch
import hashlib
from typing import Dict, Any, Optional, List
from ..agents.llm_client import LocalLLMClient, get_llm_client


class Tier1Verifier:
    """
    Two-Phase Self-Verification for individual specialists.
    
    Implements Wu et al. 2024 approach exactly:
    - Phase 1: Specialist generates answer + step-by-step explanation (already done by specialist agent)
    - Phase 2: Two-phase verification
      1. Formulate verification questions from explanation
      2. Answer questions independently (without reference)
      3. Answer questions again with reference to explanation
      4. Measure inconsistencies → uncertainty score
    - Outputs: Specialist Confidence Score (S) based on inconsistency
    """
    
    def __init__(
        self,
        llm_client: Optional[LocalLLMClient] = None,
        temperature: float = 0.2,  # Default (for backward compatibility)
        consistency_weight: float = 0.65,  # Favor initial confidence more (was 0.5)
        s_score_formula: str = "weighted_average",  # "weighted_average", "multiplicative", or "hybrid"
        independent_temp: float = 0.4,  # Temperature for independent answers (higher for diversity)
        reference_temp: float = 0.2,  # Temperature for reference answers (lower for consistency)
        question_temp: float = 0.3  # Temperature for verification question formulation
    ):
        """
        Initialize Tier 1 two-phase self-verifier.
        
        Args:
            llm_client: LLM client for verification
            temperature: Default temperature (for backward compatibility, overridden by specific temps)
            consistency_weight: Weight for combining initial and verification confidence (for weighted_average)
            s_score_formula: Formula to use for S_score calculation
                - "weighted_average": S = 0.5 * initial + 0.5 * verification
                - "multiplicative": S = initial * (1 - inconsistency)
            independent_temp: Temperature for independent answers (higher = more diverse, better inconsistency detection)
            reference_temp: Temperature for reference answers (lower = more consistent with explanation)
            question_temp: Temperature for verification question formulation
        """
        self.llm_client = llm_client or get_llm_client()
        self.temperature = temperature  # Keep for backward compatibility
        self.consistency_weight = consistency_weight
        self.s_score_formula = s_score_formula
        self.independent_temp = independent_temp  # Higher for diversity
        self.reference_temp = reference_temp  # Lower for consistency
        self.question_temp = question_temp  # Moderate for question formulation
    
    def _get_deterministic_seed(self, question: str, answer: str, stage: str) -> int:
        """
        Generate deterministic seed from question+answer+stage hash.
        
        This ensures:
        - Same question+answer always gets same seed (reproducible)
        - Different stages get different seeds (diversity across stages)
        - Seed is deterministic but allows sampling (best of both worlds)
        
        Args:
            question: The medical question
            answer: The proposed answer
            stage: Verification stage ("questions", "independent", "reference")
            
        Returns:
            Deterministic seed (0 to 2^32-1)
        """
        hash_str = f"{question}_{answer}_{stage}"
        hash_digest = hashlib.md5(hash_str.encode('utf-8')).hexdigest()
        return int(hash_digest, 16) % (2**32)
    
    def verify_specialist(
        self,
        specialist_name: str,
        question: str,
        answer: str,
        reasoning: str,
        initial_confidence: float,
        options: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Two-Phase Self-Verification for a single specialist (Wu et al. 2024).
        
        Phase 1 (already done): Specialist generated answer with step-by-step explanation
        Phase 2 (this method): Two-phase verification with inconsistency measurement
        
        Args:
            specialist_name: Name of the specialist (for context)
            question: The medical question
            answer: Proposed answer from Phase 1
            reasoning: Step-by-step explanation from Phase 1
            initial_confidence: Initial confidence from Phase 1
            options: Answer options (optional)
            
        Returns:
            Verification result with Specialist Confidence Score (S)
        """
        # Step 2a: Formulate verification questions from the explanation
        verification_questions = self._formulate_verification_questions(
            question=question,
            answer=answer,
            reasoning=reasoning,
            specialist_name=specialist_name
        )
        
        if not verification_questions:
            # Fallback: If no questions generated, use simple verification
            return self._simple_verification_fallback(
                specialist_name, question, answer, reasoning, initial_confidence
            )
        
        # Step 2b: Answer verification questions independently (without reference)
        independent_answers = self._answer_verification_questions_independently(
            question=question,
            answer=answer,
            verification_questions=verification_questions,
            specialist_name=specialist_name
        )
        
        # Step 2c: Answer verification questions again, referencing the original explanation
        reference_answers = self._answer_verification_questions_with_reference(
            question=question,
            answer=answer,
            verification_questions=verification_questions,
            reasoning=reasoning,
            specialist_name=specialist_name
        )
        
        # Step 2d: Compare inconsistencies between independent and reference answers
        inconsistency_score = self._measure_inconsistencies(
            independent_answers=independent_answers,
            reference_answers=reference_answers
        )
        
        # Wu et al. 2024 method: Use ONLY inconsistency score (no correctness checking)
        # Low inconsistency → High confidence (answer is internally consistent)
        # High inconsistency → Low confidence (answer has internal contradictions)
        verification_confidence = 1.0 - inconsistency_score
        
        # IMPROVED: Stricter thresholds for verified status
        # YES only if inconsistency < 0.10 AND initial confidence > 0.8
        # This prevents wrong but consistent answers from getting YES
        if inconsistency_score < 0.10 and initial_confidence > 0.8:
            verified_status = "YES"  # Internally consistent AND high initial confidence
        elif inconsistency_score < 0.5:
            verified_status = "UNCERTAIN"  # Some internal contradictions
        else:
            verified_status = "NO"  # High inconsistency (contradictory)
        
        # S_score formula selection
        if self.s_score_formula == "multiplicative":
            # Formula 2: S = initial * (1 - inconsistency)
            # Directly uses inconsistency as uncertainty measure (closest to Wu et al.)
            S_score = initial_confidence * (1.0 - inconsistency_score)
        elif self.s_score_formula == "hybrid":
            # Hybrid formula - weighted average with quadratic inconsistency penalty
            # S = 0.7 * initial + 0.3 * verification * (1 - inconsistency)^2
            verification_confidence_penalized = verification_confidence * ((1.0 - inconsistency_score) ** 2)
            S_score = 0.7 * initial_confidence + 0.3 * verification_confidence_penalized
        else:
            # Formula 1 (default): S = weighted_average of initial and verification confidence
            # Uses consistency_weight parameter (default 0.65, favoring initial confidence)
            S_score = (
                self.consistency_weight * initial_confidence +
                (1 - self.consistency_weight) * verification_confidence
            )
        
        # Clamp to [0, 1] with minimum floor to preserve calibration
        # Minimum floor prevents too-low scores that hurt ECE
        S_score = max(0.05, min(1.0, S_score))  # Floor at 0.05 instead of 0.0
        
        return {
            "tier": 1,
            "specialist": specialist_name,
            "phase1_confidence": initial_confidence,
            "phase2_verification_confidence": verification_confidence,
            "verified_status": verified_status,
            "specialist_confidence_S": S_score,  # Final S score
            "inconsistency_score": inconsistency_score,
            "correctness_score": None,  # Removed: using only Wu et al. consistency method
            "verification_questions": verification_questions,
            "independent_answers": independent_answers,
            "reference_answers": reference_answers,
            "verification_method": "two_phase_wu_et_al"  # Pure Wu et al. method
        }
    
    def _formulate_verification_questions(
        self,
        question: str,
        answer: str,
        reasoning: str,
        specialist_name: str
    ) -> List[str]:
        """
        Step 2a: Formulate verification questions from the explanation.
        
        Based on Wu et al. 2024: Extract factual claims from the explanation
        and formulate questions to verify them.
        """
        prompt = f"""You are a medical verification expert. Your task is to formulate verification questions based on the explanation provided.

Question: {question}
Proposed Answer: {answer}
Explanation: {reasoning}

Based on the explanation above, formulate 2-4 specific verification questions that check the factual claims made in the explanation. These questions should:
1. Target specific medical facts or claims mentioned in the explanation
2. Be answerable independently (without reference to the explanation)
3. Help verify the correctness of the reasoning

Format your response as:
VERIFICATION_QUESTIONS:
1. [First question]
2. [Second question]
3. [Third question]
...
"""
        
        # Set deterministic seed for reproducible sampling
        seed = self._get_deterministic_seed(question, answer, "questions")
        torch.manual_seed(seed)
        
        response = self.llm_client.generate(
            system_prompt=f"You are formulating verification questions for a {specialist_name}'s diagnosis.",
            user_prompt=prompt,
            temperature=self.question_temp,  # Use moderate temperature for diversity
            do_sample=True,  # Sampling for exploration (with fixed seed)
            max_new_tokens=500
        )
        
        # Parse verification questions
        questions = []
        # Look for numbered list or bullet points
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            # Match numbered items (1., 2., etc.) or bullet points (-, •, etc.)
            match = re.match(r'^[\d\-\•\*]+[\.\)]\s*(.+)', line)
            if match:
                questions.append(match.group(1).strip())
            elif line.startswith('VERIFICATION_QUESTIONS:'):
                continue
            elif line and len(line) > 20 and '?' in line:
                # Fallback: any line with a question mark
                questions.append(line.rstrip('?'))
        
        # Also try to extract from VERIFICATION_QUESTIONS section
        if not questions:
            questions_section = re.search(
                r'VERIFICATION_QUESTIONS:\s*(.+?)(?=\n[A-Z_]+:|$)',
                response,
                re.IGNORECASE | re.DOTALL
            )
            if questions_section:
                text = questions_section.group(1)
                # Split by newlines and extract questions
                for line in text.split('\n'):
                    line = line.strip()
                    if line and ('?' in line or len(line) > 20):
                        # Remove numbering/bullets
                        line = re.sub(r'^[\d\-\•\*]+[\.\)]\s*', '', line)
                        if line:
                            questions.append(line)
        
        return questions[:4]  # Limit to 4 questions max
    
    def _answer_verification_questions_independently(
        self,
        question: str,
        answer: str,
        verification_questions: List[str],
        specialist_name: str
    ) -> Dict[str, str]:
        """
        Step 2b: Answer verification questions independently (without reference to explanation).
        
        Based on Wu et al. 2024: Answer each verification question without
        looking at the original explanation.
        """
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(verification_questions)])
        
        prompt = f"""You are a medical expert. Answer the following verification questions based on your medical knowledge.

Original Question Context: {question}

Verification Questions:
{questions_text}

IMPORTANT: Answer these questions based on your medical knowledge ONLY. Do NOT reference any specific explanation or reasoning from the original question. Answer independently.

Format your response as:
ANSWERS:
1. [Answer to first question]
2. [Answer to second question]
...
"""
        
        # Set deterministic seed for reproducible sampling
        seed = self._get_deterministic_seed(question, answer, "independent")
        torch.manual_seed(seed)
        
        response = self.llm_client.generate(
            system_prompt=f"You are answering verification questions independently as a medical expert.",
            user_prompt=prompt,
            temperature=self.independent_temp,  # Higher temperature for diversity
            do_sample=True,  # Sampling for exploration (with fixed seed)
            max_new_tokens=800
        )
        
        # Parse answers
        answers = {}
        lines = response.split('\n')
        current_q_idx = None
        
        for line in lines:
            line = line.strip()
            # Match numbered items
            match = re.match(r'^(\d+)[\.\)]\s*(.+)', line)
            if match:
                q_idx = int(match.group(1)) - 1
                if 0 <= q_idx < len(verification_questions):
                    answers[verification_questions[q_idx]] = match.group(2).strip()
        
        # Fallback: try to extract from ANSWERS section
        if not answers:
            answers_section = re.search(
                r'ANSWERS:\s*(.+?)(?=\n[A-Z_]+:|$)',
                response,
                re.IGNORECASE | re.DOTALL
            )
            if answers_section:
                text = answers_section.group(1)
                for i, line in enumerate(text.split('\n')):
                    line = line.strip()
                    if line and i < len(verification_questions):
                        # Remove numbering
                        line = re.sub(r'^[\d\-\•\*]+[\.\)]\s*', '', line)
                        if line:
                            answers[verification_questions[i]] = line
        
        return answers
    
    def _answer_verification_questions_with_reference(
        self,
        question: str,
        answer: str,
        verification_questions: List[str],
        reasoning: str,
        specialist_name: str
    ) -> Dict[str, str]:
        """
        Step 2c: Answer verification questions again, referencing the original explanation.
        
        Based on Wu et al. 2024: Answer each verification question while
        referencing the original explanation.
        """
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(verification_questions)])
        
        prompt = f"""You are a medical expert. Answer the following verification questions while referencing the provided explanation.

Original Question Context: {question}

Original Explanation:
{reasoning}

Verification Questions:
{questions_text}

IMPORTANT: Answer these questions while referencing the explanation above. Use the explanation to guide your answers.

Format your response as:
ANSWERS:
1. [Answer to first question]
2. [Answer to second question]
...
"""
        
        # Set deterministic seed for reproducible sampling
        seed = self._get_deterministic_seed(question, answer, "reference")
        torch.manual_seed(seed)
        
        response = self.llm_client.generate(
            system_prompt=f"You are answering verification questions with reference to the original explanation.",
            user_prompt=prompt,
            temperature=self.reference_temp,  # Lower temperature for consistency
            do_sample=True,  # Sampling for exploration (with fixed seed)
            max_new_tokens=800
        )
        
        # Parse answers (same logic as independent)
        answers = {}
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            match = re.match(r'^(\d+)[\.\)]\s*(.+)', line)
            if match:
                q_idx = int(match.group(1)) - 1
                if 0 <= q_idx < len(verification_questions):
                    answers[verification_questions[q_idx]] = match.group(2).strip()
        
        # Fallback
        if not answers:
            answers_section = re.search(
                r'ANSWERS:\s*(.+?)(?=\n[A-Z_]+:|$)',
                response,
                re.IGNORECASE | re.DOTALL
            )
            if answers_section:
                text = answers_section.group(1)
                for i, line in enumerate(text.split('\n')):
                    line = line.strip()
                    if line and i < len(verification_questions):
                        line = re.sub(r'^[\d\-\•\*]+[\.\)]\s*', '', line)
                        if line:
                            answers[verification_questions[i]] = line
        
        return answers
    
    def _measure_inconsistencies(
        self,
        independent_answers: Dict[str, str],
        reference_answers: Dict[str, str]
    ) -> float:
        """
        Step 2d: Measure inconsistencies between independent and reference answers.
        
        Based on Wu et al. 2024: Inconsistencies indicate uncertainty.
        Lower inconsistency = higher confidence.
        """
        if not independent_answers or not reference_answers:
            return 0.5  # Default moderate inconsistency if parsing failed
        
        # Count questions that have answers in both sets
        common_questions = set(independent_answers.keys()) & set(reference_answers.keys())
        if not common_questions:
            # If no overlap, check if we have any answers at all
            if independent_answers and reference_answers:
                # Different questions answered = high inconsistency
                return 0.8
            return 0.5  # No answers = moderate inconsistency
        
        # For each common question, check if answers are consistent
        inconsistencies = 0
        total = len(common_questions)
        
        for question in common_questions:
            ind_answer = independent_answers[question].lower().strip()
            ref_answer = reference_answers[question].lower().strip()
            
            # Skip if either answer is empty
            if not ind_answer or not ref_answer:
                inconsistencies += 1
                continue
            
            # Simple consistency check: exact match or high similarity
            if ind_answer == ref_answer:
                # Exact match = consistent
                continue
            elif self._answers_similar(ind_answer, ref_answer):
                # Similar = mostly consistent
                continue
            else:
                # Different = inconsistent
                inconsistencies += 1
        
        # Inconsistency score: 0.0 (all consistent) to 1.0 (all inconsistent)
        inconsistency_score = inconsistencies / total if total > 0 else 0.5
        
        return inconsistency_score
    
    def _answers_similar(self, answer1: str, answer2: str, threshold: float = 0.4) -> bool:
        """
        Check if two answers are similar (simple word overlap).
        
        Args:
            answer1: First answer
            answer2: Second answer
            threshold: Similarity threshold (0-1) - lowered to 0.5 for more lenient matching
        
        Returns:
            True if answers are similar
        """
        # Simple word-based similarity
        # Normalize: lowercase, remove punctuation
        import string
        answer1_clean = answer1.lower().translate(str.maketrans('', '', string.punctuation))
        answer2_clean = answer2.lower().translate(str.maketrans('', '', string.punctuation))
        
        words1 = set(answer1_clean.split())
        words2 = set(answer2_clean.split())
        
        # Remove common stop words for better matching
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                     'may', 'might', 'can', 'could', 'this', 'that', 'these', 'those',
                     'in', 'on', 'at', 'by', 'for', 'with', 'to', 'from', 'of', 'as'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        if not words1 or not words2:
            return False
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return False
        
        similarity = intersection / union
        
        # Also check if one answer contains the key content words of the other
        # (for cases where one is more detailed but contains the same key info)
        if similarity < threshold:
            # Check if significant words overlap
            significant_words1 = {w for w in words1 if len(w) > 4}  # Words longer than 4 chars
            significant_words2 = {w for w in words2 if len(w) > 4}
            if significant_words1 and significant_words2:
                sig_similarity = len(significant_words1 & significant_words2) / len(significant_words1 | significant_words2)
                if sig_similarity >= 0.6:  # High overlap of significant words
                    return True
        
        return similarity >= threshold
    
    def _simple_verification_fallback(
        self,
        specialist_name: str,
        question: str,
        answer: str,
        reasoning: str,
        initial_confidence: float
    ) -> Dict[str, Any]:
        """
        Fallback verification method if question formulation fails.
        """
        # Simple consistency check
        checks = self._perform_basic_checks(question, answer, reasoning)
        
        # Simple confidence based on checks
        if all(checks.values()):
            verification_confidence = 0.8
            verified_status = "YES"
        elif sum(checks.values()) >= len(checks) // 2:
            verification_confidence = 0.5
            verified_status = "UNCERTAIN"
        else:
            verification_confidence = 0.3
            verified_status = "NO"
        
        # Adjust based on status
        if verified_status == "NO":
            adjustment_factor = 0.15
        elif verified_status == "UNCERTAIN":
            adjustment_factor = 0.5
        else:
            adjustment_factor = 1.0
        
        S_score = (
            self.consistency_weight * initial_confidence +
            (1 - self.consistency_weight) * verification_confidence
        ) * adjustment_factor
        
        S_score = max(0.0, min(1.0, S_score))
        
        return {
            "tier": 1,
            "specialist": specialist_name,
            "phase1_confidence": initial_confidence,
            "phase2_verification_confidence": verification_confidence,
            "verified_status": verified_status,
            "specialist_confidence_S": S_score,
            "inconsistency_score": 1.0 - verification_confidence,
            "verification_questions": [],
            "independent_answers": {},
            "reference_answers": {},
            "verification_method": "fallback",
            "basic_checks": checks
        }
    
    def _check_answer_correctness(
        self,
        question: str,
        answer: str,
        reasoning: str,
        options: Optional[List[str]],
        specialist_name: str
    ) -> float:
        """
        Check if the answer is actually correct (not just internally consistent).
        
        This addresses the fundamental limitation of Wu et al. method:
        - Wu et al. only checks consistency (internal coherence)
        - But wrong answers can be internally consistent
        - We need to also check correctness (medical accuracy)
        
        Returns:
            Correctness score: 0.0 (clearly wrong) to 1.0 (clearly correct)
        """
        # Format options for display
        if options:
            if isinstance(options, list):
                options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
            else:
                options_text = str(options)
        else:
            options_text = "Not provided"
        
        prompt = f"""You are a medical expert evaluating whether an answer is medically correct.

## FEW-SHOT EXAMPLES:

Example 1 (CORRECT):
Question: A 2-month-old girl is given a vaccine containing polyribosylribitol phosphate conjugated to a toxoid carrier. The vaccine provides immunity against which pathogen?
Options:
A. Neisseria meningitidis
B. Bordetella pertussis
C. Haemophilus influenzae
D. Streptococcus pneumoniae
Proposed Answer: C. Haemophilus influenzae
Reasoning: The vaccine described is the Hib vaccine, which contains polyribosylribitol phosphate (PRP) conjugated to a protein carrier.
CORRECTNESS: CORRECT
RANKING: 1 (best option)
CONFIDENCE: 0.95
EXPLANATION: This is correct. The Hib vaccine contains PRP conjugated to a carrier protein and provides immunity against Haemophilus influenzae type b.

Example 2 (INCORRECT):
Question: A patient presents with fever, hypotension, and a diffuse macular rash. Gram stain shows purple cocci in clusters. Which toxin is most likely responsible?
Options:
A. Alpha toxin
B. Toxic shock syndrome toxin 1
C. Enterotoxin B
D. Exfoliative toxin
Proposed Answer: A. Alpha toxin
Reasoning: Alpha toxin is a key virulence factor of Staphylococcus aureus and causes tissue damage.
CORRECTNESS: INCORRECT
RANKING: 3 (B is best, then C/D, then A)
CONFIDENCE: 0.85
EXPLANATION: This is incorrect. The proposed answer is A. Alpha toxin, but while alpha toxin is produced by S. aureus, the clinical presentation (fever, hypotension, diffuse rash) is classic for Toxic Shock Syndrome, which is caused by TSST-1 (option B), not alpha toxin. Therefore, the proposed answer A is wrong.

Example 3 (PROBABLY_CORRECT):
Question: A patient with dermatomyositis is most likely to have autoantibodies against which protein?
Options:
A. Centromeres
B. La protein
C. Ro protein
D. Mi-2 protein
Proposed Answer: D. Mi-2 protein
Reasoning: Dermatomyositis is associated with anti-Mi-2 antibodies.
CORRECTNESS: PROBABLY_CORRECT
RANKING: 1 (best option)
CONFIDENCE: 0.75
EXPLANATION: This is likely correct. Dermatomyositis is indeed associated with anti-Mi-2 antibodies. However, other autoantibodies can also occur.

## YOUR TASK:

Question: {question}

Answer Options:
{options_text}

**PROPOSED ANSWER TO EVALUATE: {answer}**

**CRITICAL: You MUST evaluate ONLY the answer "{answer}" above. Do NOT evaluate what you think the correct answer should be. Evaluate whether "{answer}" is medically correct for this question.**

Reasoning Provided: {reasoning}

EVALUATION STEPS (FOLLOW IN ORDER):
1. Carefully summarize the KEY CLINICAL FEATURES from the question stem (age, symptoms, labs, imaging, risk factors).
2. For EACH answer option, briefly evaluate:
   - How well it fits the clinical features
   - Medical accuracy and relevance
3. RANK all options from best (1) to worst (4 or 5) based on how well they fit the clinical scenario.
4. **CRITICAL STEP**: Identify which option is the proposed answer "{answer}" from the list above.
   - If "{answer}" is a letter (A, B, C, D), find the corresponding option
   - If "{answer}" is text, match it to an option
   - **DO NOT confuse the proposed answer with what you think is correct**
5. Compare the proposed answer "{answer}" against the top-ranked option:
   - If proposed answer "{answer}" ranks #1: Mark as CORRECT or PROBABLY_CORRECT
   - If proposed answer "{answer}" ranks #2: Mark as PROBABLY_CORRECT or LIKELY_CORRECT
   - If proposed answer "{answer}" ranks #3 or lower: Mark as INCORRECT or LIKELY_INCORRECT
6. Check if the medical facts in the reasoning are ACCURATE.
7. Verify if the proposed answer "{answer}" is APPROPRIATE for the clinical scenario.

EVALUATION GUIDELINES:
- Be thorough but not overly skeptical
- If the proposed answer is clearly the best option, mark as CORRECT
- If the proposed answer is likely correct but you have some uncertainty, mark as PROBABLY_CORRECT
- If the proposed answer is plausible but another option is clearly better, mark as LIKELY_INCORRECT
- Only mark as INCORRECT if the answer is clearly wrong or has significant medical inaccuracies

CRITICAL: You MUST provide your evaluation in the EXACT format below at the END of your response:

CORRECTNESS: [CORRECT/PROBABLY_CORRECT/LIKELY_CORRECT/LIKELY_INCORRECT/INCORRECT]
RANKING: [1-5] (where 1 is best option, 5 is worst - rank based on MEDICAL ACCURACY, not just plausibility)
CONFIDENCE: [0.0-1.0] (your confidence in the correctness assessment)
EXPLANATION: [Brief explanation - include your ranking rationale]

IMPORTANT: The RANKING should reflect which option is MEDICALLY MOST ACCURATE for this clinical scenario, not just which seems plausible. If the proposed answer is not the medically best option, do NOT rank it as #1.
"""
        
        response = self.llm_client.generate(
            system_prompt=f"You are evaluating medical answer correctness as a {specialist_name}.",
            user_prompt=prompt,
            temperature=self.temperature,
            max_new_tokens=1000  # Increased from 500 to 1000 to ensure complete responses for complex medical questions
        )
        
        # Parse correctness - BALANCED: Default depends on whether response was complete
        # Check if response seems truncated (doesn't contain CORRECTNESS line)
        has_correctness = bool(re.search(r'CORRECTNESS:', response, re.IGNORECASE))
        if has_correctness:
            correctness_score = 0.30  # Default if parsing fails but response is complete
        else:
            correctness_score = 0.20  # Lower default if response was truncated (more conservative)
        
        # Extract correctness status (now supports more nuanced statuses)
        correct_match = re.search(
            r'CORRECTNESS:\s*(CORRECT|PROBABLY_CORRECT|LIKELY_CORRECT|LIKELY_INCORRECT|INCORRECT|UNCERTAIN)',
            response,
            re.IGNORECASE
        )
        if correct_match:
            status = correct_match.group(1).upper()
            if status == "CORRECT":
                correctness_score = 0.85  # Clearly correct
            elif status == "PROBABLY_CORRECT":
                correctness_score = 0.65  # Likely correct, some uncertainty
            elif status == "LIKELY_CORRECT":
                correctness_score = 0.50  # Plausible but uncertain
            elif status == "LIKELY_INCORRECT":
                correctness_score = 0.30  # Probably wrong but not certain
            elif status == "INCORRECT":
                correctness_score = 0.15  # Clearly wrong
            else:  # UNCERTAIN - treat as LIKELY_CORRECT (less aggressive)
                correctness_score = 0.40  # Moderate uncertainty
        
        # Extract ranking if provided (for relative comparison)
        # Look for "RANKING:" on its own line or followed by number
        ranking_match = re.search(
            r'RANKING:\s*(\d+)',
            response,
            re.IGNORECASE | re.MULTILINE
        )
        ranking_boost = 1.0
        rank = None
        if ranking_match:
            try:
                rank = int(ranking_match.group(1))
                # Only apply ranking boost if correctness status suggests answer is reasonable
                # This prevents wrong answers that rank #1 from getting boosted
                # CRITICAL: Check correctness_score BEFORE applying boost
                if correctness_score > 0.4:  # Only boost if already at least LIKELY_CORRECT
                    if rank == 1:
                        ranking_boost = 1.08  # Reduced to +8% for best option (was 1.10)
                    elif rank == 2:
                        ranking_boost = 1.02  # Reduced to +2% for second best (was 1.03)
                    elif rank >= 4:
                        ranking_boost = 0.92  # Reduced to -8% for low-ranked options (was 0.90)
                else:
                    # If correctness is low, don't apply ranking boost (wrong answer might rank #1 incorrectly)
                    ranking_boost = 1.0  # No boost for low correctness scores
            except ValueError:
                pass
        
        # Extract confidence if provided
        confidence_match = re.search(
            r'CONFIDENCE:\s*(0?\.\d+|\d+\.?\d*)',
            response,
            re.IGNORECASE
        )
        if confidence_match:
            try:
                conf = float(confidence_match.group(1))
                # Adjust correctness score based on confidence (wider ranges)
                if correctness_score > 0.6:  # CORRECT or PROBABLY_CORRECT
                    correctness_score = correctness_score * 0.7 + conf * 0.3  # Blend with confidence
                elif correctness_score > 0.4:  # LIKELY_CORRECT
                    correctness_score = correctness_score * 0.8 + conf * 0.2
                elif correctness_score > 0.2:  # LIKELY_INCORRECT
                    correctness_score = correctness_score * 0.9 + conf * 0.1
                else:  # INCORRECT
                    correctness_score = 0.10 + conf * 0.05  # 0.10-0.15 range
            except ValueError:
                pass
        
        # Apply ranking boost ONLY if correctness is reasonable
        # This prevents wrong answers that incorrectly rank #1 from getting boosted
        if correctness_score > 0.4:  # Only apply boost if at least LIKELY_CORRECT
            correctness_score = correctness_score * ranking_boost
        # If correctness is low, ranking boost is already 1.0, so no change needed
        
        # Less aggressive uncertainty penalties (only for very high scores)
        uncertainty_indicators = ['uncertain', 'not sure', 'might be', 'could be', 'possibly', 'maybe']
        response_lower = response.lower()
        if any(indicator in response_lower for indicator in uncertainty_indicators):
            if correctness_score > 0.75:  # Only penalize very high scores
                correctness_score *= 0.9  # Reduce by 10% (less aggressive)
        
        # Less aggressive doubt penalties (only for very high scores)
        if correctness_score > 0.85:
            doubt_indicators = ['other options', 'could also be', 'alternatively', 'another possibility', 
                              'might also', 'could consider', 'other valid', 'also possible']
            if any(indicator in response_lower for indicator in doubt_indicators):
                correctness_score *= 0.85  # Reduce by 15% (less aggressive)
        
        # CRITICAL FIX: Penalize close but not exact matches
        # "D. Mi-2 protein" should not match "Mi-2 protein" - need exact match
        # Strip letter prefixes from answer for comparison
        answer_clean = re.sub(r'^[A-Z]\.\s*', '', answer, flags=re.IGNORECASE).strip()
        
        # If options are provided, check if answer matches any option exactly
        if options:
            # Get all option texts (strip letter prefixes)
            option_texts = []
            if isinstance(options, list):
                option_texts = [re.sub(r'^[A-Z]\.\s*', '', opt, flags=re.IGNORECASE).strip() for opt in options]
            elif isinstance(options, dict):
                option_texts = [re.sub(r'^[A-Z]\.\s*', '', opt, flags=re.IGNORECASE).strip() for opt in options.values()]
            
            # Check if answer matches any option exactly (case-insensitive)
            answer_matches_option = any(answer_clean.lower() == opt.lower() for opt in option_texts)
            
            # If answer doesn't match any option exactly, it's likely wrong
            if not answer_matches_option and correctness_score > 0.5:
                # Answer doesn't match any option - reduce correctness significantly
                correctness_score *= 0.5  # Reduce by 50% if doesn't match any option
            # If answer has letter prefix but correctness is high, might be close match
            elif re.match(r'^[A-Z]\.\s*', answer, flags=re.IGNORECASE) and correctness_score > 0.7:
                # Answer has letter prefix - might be close but not exact
                # Check if stripped answer matches any option
                stripped_matches = any(answer_clean.lower() == opt.lower() for opt in option_texts)
                if not stripped_matches:
                    correctness_score *= 0.6  # Reduce by 40% if letter-prefixed answer doesn't match exactly
        
        return max(0.0, min(1.0, correctness_score))
    
    def _perform_basic_checks(
        self,
        question: str,
        answer: str,
        reasoning: str
    ) -> Dict[str, bool]:
        """
        Perform basic automated checks on the answer.
        """
        checks = {}
        checks["has_answer"] = bool(answer and answer.strip())
        checks["has_reasoning"] = bool(reasoning and len(reasoning.strip()) > 10)
        
        if answer and reasoning:
            checks["reasoning_mentions_answer"] = answer.upper() in reasoning.upper()
        else:
            checks["reasoning_mentions_answer"] = False
        
        checks["sufficient_reasoning_length"] = len(reasoning) > 50 if reasoning else False
        
        medical_indicators = [
            "patient", "diagnosis", "treatment", "symptom", "disease",
            "condition", "medical", "clinical", "therapy", "pathology"
        ]
        text = (question + " " + reasoning).lower()
        checks["contains_medical_terms"] = any(term in text for term in medical_indicators)
        
        return checks
    
    def verify(
        self,
        question: str,
        answer: str,
        reasoning: str,
        options: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility.
        Use verify_specialist() for proper two-phase self-verification.
        """
        initial_confidence = self._extract_confidence_from_reasoning(reasoning) or 0.7
        return self.verify_specialist(
            specialist_name="Unknown Specialist",
            question=question,
            answer=answer,
            reasoning=reasoning,
            initial_confidence=initial_confidence,
            options=options
        )
    
    def _extract_confidence_from_reasoning(self, reasoning: str) -> Optional[float]:
        """Try to extract confidence score from reasoning text."""
        confidence_match = re.search(
            r'confidence[:\s]+(0?\.\d+|\d+\.?\d*)',
            reasoning,
            re.IGNORECASE
        )
        if confidence_match:
            try:
                return float(confidence_match.group(1))
            except ValueError:
                pass
        return None
    
    def __repr__(self) -> str:
        return "Tier1Verifier()"
