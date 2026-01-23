"""
Hierarchical Integration Methods for combining Specialist (S) and GP (G) scores.

Four methods for Paper 1:
1. Linear: C = α*S + (1-α)*G
2. Multiplicative: C = S^γ × G^(1-γ)
3. Bayesian: P(Correct|S,G) using conditional probabilities
4. Threshold: Rule-based min/max logic
"""
import numpy as np
from typing import Dict, Any, List, Optional
from scipy import stats


def linear_integration(
    S_score: float,
    G_score: float,
    alpha: float = 0.5
) -> float:
    """
    Linear hierarchical integration.
    
    C = α*S + (1-α)*G
    
    Args:
        S_score: Specialist confidence score (Tier 1)
        G_score: GP validation confidence score (Tier 2)
        alpha: Weight for specialist score (0 to 1)
            - α=1.0: Only specialist score
            - α=0.5: Equal weight
            - α=0.0: Only GP score
    
    Returns:
        Combined confidence score C
    """
    if not (0 <= alpha <= 1):
        raise ValueError("Alpha must be between 0 and 1")
    
    C = alpha * S_score + (1 - alpha) * G_score
    return max(0.0, min(1.0, C))


def multiplicative_integration(
    S_score: float,
    G_score: float,
    gamma: float = 0.5
) -> float:
    """
    Multiplicative hierarchical integration.
    
    C = S^γ × G^(1-γ)
    
    Args:
        S_score: Specialist confidence score (Tier 1)
        G_score: GP validation confidence score (Tier 2)
        gamma: Weight exponent (0 to 1)
            - γ=1.0: Only specialist score
            - γ=0.5: Equal weight (geometric mean)
            - γ=0.0: Only GP score
    
    Returns:
        Combined confidence score C
    """
    if not (0 <= gamma <= 1):
        raise ValueError("Gamma must be between 0 and 1")
    
    # Avoid log(0) issues
    S_safe = max(0.01, min(0.99, S_score))
    G_safe = max(0.01, min(0.99, G_score))
    
    C = (S_safe ** gamma) * (G_safe ** (1 - gamma))
    return max(0.0, min(1.0, C))


def bayesian_integration(
    S_score: float,
    G_score: float,
    prior: float = 0.5,
    S_reliability: float = 0.8,
    G_reliability: float = 0.85
) -> float:
    """
    Bayesian hierarchical integration.
    
    P(Correct | S, G) using Bayes' theorem with conditional independence assumption.
    
    Args:
        S_score: Specialist confidence score (Tier 1)
        G_score: GP validation confidence score (Tier 2)
        prior: Prior probability of correct answer
        S_reliability: How reliable specialist scores are (accuracy of S)
        G_reliability: How reliable GP scores are (accuracy of G)
    
    Returns:
        Posterior probability C
    """
    # Use Bayesian updating
    # P(Correct | S) ∝ P(S | Correct) * P(Correct)
    # P(S | Correct) = S_score * S_reliability + (1-S_score) * (1-S_reliability)
    
    # Likelihood of observing S given answer is correct
    P_S_given_correct = S_score * S_reliability + (1 - S_score) * (1 - S_reliability)
    
    # Likelihood of observing S given answer is incorrect
    P_S_given_incorrect = S_score * (1 - S_reliability) + (1 - S_score) * S_reliability
    
    # Update prior with S
    posterior_after_S = (P_S_given_correct * prior) / (
        P_S_given_correct * prior + P_S_given_incorrect * (1 - prior)
    )
    
    # Now update with G using posterior_after_S as new prior
    P_G_given_correct = G_score * G_reliability + (1 - G_score) * (1 - G_reliability)
    P_G_given_incorrect = G_score * (1 - G_reliability) + (1 - G_score) * G_reliability
    
    C = (P_G_given_correct * posterior_after_S) / (
        P_G_given_correct * posterior_after_S + P_G_given_incorrect * (1 - posterior_after_S)
    )
    
    return max(0.0, min(1.0, C))


def threshold_integration(
    S_score: float,
    G_score: float,
    high_threshold: float = 0.8,
    low_threshold: float = 0.6,
    rules: str = "min_max"
) -> float:
    """
    Threshold-based hierarchical integration.
    
    Uses rule-based logic with thresholds.
    
    Args:
        S_score: Specialist confidence score (Tier 1)
        G_score: GP validation confidence score (Tier 2)
        high_threshold: Threshold for high confidence
        low_threshold: Threshold for low confidence
        rules: Integration rule ("min_max", "conservative", "optimistic")
    
    Returns:
        Combined confidence score C
    """
    if rules == "min_max":
        # If both agree high → high confidence
        if S_score >= high_threshold and G_score >= high_threshold:
            C = max(S_score, G_score)
        # If both agree low → low confidence
        elif S_score < low_threshold and G_score < low_threshold:
            C = min(S_score, G_score)
        # If disagreement → average
        else:
            C = (S_score + G_score) / 2
    
    elif rules == "conservative":
        # Always use minimum (most conservative)
        C = min(S_score, G_score)
    
    elif rules == "optimistic":
        # Always use maximum (most optimistic)
        C = max(S_score, G_score)
    
    else:
        # Default: weighted average
        C = 0.6 * S_score + 0.4 * G_score
    
    return max(0.0, min(1.0, C))


def integrate_scores(
    S_score: float,
    G_score: float,
    method: str = "linear",
    **kwargs
) -> float:
    """
    General interface for hierarchical integration.
    
    Args:
        S_score: Specialist confidence score (Tier 1)
        G_score: GP validation confidence score (Tier 2)
        method: Integration method ("linear", "multiplicative", "bayesian", "threshold")
        **kwargs: Method-specific parameters
    
    Returns:
        Combined confidence score C
    """
    if method == "linear":
        return linear_integration(S_score, G_score, alpha=kwargs.get("alpha", 0.5))
    elif method == "multiplicative":
        return multiplicative_integration(S_score, G_score, gamma=kwargs.get("gamma", 0.5))
    elif method == "bayesian":
        return bayesian_integration(
            S_score, G_score,
            prior=kwargs.get("prior", 0.5),
            S_reliability=kwargs.get("S_reliability", 0.8),
            G_reliability=kwargs.get("G_reliability", 0.85)
        )
    elif method == "threshold":
        return threshold_integration(
            S_score, G_score,
            high_threshold=kwargs.get("high_threshold", 0.8),
            low_threshold=kwargs.get("low_threshold", 0.6),
            rules=kwargs.get("rules", "min_max")
        )
    else:
        raise ValueError(f"Unknown integration method: {method}")


def fuse_multi_specialist_scores(
    specialist_scores: List[Dict[str, Any]],
    method: str = "equal_weight"
) -> Dict[str, Any]:
    """
    Fuse scores from multiple specialists (Paper 1: equal weights).
    
    Args:
        specialist_scores: List of specialist results with hierarchical confidence scores
        method: Fusion method ("equal_weight", "weighted", "voting")
    
    Returns:
        Dictionary with final answer, confidence, and metadata
    """
    if not specialist_scores:
        raise ValueError("No specialist scores provided")
    
    if method == "equal_weight":
        # Equal-weight averaging (Paper 1)
        confidences = [s["hierarchical_confidence"] for s in specialist_scores]
        final_confidence = np.mean(confidences)
        
        # Choose answer from most confident specialist
        best_specialist = max(specialist_scores, key=lambda s: s["hierarchical_confidence"])
        final_answer = best_specialist["answer"]
        
        # Aggregate reasoning
        reasoning_parts = [
            f"{s['specialist']}: {s.get('reasoning', 'No reasoning')[:200]}..."
            for s in specialist_scores
        ]
        
        return {
            "answer": final_answer,
            "confidence": final_confidence,
            "reasoning": "\n\n".join(reasoning_parts),
            "fusion_method": "equal_weight",
            "num_specialists": len(specialist_scores),
            "specialist_confidences": confidences,
            "agreement_level": np.std(confidences)  # Lower std = more agreement
        }
    
    elif method == "weighted":
        # Confidence-weighted fusion (Paper 2)
        confidences = np.array([s["hierarchical_confidence"] for s in specialist_scores])
        weights = confidences / confidences.sum()
        
        # Weighted voting
        answers = [s["answer"] for s in specialist_scores]
        from collections import Counter
        answer_votes = Counter()
        for answer, weight in zip(answers, weights):
            answer_votes[answer] += weight
        
        final_answer = answer_votes.most_common(1)[0][0]
        final_confidence = confidences.mean()  # Or use weighted average
        
        return {
            "answer": final_answer,
            "confidence": final_confidence,
            "fusion_method": "weighted",
            "num_specialists": len(specialist_scores)
        }
    
    else:
        raise ValueError(f"Unknown fusion method: {method}")
