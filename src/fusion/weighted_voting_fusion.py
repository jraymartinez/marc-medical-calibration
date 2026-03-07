"""
Simple weighted voting fusion by S-score.
No heuristic thresholds, no complex rules - just weighted voting.

This approach is designed to be generalizable across datasets.
"""

from typing import List, Dict, Any, Tuple
import numpy as np


def weighted_voting_fusion(
    specialist_results: List[Dict[str, Any]]
) -> Tuple[str, float, Dict[str, Any]]:
    """
    Fuse specialist opinions using weighted voting by S-score.
    
    Simple algorithm:
    1. Each specialist votes for their answer
    2. Vote weight = S-score (confidence after two-phase verification)
    3. Answer with highest total weight wins
    4. Final confidence = average S-score of supporting specialists
    
    No temperature scaling - we trust the S-score calibration from Two-Phase Verification.
    
    Args:
        specialist_results: List of dicts with keys:
            - 'specialist': specialist name
            - 'answer': chosen answer (A/B/C/D)
            - 'S_score': confidence score (0-1)
            - 'verified_status': verification status (not used in weighted voting)
    
    Returns:
        Tuple of (final_answer, final_confidence, metadata)
    """
    if not specialist_results:
        raise ValueError("No specialist results provided")
    
    # Collect weighted votes
    votes = {}
    for result in specialist_results:
        answer = result['answer']
        s_score = result['S_score']
        specialist = result['specialist']
        
        if answer not in votes:
            votes[answer] = {
                'total_weight': 0.0,
                'count': 0,
                'specialists': [],
                's_scores': []
            }
        
        votes[answer]['total_weight'] += s_score
        votes[answer]['count'] += 1
        votes[answer]['specialists'].append(specialist)
        votes[answer]['s_scores'].append(s_score)
    
    # Select answer with highest weighted vote
    final_answer = max(votes.items(), key=lambda x: x[1]['total_weight'])[0]
    
    # Calculate final confidence (average S-score of supporting specialists)
    supporting_s_scores = votes[final_answer]['s_scores']
    avg_s_score = np.mean(supporting_s_scores)
    
    # DEBUG: Print fusion details (simplified)
    vote_summary = {ans: f"{v['count']} votes (weight={v['total_weight']:.2f})" for ans, v in votes.items()}
    print(f"DEBUG FUSION: Votes={vote_summary}, Winner={final_answer}, Conf={avg_s_score:.3f}", flush=True)
    
    # Use S-score directly - no temperature scaling
    # S-scores from Two-Phase Verification are already calibrated
    final_confidence = float(avg_s_score)
    
    # Build metadata for analysis
    metadata = {
        'fusion_method': 'weighted_voting',
        'num_specialists': len(specialist_results),
        'num_answers': len(votes),
        'final_answer': final_answer,
        'num_supporting': votes[final_answer]['count'],
        'supporting_specialists': votes[final_answer]['specialists'],
        'vote_distribution': {ans: v['count'] for ans, v in votes.items()},
        'weight_distribution': {ans: round(v['total_weight'], 3) for ans, v in votes.items()},
        'avg_s_score': round(avg_s_score, 3),
        'all_s_scores': [r['S_score'] for r in specialist_results]
    }
    
    return final_answer, final_confidence, metadata


def analyze_fusion_decision(
    specialist_results: List[Dict[str, Any]],
    final_answer: str,
    metadata: Dict[str, Any]
) -> str:
    """
    Generate human-readable description of fusion decision.
    
    Args:
        specialist_results: Original specialist results
        final_answer: Final fused answer
        metadata: Metadata from weighted_voting_fusion
    
    Returns:
        String description of the decision
    """
    num_specialists = len(specialist_results)
    num_supporting = metadata['num_supporting']
    vote_dist = metadata['vote_distribution']
    weight_dist = metadata['weight_distribution']
    
    # Classify decision type
    if num_supporting == num_specialists:
        decision_type = "unanimous_consensus"
        description = f"All {num_specialists} specialists agreed on {final_answer}"
    elif num_supporting >= num_specialists * 0.75:
        decision_type = "strong_majority"
        description = f"Strong majority ({num_supporting}/{num_specialists}) voted for {final_answer}"
    elif num_supporting > num_specialists / 2:
        decision_type = "simple_majority"
        description = f"Simple majority ({num_supporting}/{num_specialists}) voted for {final_answer}"
    elif num_supporting == num_specialists / 2:
        decision_type = "tie_broken_by_weight"
        description = f"Tie ({num_supporting}/{num_specialists}), broken by weighted vote (total weight: {weight_dist[final_answer]:.3f})"
    else:
        decision_type = "minority_high_confidence"
        description = f"Minority ({num_supporting}/{num_specialists}) won with higher confidence (total weight: {weight_dist[final_answer]:.3f})"
    
    # Add vote distribution
    vote_summary = ", ".join([f"{ans}: {count} votes (weight: {weight_dist[ans]:.3f})" 
                              for ans, count in sorted(vote_dist.items())])
    
    full_description = f"{description}\nVote distribution: {vote_summary}"
    
    return full_description


# Example usage and testing
if __name__ == "__main__":
    # Test case 1: Unanimous consensus
    print("=" * 70)
    print("Test 1: Unanimous Consensus")
    print("=" * 70)
    results1 = [
        {'specialist': 'respiratory', 'answer': 'A', 'S_score': 0.85, 'verified_status': 'YES'},
        {'specialist': 'cardiology', 'answer': 'A', 'S_score': 0.90, 'verified_status': 'YES'},
        {'specialist': 'neurology', 'answer': 'A', 'S_score': 0.80, 'verified_status': 'YES'},
        {'specialist': 'gastroenterology', 'answer': 'A', 'S_score': 0.88, 'verified_status': 'YES'},
    ]
    answer1, conf1, meta1 = weighted_voting_fusion(results1)
    print(f"Final answer: {answer1}")
    print(f"Final confidence: {conf1:.3f}")
    print(f"Metadata: {meta1}")
    print(f"\nDecision: {analyze_fusion_decision(results1, answer1, meta1)}")
    
    # Test case 2: Strong majority (3 vs 1)
    print("\n" + "=" * 70)
    print("Test 2: Strong Majority (3 vs 1)")
    print("=" * 70)
    results2 = [
        {'specialist': 'respiratory', 'answer': 'B', 'S_score': 0.75, 'verified_status': 'YES'},
        {'specialist': 'cardiology', 'answer': 'B', 'S_score': 0.80, 'verified_status': 'YES'},
        {'specialist': 'neurology', 'answer': 'B', 'S_score': 0.70, 'verified_status': 'UNCERTAIN'},
        {'specialist': 'gastroenterology', 'answer': 'A', 'S_score': 0.90, 'verified_status': 'YES'},
    ]
    answer2, conf2, meta2 = weighted_voting_fusion(results2)
    print(f"Final answer: {answer2}")
    print(f"Final confidence: {conf2:.3f}")
    print(f"Metadata: {meta2}")
    print(f"\nDecision: {analyze_fusion_decision(results2, answer2, meta2)}")
    
    # Test case 3: Tie broken by weight (2 vs 2, different confidences)
    print("\n" + "=" * 70)
    print("Test 3: Tie Broken by Weight (2 vs 2)")
    print("=" * 70)
    results3 = [
        {'specialist': 'respiratory', 'answer': 'C', 'S_score': 0.85, 'verified_status': 'YES'},
        {'specialist': 'cardiology', 'answer': 'C', 'S_score': 0.80, 'verified_status': 'YES'},
        {'specialist': 'neurology', 'answer': 'D', 'S_score': 0.70, 'verified_status': 'UNCERTAIN'},
        {'specialist': 'gastroenterology', 'answer': 'D', 'S_score': 0.65, 'verified_status': 'UNCERTAIN'},
    ]
    answer3, conf3, meta3 = weighted_voting_fusion(results3)
    print(f"Final answer: {answer3}")
    print(f"Final confidence: {conf3:.3f}")
    print(f"Metadata: {meta3}")
    print(f"\nDecision: {analyze_fusion_decision(results3, answer3, meta3)}")
    
    # Test case 4: High-confidence minority wins (1 vs 1 vs 1 vs 1)
    print("\n" + "=" * 70)
    print("Test 4: Complete Disagreement (1-1-1-1)")
    print("=" * 70)
    results4 = [
        {'specialist': 'respiratory', 'answer': 'A', 'S_score': 0.95, 'verified_status': 'YES'},
        {'specialist': 'cardiology', 'answer': 'B', 'S_score': 0.70, 'verified_status': 'UNCERTAIN'},
        {'specialist': 'neurology', 'answer': 'C', 'S_score': 0.65, 'verified_status': 'UNCERTAIN'},
        {'specialist': 'gastroenterology', 'answer': 'D', 'S_score': 0.60, 'verified_status': 'NO'},
    ]
    answer4, conf4, meta4 = weighted_voting_fusion(results4)
    print(f"Final answer: {answer4}")
    print(f"Final confidence: {conf4:.3f}")
    print(f"Metadata: {meta4}")
    print(f"\nDecision: {analyze_fusion_decision(results4, answer4, meta4)}")
