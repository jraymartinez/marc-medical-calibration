"""
Evaluation metrics for medical QA systems.
Includes accuracy, confidence calibration, AUROC, and specialized metrics.
"""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from collections import defaultdict
try:
    from sklearn.metrics import roc_auc_score, roc_curve
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def calculate_accuracy(
    predictions: List[str],
    ground_truth: List[str],
    options: Optional[List[Dict[str, str]]] = None
) -> float:
    """
    Calculate simple accuracy.
    
    Args:
        predictions: List of predicted answers (can be letters or full text)
        ground_truth: List of correct answers (full text)
        options: Optional list of option dictionaries for each question (to convert letters to text)
        
    Returns:
        Accuracy score (0.0-1.0)
    """
    if len(predictions) != len(ground_truth):
        raise ValueError("Predictions and ground truth must have same length")
    
    if len(predictions) == 0:
        return 0.0
    
    import re
    
    correct = 0
    for i, (p, g) in enumerate(zip(predictions, ground_truth)):
        # Normalize prediction: convert letter to full text if needed
        pred_normalized = p.strip()
        if options and i < len(options):
            opt_dict = options[i]
            if isinstance(opt_dict, dict):
                if len(pred_normalized) == 1 and pred_normalized.upper() in opt_dict:
                    pred_normalized = opt_dict[pred_normalized.upper()]
        
        # Strip letter prefixes and normalize
        pred_normalized = re.sub(r'^[A-Z]\.\s*', '', pred_normalized, flags=re.IGNORECASE).strip()
        gt_normalized = re.sub(r'^[A-Z]\.\s*', '', g, flags=re.IGNORECASE).strip()
        
        # Compare (case-insensitive)
        if pred_normalized.lower() == gt_normalized.lower():
            correct += 1
    
    return correct / len(predictions)


def calculate_confidence_metrics(
    predictions: List[str],
    ground_truth: List[str],
    confidences: List[float],
    options: Optional[List[Dict[str, str]]] = None
) -> Dict[str, float]:
    """
    Calculate confidence-related metrics including calibration.
    
    Args:
        predictions: List of predicted answers
        ground_truth: List of correct answers
        confidences: List of confidence scores
        
    Returns:
        Dictionary of confidence metrics
    """
    if not (len(predictions) == len(ground_truth) == len(confidences)):
        raise ValueError("All lists must have same length")
    
    # Accuracy by confidence bins
    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    bin_accuracies = []
    bin_confidences = []
    bin_counts = []
    
    for i in range(len(bins) - 1):
        bin_preds = []
        bin_gts = []
        bin_confs = []
        
        for pred, gt, conf in zip(predictions, ground_truth, confidences):
            if bins[i] <= conf < bins[i + 1] or (i == len(bins) - 2 and conf == 1.0):
                bin_preds.append(pred)
                bin_gts.append(gt)
                bin_confs.append(conf)
        
        if bin_preds:
            # Use options if available for answer matching
            bin_options = None
            if options:
                # Get options for questions in this bin (approximate - use first question's options)
                bin_options = [options[0]] * len(bin_preds) if len(options) > 0 else None
            acc = calculate_accuracy(bin_preds, bin_gts, bin_options)
            avg_conf = np.mean(bin_confs)
            bin_accuracies.append(acc)
            bin_confidences.append(avg_conf)
            bin_counts.append(len(bin_preds))
        else:
            bin_accuracies.append(0.0)
            bin_confidences.append(0.0)
            bin_counts.append(0)
    
    # Expected Calibration Error (ECE)
    ece = 0.0
    total = len(predictions)
    for acc, conf, count in zip(bin_accuracies, bin_confidences, bin_counts):
        if count > 0:
            ece += (count / total) * abs(acc - conf)
    
    # Average confidence
    avg_confidence = np.mean(confidences)
    
    # Confidence on correct vs incorrect (use normalized comparison)
    import re
    correct_confidences = []
    incorrect_confidences = []
    for i, (p, g, c) in enumerate(zip(predictions, ground_truth, confidences)):
        # Normalize prediction
        pred_normalized = p.strip()
        if options and i < len(options):
            opt_dict = options[i]
            if isinstance(opt_dict, dict):
                if len(pred_normalized) == 1 and pred_normalized.upper() in opt_dict:
                    pred_normalized = opt_dict[pred_normalized.upper()]
        
        # Strip prefixes and normalize
        pred_normalized = re.sub(r'^[A-Z]\.\s*', '', pred_normalized, flags=re.IGNORECASE).strip()
        gt_normalized = re.sub(r'^[A-Z]\.\s*', '', g, flags=re.IGNORECASE).strip()
        
        if pred_normalized.lower() == gt_normalized.lower():
            correct_confidences.append(c)
        else:
            incorrect_confidences.append(c)
    
    avg_conf_correct = np.mean(correct_confidences) if correct_confidences else 0.0
    avg_conf_incorrect = np.mean(incorrect_confidences) if incorrect_confidences else 0.0
    
    return {
        "ece": ece,
        "avg_confidence": avg_confidence,
        "avg_confidence_correct": avg_conf_correct,
        "avg_confidence_incorrect": avg_conf_incorrect,
        "bin_accuracies": bin_accuracies,
        "bin_confidences": bin_confidences,
        "bin_counts": bin_counts
    }


def calculate_quality_score_correlation(
    predictions: List[str],
    ground_truth: List[str],
    quality_scores: List[float]
) -> Dict[str, float]:
    """
    Calculate correlation between quality scores and correctness.
    
    Args:
        predictions: List of predicted answers
        ground_truth: List of correct answers
        quality_scores: List of quality scores
        
    Returns:
        Dictionary with correlation metrics
    """
    if not (len(predictions) == len(ground_truth) == len(quality_scores)):
        raise ValueError("All lists must have same length")
    
    correctness = [1 if p == g else 0 for p, g in zip(predictions, ground_truth)]
    
    # Pearson correlation
    if len(correctness) > 1:
        correlation = np.corrcoef(correctness, quality_scores)[0, 1]
    else:
        correlation = 0.0
    
    # Average quality score for correct vs incorrect
    correct_quality = [q for c, q in zip(correctness, quality_scores) if c == 1]
    incorrect_quality = [q for c, q in zip(correctness, quality_scores) if c == 0]
    
    avg_quality_correct = np.mean(correct_quality) if correct_quality else 0.0
    avg_quality_incorrect = np.mean(incorrect_quality) if incorrect_quality else 0.0
    
    return {
        "correlation": correlation if not np.isnan(correlation) else 0.0,
        "avg_quality_correct": avg_quality_correct,
        "avg_quality_incorrect": avg_quality_incorrect
    }


def calculate_auroc(
    predictions: List[str],
    ground_truth: List[str],
    confidences: List[float],
    options: Optional[List[Dict[str, str]]] = None
) -> float:
    """
    Calculate Area Under ROC Curve (AUROC).
    
    Measures how well confidence scores discriminate between correct and incorrect predictions.
    
    Args:
        predictions: List of predicted answers
        ground_truth: List of correct answers
        confidences: List of confidence scores
    
    Returns:
        AUROC score (0.0-1.0), or 0.0 if sklearn not available
    """
    if not SKLEARN_AVAILABLE:
        print("Warning: sklearn not available, AUROC not calculated")
        return 0.0
    
    if len(predictions) != len(ground_truth) or len(predictions) != len(confidences):
        raise ValueError("All lists must have same length")
    
    # Convert to binary labels (1 = correct, 0 = incorrect) with proper answer matching
    import re
    y_true = []
    for i, (p, g) in enumerate(zip(predictions, ground_truth)):
        # Normalize prediction
        pred_normalized = p.strip()
        if options and i < len(options):
            opt_dict = options[i]
            if isinstance(opt_dict, dict):
                if len(pred_normalized) == 1 and pred_normalized.upper() in opt_dict:
                    pred_normalized = opt_dict[pred_normalized.upper()]
        
        # Strip prefixes and normalize
        pred_normalized = re.sub(r'^[A-Z]\.\s*', '', pred_normalized, flags=re.IGNORECASE).strip()
        gt_normalized = re.sub(r'^[A-Z]\.\s*', '', g, flags=re.IGNORECASE).strip()
        
        y_true.append(1 if pred_normalized.lower() == gt_normalized.lower() else 0)
    
    # Check if we have both classes
    if len(set(y_true)) < 2:
        print("Warning: Only one class present, AUROC not meaningful")
        return 0.5
    
    try:
        auroc = roc_auc_score(y_true, confidences)
        return auroc
    except Exception as e:
        print(f"Warning: AUROC calculation failed: {e}")
        return 0.0


def calculate_specialist_agreement(
    specialist_outputs: List[List[Dict[str, Any]]]
) -> Dict[str, float]:
    """
    Calculate agreement metrics among specialists.
    
    Args:
        specialist_outputs: List of specialist output lists for each question
        
    Returns:
        Dictionary with agreement metrics
    """
    if not specialist_outputs:
        return {"avg_agreement": 0.0, "unanimous_percentage": 0.0}
    
    agreements = []
    unanimous_count = 0
    
    for outputs in specialist_outputs:
        if not outputs:
            continue
        
        answers = [o.get("answer") for o in outputs if o.get("answer")]
        if not answers:
            continue
        
        # Most common answer count / total
        from collections import Counter
        answer_counts = Counter(answers)
        most_common_count = answer_counts.most_common(1)[0][1]
        agreement = most_common_count / len(answers)
        agreements.append(agreement)
        
        # Check if unanimous
        if most_common_count == len(answers):
            unanimous_count += 1
    
    avg_agreement = np.mean(agreements) if agreements else 0.0
    unanimous_percentage = unanimous_count / len(specialist_outputs) if specialist_outputs else 0.0
    
    return {
        "avg_agreement": avg_agreement,
        "unanimous_percentage": unanimous_percentage
    }


def calculate_verification_impact(
    results_with_verification: List[Dict[str, Any]],
    results_without_verification: List[Dict[str, Any]],
    ground_truth: List[str]
) -> Dict[str, float]:
    """
    Calculate the impact of verification on results.
    
    Args:
        results_with_verification: Results including verification
        results_without_verification: Baseline results without verification
        ground_truth: Correct answers
        
    Returns:
        Dictionary with impact metrics
    """
    if not (len(results_with_verification) == len(results_without_verification) == len(ground_truth)):
        raise ValueError("All lists must have same length")
    
    # Extract predictions
    preds_with = [r.get("answer") for r in results_with_verification]
    preds_without = [r.get("answer") for r in results_without_verification]
    
    # Calculate accuracies
    acc_with = calculate_accuracy(preds_with, ground_truth)
    acc_without = calculate_accuracy(preds_without, ground_truth)
    
    # Calculate confidence changes
    conf_with = [r.get("confidence", 0.5) for r in results_with_verification]
    conf_without = [r.get("confidence", 0.5) for r in results_without_verification]
    
    avg_conf_change = np.mean([c1 - c2 for c1, c2 in zip(conf_with, conf_without)])
    
    # Count changes
    answer_changes = sum(1 for p1, p2 in zip(preds_with, preds_without) if p1 != p2)
    
    # Count improvements vs degradations
    improvements = sum(1 for p1, p2, gt in zip(preds_with, preds_without, ground_truth)
                      if p1 == gt and p2 != gt)
    degradations = sum(1 for p1, p2, gt in zip(preds_with, preds_without, ground_truth)
                      if p1 != gt and p2 == gt)
    
    return {
        "accuracy_with_verification": acc_with,
        "accuracy_without_verification": acc_without,
        "accuracy_improvement": acc_with - acc_without,
        "avg_confidence_change": avg_conf_change,
        "answer_changes": answer_changes,
        "improvements": improvements,
        "degradations": degradations,
        "net_improvements": improvements - degradations
    }


def generate_evaluation_report(
    predictions: List[str],
    ground_truth: List[str],
    confidences: List[float],
    quality_scores: Optional[List[float]] = None,
    specialist_outputs: Optional[List[List[Dict[str, Any]]]] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive evaluation report.
    
    Args:
        predictions: Predicted answers
        ground_truth: Correct answers
        confidences: Confidence scores
        quality_scores: Quality scores (optional)
        specialist_outputs: Specialist outputs for each question (optional)
        
    Returns:
        Comprehensive evaluation report
    """
    report = {}
    
    # Basic accuracy
    report["accuracy"] = calculate_accuracy(predictions, ground_truth)
    report["total_questions"] = len(predictions)
    report["correct_answers"] = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    
    # Confidence metrics
    report["confidence_metrics"] = calculate_confidence_metrics(
        predictions, ground_truth, confidences
    )
    
    # AUROC
    report["auroc"] = calculate_auroc(predictions, ground_truth, confidences)
    
    # Quality score metrics
    if quality_scores:
        report["quality_metrics"] = calculate_quality_score_correlation(
            predictions, ground_truth, quality_scores
        )
    
    # Specialist agreement
    if specialist_outputs:
        report["specialist_agreement"] = calculate_specialist_agreement(
            specialist_outputs
        )
    
    return report


def print_evaluation_report(report: Dict[str, Any]) -> None:
    """
    Print formatted evaluation report.
    
    Args:
        report: Evaluation report from generate_evaluation_report()
    """
    print("=" * 60)
    print("EVALUATION REPORT")
    print("=" * 60)
    
    print(f"\nOverall Accuracy: {report['accuracy']:.4f}")
    print(f"Correct: {report['correct_answers']} / {report['total_questions']}")
    
    if "auroc" in report:
        print(f"AUROC: {report['auroc']:.4f}")
    
    if "confidence_metrics" in report:
        cm = report["confidence_metrics"]
        print(f"\nConfidence Metrics:")
        print(f"  Average Confidence: {cm['avg_confidence']:.4f}")
        print(f"  ECE (Calibration Error): {cm['ece']:.4f}")
        print(f"  Avg Confidence (Correct): {cm['avg_confidence_correct']:.4f}")
        print(f"  Avg Confidence (Incorrect): {cm['avg_confidence_incorrect']:.4f}")
    
    if "quality_metrics" in report:
        qm = report["quality_metrics"]
        print(f"\nQuality Score Metrics:")
        print(f"  Correlation with Correctness: {qm['correlation']:.4f}")
        print(f"  Avg Quality (Correct): {qm['avg_quality_correct']:.4f}")
        print(f"  Avg Quality (Incorrect): {qm['avg_quality_incorrect']:.4f}")
    
    if "specialist_agreement" in report:
        sa = report["specialist_agreement"]
        print(f"\nSpecialist Agreement:")
        print(f"  Average Agreement: {sa['avg_agreement']:.4f}")
        print(f"  Unanimous Decisions: {sa['unanimous_percentage']:.2%}")
    
    print("=" * 60)
