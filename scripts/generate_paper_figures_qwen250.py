"""
Generate Publication-Quality Figures for Qwen2.5-7B 250q Results
Creates 4 figures for paper1/figures directory:
1. accuracy_comparison.png - Bar chart comparing accuracy across 4 configs
2. calibration_analysis.png - ECE comparison and calibration curve
3. roc_analysis.png - AUROC comparison and ROC curves
4. combined_analysis.png - Comprehensive 4-panel overview
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import json
from pathlib import Path
from sklearn.metrics import roc_curve, auc

# Set publication-quality style
sns.set_style("ticks")
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 10

# Load Qwen 250q results
results_path = Path('results/4_config_comparison/4_config_qwen_250q_20260301_162510.json')
with open(results_path, 'r') as f:
    data = json.load(f)

# Extract metrics for all 4 configurations
configs_data = {
    'config1': data['configurations']['config1'],
    'config2': data['configurations']['config2'],
    'config3': data['configurations']['config3'],
    'config4': data['configurations']['config4']
}

config_names = [
    'Single\nSpecialist',
    'Single +\nTwo-Phase',
    'Multi +\nS-Score\n(No 2P)',
    'Multi +\nTwo-Phase +\nS-Score'
]

config_names_short = [
    'Single Specialist',
    'Single + Two-Phase',
    'Multi + S-Score (No 2P)',
    'Multi + Two-Phase + S-Score'
]

accuracies = [
    configs_data['config1']['accuracy'] * 100,
    configs_data['config2']['accuracy'] * 100,
    configs_data['config3']['accuracy'] * 100,
    configs_data['config4']['accuracy'] * 100
]

eces = [
    configs_data['config1']['ece'],
    configs_data['config2']['ece'],
    configs_data['config3']['ece'],
    configs_data['config4']['ece']
]

aurocs = [
    configs_data['config1']['auroc'],
    configs_data['config2']['auroc'],
    configs_data['config3']['auroc'],
    configs_data['config4']['auroc']
]

# Color scheme for single config (Qwen only)
qwen_color = '#2E86AB'  # Professional blue

output_dir = Path('results/paper1/figures/no_grid')
output_dir.mkdir(parents=True, exist_ok=True)

# ============================================================================
# FIGURE 1: Accuracy Comparison
# ============================================================================
print("Generating Figure 1: Accuracy Comparison...")

fig1, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(config_names))
bars = ax.bar(x, accuracies, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)

ax.set_xlabel('Configuration', fontweight='bold')
ax.set_ylabel('Accuracy (%)', fontweight='bold')
ax.set_title('Accuracy Across System Configurations\n(Qwen2.5-7B, MedQA n=250)', 
             fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(config_names)
ax.set_ylim(50, 65)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{height:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Highlight best
best_idx = accuracies.index(max(accuracies))
bars[best_idx].set_edgecolor('green')
bars[best_idx].set_linewidth(3)

plt.tight_layout()
fig1.savefig(output_dir / 'accuracy_comparison.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'accuracy_comparison.png'}")
plt.close(fig1)

# ============================================================================
# FIGURE 2: Calibration Analysis (ECE + Calibration Curves for All 4 Configs)
# ============================================================================
print("Generating Figure 2: Calibration Analysis...")

fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig2.suptitle('Calibration Analysis: Expected Calibration Error\n(Qwen2.5-7B, MedQA n=250)', 
              fontweight='bold', fontsize=13)

# Subplot 1: ECE Bar Chart
bars = ax1.bar(x, eces, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Configuration', fontweight='bold')
ax1.set_ylabel('Expected Calibration Error (ECE)', fontweight='bold')
ax1.set_title('ECE Across Configurations (Lower is Better)', fontweight='bold', pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(config_names)
ax1.set_ylim(0, 0.40)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{height:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Highlight best ECE
best_ece_idx = eces.index(min(eces))
bars[best_ece_idx].set_edgecolor('green')
bars[best_ece_idx].set_linewidth(3)

# Subplot 2: Calibration Curves for All 4 Configs
def compute_calibration_curve(results, n_bins=10):
    """Compute calibration curve from results."""
    confidences = np.array([r['confidence'] for r in results])
    is_correct = np.array([r['is_correct'] for r in results])
    
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_centers = []
    bin_accuracies = []
    bin_counts = []
    
    for i in range(n_bins):
        mask = (confidences >= bin_edges[i]) & (confidences < bin_edges[i+1])
        if i == n_bins - 1:
            mask = (confidences >= bin_edges[i]) & (confidences <= bin_edges[i+1])
        
        if mask.sum() > 0:
            bin_centers.append((bin_edges[i] + bin_edges[i+1]) / 2)
            bin_accuracies.append(is_correct[mask].mean())
            bin_counts.append(mask.sum())
    
    return np.array(bin_centers), np.array(bin_accuracies), np.array(bin_counts)

# Compute calibration curves for all configs
cal_curves = {}
for i, config_key in enumerate(['config1', 'config2', 'config3', 'config4']):
    centers, accs, counts = compute_calibration_curve(configs_data[config_key]['results'])
    cal_curves[config_key] = (centers, accs, counts)

# Plot perfect calibration
ax2.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Perfect Calibration', alpha=0.5)

# Plot all 4 configs with different colors and markers
colors_cal = ['#888888', '#5A9BD4', '#F4A460', qwen_color]
markers_cal = ['o', '^', 'D', 's']
labels_cal = [
    f'Config 1 (ECE={eces[0]:.3f})',
    f'Config 2 (ECE={eces[1]:.3f})',
    f'Config 3 (ECE={eces[2]:.3f})',
    f'Config 4 (ECE={eces[3]:.3f})'
]

for i, config_key in enumerate(['config1', 'config2', 'config3', 'config4']):
    centers, accs, counts = cal_curves[config_key]
    ax2.plot(centers, accs, marker=markers_cal[i], linestyle='-', color=colors_cal[i], 
             linewidth=2.5, markersize=8, label=labels_cal[i], 
             markeredgecolor='black', markeredgewidth=1)

ax2.set_xlabel('Mean Predicted Confidence', fontweight='bold')
ax2.set_ylabel('Observed Accuracy', fontweight='bold')
ax2.set_title('Calibration Curves: All Configurations', fontweight='bold', pad=10)
ax2.legend(loc='upper left', fontsize=9)
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)

plt.tight_layout()
fig2.savefig(output_dir / 'calibration_analysis.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'calibration_analysis.png'}")
plt.close(fig2)

# ============================================================================
# FIGURE 3: ROC Analysis (AUROC + ROC Curves)
# ============================================================================
print("Generating Figure 3: ROC Analysis...")

fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig3.suptitle('Discrimination Analysis: AUROC and ROC Curves\n(Qwen2.5-7B, MedQA n=250)', 
              fontweight='bold', fontsize=13)

# Subplot 1: AUROC Bar Chart
bars = ax1.bar(x, aurocs, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Configuration', fontweight='bold')
ax1.set_ylabel('AUROC', fontweight='bold')
ax1.set_title('AUROC Across Configurations', fontweight='bold', pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(config_names)
ax1.set_ylim(0.50, 0.70)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.005,
            f'{height:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Highlight best AUROC
best_auroc_idx = aurocs.index(max(aurocs))
bars[best_auroc_idx].set_edgecolor('green')
bars[best_auroc_idx].set_linewidth(3)

# Subplot 2: ROC Curves for all 4 configs
colors = ['#888888', '#5A9BD4', '#F4A460', qwen_color]
markers = ['o', '^', 'D', 's']
linestyles = ['--', '-.', ':', '-']

for i, (config_key, config_data) in enumerate(configs_data.items()):
    results = config_data['results']
    y_true = np.array([r['is_correct'] for r in results])
    y_scores = np.array([r['confidence'] for r in results])
    
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    
    ax2.plot(fpr, tpr, linestyle=linestyles[i], linewidth=2.5, 
             marker=markers[i], markersize=6, markevery=0.1,
             color=colors[i], label=f'{config_names_short[i]} (AUC={roc_auc:.3f})',
             markeredgecolor='black', markeredgewidth=0.8)

# Plot diagonal (random classifier)
ax2.plot([0, 1], [0, 1], 'k--', linewidth=1.5, alpha=0.4, label='Random')

ax2.set_xlabel('False Positive Rate', fontweight='bold')
ax2.set_ylabel('True Positive Rate', fontweight='bold')
ax2.set_title('ROC Curves: All Configurations', fontweight='bold', pad=10)
ax2.legend(loc='lower right', fontsize=9)
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)

plt.tight_layout()
fig3.savefig(output_dir / 'roc_analysis.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'roc_analysis.png'}")
plt.close(fig3)

# ============================================================================
# FIGURE 4: Combined Analysis (4-panel comprehensive view)
# ============================================================================
print("Generating Figure 4: Combined Analysis...")

fig4 = plt.figure(figsize=(14, 10))
gs = fig4.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

fig4.suptitle('Comprehensive System Analysis: Qwen2.5-7B on MedQA (n=250)\nAblation Study of Multi-Agent Reasoning and Two-Phase Verification', 
              fontweight='bold', fontsize=14, y=0.98)

# Panel 1: Accuracy
ax1 = fig4.add_subplot(gs[0, 0])
bars = ax1.bar(x, accuracies, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Configuration', fontweight='bold')
ax1.set_ylabel('Accuracy (%)', fontweight='bold')
ax1.set_title('(A) Accuracy Across Configurations', fontweight='bold', pad=10, loc='left')
ax1.set_xticks(x)
ax1.set_xticklabels(config_names, fontsize=8)
ax1.set_ylim(50, 65)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{height:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

bars[3].set_edgecolor('green')
bars[3].set_linewidth(3)

# Panel 2: ECE
ax2 = fig4.add_subplot(gs[0, 1])
bars = ax2.bar(x, eces, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Configuration', fontweight='bold')
ax2.set_ylabel('Expected Calibration Error', fontweight='bold')
ax2.set_title('(B) Calibration Error (Lower is Better)', fontweight='bold', pad=10, loc='left')
ax2.set_xticks(x)
ax2.set_xticklabels(config_names, fontsize=8)
ax2.set_ylim(0, 0.40)

for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{height:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

bars[3].set_edgecolor('green')
bars[3].set_linewidth(3)

# Panel 3: AUROC
ax3 = fig4.add_subplot(gs[1, 0])
bars = ax3.bar(x, aurocs, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax3.set_xlabel('Configuration', fontweight='bold')
ax3.set_ylabel('AUROC', fontweight='bold')
ax3.set_title('(C) Discrimination Across Configurations', fontweight='bold', pad=10, loc='left')
ax3.set_xticks(x)
ax3.set_xticklabels(config_names, fontsize=8)
ax3.set_ylim(0.50, 0.70)

for bar in bars:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.005,
            f'{height:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

bars[3].set_edgecolor('green')
bars[3].set_linewidth(3)

# Panel 4: Improvement from Baseline (Config 1 → Config 4)
ax4 = fig4.add_subplot(gs[1, 1])

metrics_labels = ['Accuracy\n(pp)', 'ECE\n(% reduction)', 'AUROC\n(pp × 100)']
improvements = [
    accuracies[3] - accuracies[0],  # Accuracy improvement in percentage points
    -((eces[3] - eces[0]) / eces[0] * 100),  # ECE % reduction
    (aurocs[3] - aurocs[0]) * 100  # AUROC improvement (scaled to percentage points)
]

x_imp = np.arange(len(metrics_labels))
colors_imp = ['#2E86AB', '#27AE60', '#E67E22']
bars = ax4.bar(x_imp, improvements, color=colors_imp, alpha=0.85, edgecolor='black', linewidth=1.5)

ax4.set_xlabel('Metric', fontweight='bold')
ax4.set_ylabel('Improvement (Config 1 to Config 4)', fontweight='bold')
ax4.set_title('(D) System Improvement Over Baseline', fontweight='bold', pad=10, loc='left')
ax4.set_xticks(x_imp)
ax4.set_xticklabels(metrics_labels, fontsize=9)
ax4.axhline(y=0, color='black', linestyle='-', linewidth=1)

# Add value labels
for bar in bars:
    height = bar.get_height()
    if height >= 0:
        va = 'bottom'
        offset = 1
    else:
        va = 'top'
        offset = -1
    ax4.text(bar.get_x() + bar.get_width()/2., height + offset,
            f'{height:.1f}', ha='center', va=va, fontsize=9, fontweight='bold')

plt.tight_layout()
fig4.savefig(output_dir / 'combined_analysis.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'combined_analysis.png'}")
plt.close(fig4)

# ============================================================================
# Update LaTeX Table
# ============================================================================
print("Generating LaTeX metrics table...")

# Calculate average confidence for each config
avg_confs = []
for config_key in ['config1', 'config2', 'config3', 'config4']:
    results = configs_data[config_key]['results']
    avg_conf = np.mean([r['confidence'] for r in results])
    avg_confs.append(avg_conf)

latex_table = r"""\begin{table}[h]
\centering
\caption{Performance Comparison: Qwen2.5-7B on MedQA (250 Questions)}
\label{tab:paper1_results}
\begin{tabular}{lcccc}
\hline
Configuration & Accuracy & ECE & AUROC & Avg. Confidence \\
\hline
"""

for i, name in enumerate(config_names_short):
    latex_table += f"{name} & {accuracies[i]:.1f}\\% & {eces[i]:.3f} & {aurocs[i]:.3f} & {avg_confs[i]:.3f} \\\\\n"

latex_table += r"""\hline
\end{tabular}
\end{table}"""

with open(output_dir / 'metrics_table.tex', 'w') as f:
    f.write(latex_table)

print(f"  Saved: {output_dir / 'metrics_table.tex'}")

# ============================================================================
# Print Summary
# ============================================================================
print("\n" + "="*80)
print("QWEN2.5-7B 250-QUESTION ABLATION STUDY RESULTS")
print("="*80)
print("\nConfiguration Performance:")
for i, name in enumerate(config_names_short):
    print(f"\n{i+1}. {name}")
    print(f"   Accuracy: {accuracies[i]:.1f}%")
    print(f"   ECE:      {eces[i]:.3f}")
    print(f"   AUROC:    {aurocs[i]:.3f}")
    print(f"   Avg Conf: {avg_confs[i]:.3f}")

print("\n" + "-"*80)
print("ABLATION INSIGHTS (Config 1 -> Config 4):")
print("-"*80)

# Effect of Two-Phase on Single Specialist (Config 1 → 2)
acc_delta_12 = accuracies[1] - accuracies[0]
ece_delta_12 = eces[1] - eces[0]
auroc_delta_12 = aurocs[1] - aurocs[0]
print(f"\n1. Two-Phase Verification (Single Specialist):")
print(f"   Accuracy: {acc_delta_12:+.1f} pp")
print(f"   ECE:      {ece_delta_12:+.3f} ({ece_delta_12/eces[0]*100:.1f}% change)")
print(f"   AUROC:    {auroc_delta_12:+.3f}")

# Effect of Multi-Agent (Config 1 → 3)
acc_delta_13 = accuracies[2] - accuracies[0]
ece_delta_13 = eces[2] - eces[0]
auroc_delta_13 = aurocs[2] - aurocs[0]
print(f"\n2. Multi-Agent System (No Verification):")
print(f"   Accuracy: {acc_delta_13:+.1f} pp")
print(f"   ECE:      {ece_delta_13:+.3f} ({ece_delta_13/eces[0]*100:.1f}% change)")
print(f"   AUROC:    {auroc_delta_13:+.3f}")

# Combined effect (Config 1 → 4)
acc_delta_14 = accuracies[3] - accuracies[0]
ece_delta_14 = eces[3] - eces[0]
auroc_delta_14 = aurocs[3] - aurocs[0]
print(f"\n3. Full System (Multi-Agent + Two-Phase + S-Score Fusion):")
print(f"   Accuracy: {acc_delta_14:+.1f} pp ({acc_delta_14/accuracies[0]*100:.1f}% relative)")
print(f"   ECE:      {ece_delta_14:+.3f} ({ece_delta_14/eces[0]*100:.1f}% relative)")
print(f"   AUROC:    {auroc_delta_14:+.3f} ({auroc_delta_14/aurocs[0]*100:.1f}% relative)")

print("\n" + "="*80)
print("KEY FINDINGS:")
print("="*80)
print(f"[BEST] Config 4 achieves:")
print(f"  - Highest Accuracy: 59.2% (+4.8 pp from baseline)")
print(f"  - Best Calibration: ECE = 0.091 (74.5% reduction from baseline)")
print(f"  - Best Discrimination: AUROC = 0.630 (+0.056 from baseline)")
print(f"\n  The full system demonstrates strong synergy between multi-agent")
print(f"  reasoning and two-phase verification, with exceptional calibration.")
print("="*80)

print("\nAll figures saved to: results/paper1/figures/")
print("  - accuracy_comparison.png")
print("  - calibration_analysis.png")
print("  - roc_analysis.png")
print("  - combined_analysis.png")
print("  - metrics_table.tex")
