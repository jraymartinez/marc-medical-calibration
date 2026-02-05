"""
Generate Publication-Quality Visualizations for Paper 1
Creates calibration plots, ROC curves, and accuracy comparisons
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set publication-quality style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'


def load_comparison_results(file_path: str) -> Dict[str, Any]:
    """Load comparison results from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_metrics(config_result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract predictions, ground truth, and confidences from config results."""
    predictions = []
    ground_truth = []
    confidences = []
    is_correct = []
    
    for q in config_result['question_results']:
        predictions.append(q['final_answer'])
        ground_truth.append(q['correct_answer'])
        confidences.append(q['final_confidence'])
        is_correct.append(1 if q['is_correct'] else 0)
    
    return {
        'predictions': predictions,
        'ground_truth': ground_truth,
        'confidences': confidences,
        'is_correct': is_correct,
        'metrics': config_result['metrics']
    }


def calculate_calibration_curve(confidences: List[float], is_correct: List[int], n_bins: int = 10):
    """Calculate calibration curve data."""
    confidences = np.array(confidences)
    is_correct = np.array(is_correct)
    
    # Create bins
    bins = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    bin_accuracies = []
    bin_confidences = []
    bin_counts = []
    
    for i in range(n_bins):
        bin_mask = (confidences >= bins[i]) & (confidences < bins[i + 1])
        if i == n_bins - 1:  # Include 1.0 in last bin
            bin_mask = (confidences >= bins[i]) & (confidences <= bins[i + 1])
        
        if bin_mask.sum() > 0:
            bin_acc = is_correct[bin_mask].mean()
            bin_conf = confidences[bin_mask].mean()
            bin_count = bin_mask.sum()
        else:
            bin_acc = 0.0
            bin_conf = bin_centers[i]
            bin_count = 0
        
        bin_accuracies.append(bin_acc)
        bin_confidences.append(bin_conf)
        bin_counts.append(bin_count)
    
    return np.array(bin_confidences), np.array(bin_accuracies), np.array(bin_counts)


def calculate_roc_curve(confidences: List[float], is_correct: List[int]):
    """Calculate ROC curve data."""
    confidences = np.array(confidences)
    is_correct = np.array(is_correct)
    
    # Sort by confidence (descending)
    sorted_indices = np.argsort(-confidences)
    sorted_correct = is_correct[sorted_indices]
    
    # Calculate TPR and FPR at each threshold
    tpr = []
    fpr = []
    
    total_positive = is_correct.sum()
    total_negative = len(is_correct) - total_positive
    
    tp = 0
    fp = 0
    
    for correct in sorted_correct:
        if correct == 1:
            tp += 1
        else:
            fp += 1
        
        tpr.append(tp / total_positive if total_positive > 0 else 0)
        fpr.append(fp / total_negative if total_negative > 0 else 0)
    
    # Add (0, 0) and (1, 1) points
    tpr = [0] + tpr + [1]
    fpr = [0] + fpr + [1]
    
    return np.array(fpr), np.array(tpr)


def plot_calibration_analysis(all_configs: Dict[str, Dict], output_path: str):
    """
    Generate calibration analysis plot (reliability diagram).
    Shows predicted confidence vs actual accuracy.
    """
    fig, ax = plt.subplots(figsize=(6, 5))
    
    colors = {
        'Single Specialist': '#95A5A6',
        'Single Specialist + Two-Phase Verification': '#3498DB',
        'Multi-Agent (No Verification)': '#2ECC71',
        'Multi-Agent + Two-Phase Verification': '#9B59B6'
    }
    
    # Plot perfect calibration line
    ax.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Perfect Calibration', alpha=0.5)
    
    # Plot each configuration
    for config_name, config_data in all_configs.items():
        bin_confs, bin_accs, bin_counts = calculate_calibration_curve(
            config_data['confidences'], 
            config_data['is_correct']
        )
        
        # Plot line
        ax.plot(bin_confs, bin_accs, 'o-', 
                color=colors.get(config_name, '#34495E'),
                linewidth=2, markersize=6,
                label=f"{config_name} (ECE={config_data['metrics']['ece']:.3f})",
                alpha=0.8)
    
    ax.set_xlabel('Predicted Confidence', fontweight='bold')
    ax.set_ylabel('Actual Accuracy', fontweight='bold')
    ax.set_title('Calibration Analysis: Confidence vs Accuracy', fontweight='bold', pad=15)
    ax.legend(loc='upper left', framealpha=0.95, fontsize=8)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_aspect('equal')
    
    # Add goal annotation
    ax.text(0.98, 0.02, 'Goal: ECE < 0.05\n(well-calibrated)', 
            transform=ax.transAxes, fontsize=9,
            horizontalalignment='right', verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved calibration plot: {output_path}")
    plt.close()


def plot_roc_analysis(all_configs: Dict[str, Dict], output_path: str):
    """
    Generate ROC curve analysis plot.
    Shows discrimination ability (error detection).
    """
    fig, ax = plt.subplots(figsize=(6, 5))
    
    colors = {
        'Single Specialist': '#95A5A6',
        'Single Specialist + Two-Phase Verification': '#3498DB',
        'Multi-Agent (No Verification)': '#2ECC71',
        'Multi-Agent + Two-Phase Verification': '#9B59B6'
    }
    
    # Plot random classifier line
    ax.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Random', alpha=0.5)
    
    # Plot each configuration
    for config_name, config_data in all_configs.items():
        fpr, tpr = calculate_roc_curve(
            config_data['confidences'], 
            config_data['is_correct']
        )
        
        # Calculate AUC using trapezoidal rule
        auc = np.trapz(tpr, fpr)
        
        # Plot curve
        ax.plot(fpr, tpr, 
                color=colors.get(config_name, '#34495E'),
                linewidth=2.5,
                label=f"{config_name} (AUROC={auc:.3f})",
                alpha=0.8)
    
    ax.set_xlabel('False Positive Rate', fontweight='bold')
    ax.set_ylabel('True Positive Rate', fontweight='bold')
    ax.set_title('Discrimination Analysis: Error Detection via Confidence', fontweight='bold', pad=15)
    ax.legend(loc='lower right', fontsize=7, framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved ROC plot: {output_path}")
    plt.close()


def mcnemar_test(correct1: List[int], correct2: List[int]) -> Dict[str, float]:
    """
    Perform McNemar's test for paired binary outcomes.
    Tests if two configurations have significantly different error rates.
    """
    correct1 = np.array(correct1)
    correct2 = np.array(correct2)
    
    # Create contingency table
    # b = correct in config1 but wrong in config2
    # c = wrong in config1 but correct in config2
    b = ((correct1 == 1) & (correct2 == 0)).sum()
    c = ((correct1 == 0) & (correct2 == 1)).sum()
    
    # McNemar's test statistic (with continuity correction)
    if b + c == 0:
        return {'statistic': 0.0, 'p_value': 1.0}
    
    statistic = (abs(b - c) - 1) ** 2 / (b + c)
    p_value = 1 - stats.chi2.cdf(statistic, df=1)
    
    return {'statistic': statistic, 'p_value': p_value}


def plot_accuracy_comparison(all_configs: Dict[str, Dict], output_path: str, baseline_name: str = 'Single Specialist'):
    """
    Generate accuracy comparison bar chart with significance testing.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Configuration order
    config_order = ['Single Specialist', 'Single Specialist + Two-Phase Verification', 
                    'Multi-Agent (No Verification)', 'Multi-Agent + Two-Phase Verification']
    
    colors = {
        'Single Specialist': '#95A5A6',
        'Single Specialist + Two-Phase Verification': '#3498DB',
        'Multi-Agent (No Verification)': '#2ECC71',
        'Multi-Agent + Two-Phase Verification': '#9B59B6'
    }
    
    # Extract accuracies
    accuracies = []
    config_names = []
    bar_colors = []
    
    for config_name in config_order:
        if config_name in all_configs:
            accuracies.append(all_configs[config_name]['metrics']['accuracy'] * 100)
            config_names.append(config_name.replace(' (a=0.5)', '\n(α=0.5)'))
            bar_colors.append(colors.get(config_name, '#34495E'))
    
    # Create bars
    x = np.arange(len(config_names))
    bars = ax.bar(x, accuracies, color=bar_colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (bar, acc) in enumerate(zip(bars, accuracies)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{acc:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Removed significance testing for cleaner visualization
    
    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_xlabel('Configuration', fontweight='bold')
    ax.set_title('Accuracy Comparison Across Configurations', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(config_names, rotation=25, ha='right', fontsize=9)
    if accuracies:
        ax.set_ylim([0, max(accuracies) + 10])
    else:
        ax.set_ylim([0, 100])
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved accuracy comparison: {output_path}")
    plt.close()


def plot_combined_figure(all_configs: Dict[str, Dict], output_path: str):
    """
    Generate combined figure with all three analyses (like the example image).
    """
    fig = plt.figure(figsize=(16, 5))
    gs = fig.add_gridspec(1, 3, hspace=0.3, wspace=0.3)
    
    colors = {
        'Single Specialist': '#95A5A6',
        'Single Specialist + Two-Phase Verification': '#3498DB',
        'Multi-Agent (No Verification)': '#2ECC71',
        'Multi-Agent + Two-Phase Verification': '#9B59B6'
    }
    
    # --- Panel 1: Calibration Analysis ---
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Perfect', alpha=0.5)
    
    for config_name, config_data in all_configs.items():
        bin_confs, bin_accs, _ = calculate_calibration_curve(
            config_data['confidences'], 
            config_data['is_correct']
        )
        ax1.plot(bin_confs, bin_accs, 'o-', 
                color=colors.get(config_name, '#34495E'),
                linewidth=2, markersize=5,
                label=config_name.replace(' (a=0.5)', ''),
                alpha=0.8)
    
    ax1.set_xlabel('Predicted Confidence', fontweight='bold')
    ax1.set_ylabel('Actual Accuracy', fontweight='bold')
    ax1.set_title('Calibration Analysis\nPrimary Validation', fontweight='bold', fontsize=12)
    ax1.legend(loc='upper left', fontsize=7, framealpha=0.95)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 1])
    ax1.set_ylim([0, 1])
    ax1.set_aspect('equal')
    
    # --- Panel 2: Discrimination Analysis ---
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Random', alpha=0.5)
    
    for config_name, config_data in all_configs.items():
        fpr, tpr = calculate_roc_curve(
            config_data['confidences'], 
            config_data['is_correct']
        )
        ax2.plot(fpr, tpr, 
                color=colors.get(config_name, '#34495E'),
                linewidth=2.5,
                label=config_name.replace(' (a=0.5)', ''),
                alpha=0.8)
    
    ax2.set_xlabel('False Positive Rate', fontweight='bold')
    ax2.set_ylabel('True Positive Rate', fontweight='bold')
    ax2.set_title('Discrimination Analysis\nError Detection', fontweight='bold', fontsize=12)
    ax2.legend(loc='lower right', fontsize=7, framealpha=0.95)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 1])
    ax2.set_ylim([0, 1])
    ax2.set_aspect('equal')
    
    # --- Panel 3: Accuracy Comparison ---
    ax3 = fig.add_subplot(gs[0, 2])
    
    config_order = ['Single Specialist', 'Single Specialist + Two-Phase Verification', 
                    'Multi-Agent (No Verification)', 'Multi-Agent + Two-Phase Verification']
    accuracies = []
    config_labels = []
    bar_colors_list = []
    
    for config_name in config_order:
        if config_name in all_configs:
            accuracies.append(all_configs[config_name]['metrics']['accuracy'] * 100)
            
            # Short labels
            label_map = {
                'Single Specialist': 'Single\nSpec',
                'Single Specialist + Two-Phase Verification': 'Single\n+ 2Phase',
                'Multi-Agent (No Verification)': 'Multi\nNo Verif',
                'Multi-Agent + Two-Phase Verification': 'Multi\n+ 2Phase'
            }
            config_labels.append(label_map.get(config_name, config_name))
            bar_colors_list.append(colors.get(config_name, '#34495E'))
    
    x = np.arange(len(config_labels))
    bars = ax3.bar(x, accuracies, color=bar_colors_list, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{acc:.0f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    ax3.set_ylabel('Accuracy (%)', fontweight='bold')
    ax3.set_title('Accuracy Comparison\nBaseline Performance', fontweight='bold', fontsize=12)
    ax3.set_xticks(x)
    ax3.set_xticklabels(config_labels, fontsize=9)
    if accuracies:
        ax3.set_ylim([0, max(accuracies) + 8])
    else:
        ax3.set_ylim([0, 100])
    ax3.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved combined figure: {output_path}")
    plt.close()


def generate_metrics_table(all_configs: Dict[str, Dict], output_path: str):
    """Generate LaTeX table with all metrics."""
    table_lines = []
    table_lines.append("\\begin{table}[h]")
    table_lines.append("\\centering")
    table_lines.append("\\caption{Performance Comparison of Hierarchical Verification Configurations}")
    table_lines.append("\\label{tab:paper1_results}")
    table_lines.append("\\begin{tabular}{lcccc}")
    table_lines.append("\\hline")
    table_lines.append("Configuration & Accuracy & ECE & AUROC & Avg. Confidence \\\\")
    table_lines.append("\\hline")
    
    config_order = ['No Verification', 'Tier 1 Only', 'Full Linear (a=0.5)', 'Bayesian']
    
    for config_name in config_order:
        if config_name in all_configs:
            metrics = all_configs[config_name]['metrics']
            formatted_name = config_name.replace('(a=0.5)', '($\\alpha$=0.5)')
            table_lines.append(
                f"{formatted_name} & "
                f"{metrics['accuracy']:.3f} & "
                f"{metrics['ece']:.3f} & "
                f"{metrics['auroc']:.3f} & "
                f"{metrics['avg_confidence']:.3f} \\\\"
            )
    
    table_lines.append("\\hline")
    table_lines.append("\\end{tabular}")
    table_lines.append("\\end{table}")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(table_lines))
    
    print(f"Saved LaTeX table: {output_path}")


def main():
    """Main function to generate all visualizations."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate publication-quality visualizations')
    parser.add_argument('results_file', type=str, help='Path to comparison results JSON')
    parser.add_argument('--output-dir', type=str, default='results/paper1/figures',
                       help='Output directory for figures')
    
    args = parser.parse_args()
    
    # Load results
    print(f"Loading results from: {args.results_file}")
    results = load_comparison_results(args.results_file)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract data for each configuration
    all_configs = {}
    for config_result in results['configurations']:
        config_name = config_result['config_name']
        all_configs[config_name] = extract_metrics(config_result)
    
    print(f"\nGenerating visualizations for {len(all_configs)} configurations...")
    
    # Generate individual plots
    plot_calibration_analysis(all_configs, output_dir / 'calibration_analysis.png')
    plot_roc_analysis(all_configs, output_dir / 'roc_analysis.png')
    plot_accuracy_comparison(all_configs, output_dir / 'accuracy_comparison.png')
    
    # Generate combined figure (publication-ready)
    plot_combined_figure(all_configs, output_dir / 'combined_analysis.png')
    
    # Generate LaTeX table
    generate_metrics_table(all_configs, output_dir / 'metrics_table.tex')
    
    print("\n" + "="*70)
    print("VISUALIZATION COMPLETE")
    print("="*70)
    print(f"\nGenerated files in: {output_dir}")
    print("  - calibration_analysis.png")
    print("  - roc_analysis.png")
    print("  - accuracy_comparison.png")
    print("  - combined_analysis.png (publication-ready)")
    print("  - metrics_table.tex (LaTeX)")
    print("\nAll figures are 300 DPI and ready for publication.")


if __name__ == "__main__":
    main()
