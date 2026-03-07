"""
S-Score Weighted Fusion Strategy

Winner Selection: score = vote_count × mean_S_score
Confidence Calibration: Vote-strength weighted (blend of mean and min)

Rationale:
- Winner: Balances majority voting with verification quality (S-scores)
- Confidence: Weighted by vote strength to reduce underconfidence
- When all specialists agree: High confidence (max S-score)
- When specialists disagree: Weighted confidence based on agreement level
"""

from typing import List, Dict, Any, Tuple
import numpy as np


class SScoreWeightedFusion:
    """
    S-Score Weighted Fusion leverages verification quality (S-scores) to weight
    both answer selection and confidence calibration.
    
    Strategy: 
      Winner = answer with highest (vote_count × mean_S_score)
      Confidence = vote-strength weighted blend of mean and min S-scores
    """
    
    def __init__(self):
        """Initialize S-Score Weighted Fusion."""
        self.name = "S-Score Weighted Fusion"
    
    def fuse(self, specialist_outputs: List[Dict[str, Any]]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Fuse specialist outputs using agreement-based confidence.
        
        Args:
            specialist_outputs: List of dicts with keys:
                - specialist: str (specialty name)
                - answer: str (predicted answer)
                - confidence: float (initial confidence)
                - S_score: float (specialist confidence score from 2P verification)
        
        Returns:
            Tuple of (final_answer, final_confidence, debug_info)
        """
        if not specialist_outputs:
            return "", 0.0, {"error": "No specialist outputs"}
        
        # Extract answers and S-scores
        answers = [spec['answer'] for spec in specialist_outputs]
        s_scores = [spec.get('S_score', spec.get('confidence', 0.0)) for spec in specialist_outputs]
        
        # Count votes for each answer
        from collections import Counter
        vote_counts = Counter(answers)
        
        # Check if all specialists agree
        all_agree = len(vote_counts) == 1
        
        # Option B: S-score weighted voting
        # Calculate score for each answer: vote_count × mean_S_score
        answer_scores = {}
        answer_s_scores = {}
        
        for ans in vote_counts.keys():
            supporters = [spec for spec in specialist_outputs if spec['answer'] == ans]
            s_scores_for_ans = [spec.get('S_score', spec.get('confidence', 0.0)) for spec in supporters]
            
            vote_count = len(supporters)
            mean_s = np.mean(s_scores_for_ans) if s_scores_for_ans else 0.0
            
            # Score = vote_count × mean_S_score
            answer_scores[ans] = vote_count * mean_s
            answer_s_scores[ans] = s_scores_for_ans
        
        # Pick answer with highest score
        winning_answer = max(answer_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence based on agreement (Option A: vote-strength weighted)
        if all_agree:
            # All agree: Use max S-score (high confidence)
            final_confidence = float(max(s_scores))
            confidence_reason = "all_agree_max_s"
        else:
            # Disagree: Use weighted confidence based on vote strength (Option A)
            winner_s_scores = answer_s_scores.get(winning_answer, [])
            
            if not winner_s_scores:
                # Fallback: shouldn't happen, but handle gracefully
                final_confidence = float(min(s_scores))
                confidence_reason = "disagree_fallback"
            else:
                # Calculate vote strength (fraction of specialists supporting winner)
                vote_strength = len(winner_s_scores) / len(specialist_outputs)
                
                # Weighted confidence: blend mean and min based on vote strength
                # Strong majority (vote_strength=0.75-1.0): Use more of mean (higher confidence)
                # Weak majority (vote_strength=0.5): Use more of min (lower confidence)
                mean_winner_s = float(np.mean(winner_s_scores))
                min_winner_s = float(min(winner_s_scores))
                
                final_confidence = vote_strength * mean_winner_s + (1 - vote_strength) * min_winner_s
                confidence_reason = f"disagree_weighted_vs{vote_strength:.2f}"
        
        # Create debug info
        debug_info = {
            "all_agree": all_agree,
            "vote_counts": dict(vote_counts),
            "answer_scores": {k: float(v) for k, v in answer_scores.items()},
            "winning_answer": winning_answer,
            "winning_score": float(answer_scores[winning_answer]),
            "s_scores": s_scores,
            "min_s_score": float(min(s_scores)),
            "max_s_score": float(max(s_scores)),
            "mean_s_score": float(np.mean(s_scores)),
            "final_confidence": final_confidence,
            "confidence_reason": confidence_reason,
        }
        
        return winning_answer, final_confidence, debug_info
    
    def __str__(self):
        return self.name


def create_s_score_weighted_fusion() -> SScoreWeightedFusion:
    """Factory function to create S-Score Weighted Fusion."""
    return SScoreWeightedFusion()
