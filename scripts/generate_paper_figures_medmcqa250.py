"""
Generate Publication-Quality Figures for Qwen2.5-7B MedMCQA 250q Results
Creates 5 figures for results/paper1/figures/medmcqa250/ directory:
1. accuracy_comparison.png
2. calibration_analysis.png
3. roc_analysis.png
4. combined_analysis.png
5. calibration_grid_4configs.png
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import json
from pathlib import Path
from sklearn.metrics import roc_curve, auc

# Publication style
sns.set_style("ticks")
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 10

# ── Load results ──────────────────────────────────────────────────────────────
results_path = Path('results/4_config_comparison/4_config_qwen_250q_medmcqa_20260304_173609.json')
with open(results_path) as f:
    data = json.load(f)

configs_data = {k: data['configurations'][k] for k in ['config1','config2','config3','config4']}

config_names = [
    'Single\nSpecialist',
    'Single +\nTwo-Phase',
    'Multi +\nS-Score\n(No 2P)',
    'Multi +\nTwo-Phase +\nS-Score',
]
config_names_short = [
    'Single Specialist',
    'Single + Two-Phase',
    'Multi + S-Score (No 2P)',
    'Multi + Two-Phase + S-Score',
]
config_titles = [
    'Config 1:\nSingle Specialist',
    'Config 2:\nSingle + Two-Phase',
    'Config 3:\nMulti + S-Score (No 2P)',
    'Config 4:\nMulti + Two-Phase + S-Score',
]

accuracies = [configs_data[f'config{i}']['accuracy'] * 100 for i in range(1,5)]
eces       = [configs_data[f'config{i}']['ece']           for i in range(1,5)]
aurocs     = [configs_data[f'config{i}']['auroc']         for i in range(1,5)]

qwen_color = '#2E86AB'
x = np.arange(4)

output_dir = Path('results/paper1/figures/no_grid/medmcqa250')
output_dir.mkdir(parents=True, exist_ok=True)

# ── helpers ───────────────────────────────────────────────────────────────────
def compute_calibration_curve(results, n_bins=10):
    confidences = np.array([r['confidence'] for r in results])
    is_correct  = np.array([r['is_correct']  for r in results])
    edges = np.linspace(0, 1, n_bins + 1)
    centers, accs, counts = [], [], []
    for i in range(n_bins):
        lo, hi = edges[i], edges[i+1]
        mask = (confidences >= lo) & (confidences <= hi if i == n_bins-1 else confidences < hi)
        if mask.sum() > 0:
            centers.append((lo + hi) / 2)
            accs.append(is_correct[mask].mean())
            counts.append(mask.sum())
    return np.array(centers), np.array(accs), np.array(counts)

def compute_calibration_bins(results, bin_size=0.05):
    confidences = np.array([r['confidence'] for r in results])
    is_correct  = np.array([r['is_correct']  for r in results])
    edges = np.arange(0, 1 + bin_size, bin_size)
    centers, accs, counts = [], [], []
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i+1]
        mask = (confidences >= lo) & (confidences <= hi if i == len(edges)-2 else confidences < hi)
        centers.append((lo + hi) / 2)
        accs.append(is_correct[mask].mean() if mask.sum() > 0 else 0)
        counts.append(mask.sum())
    return np.array(centers), np.array(accs), np.array(counts)

# ── Figure 1: Accuracy ────────────────────────────────────────────────────────
print("Generating Figure 1: Accuracy Comparison...")
fig1, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(x, accuracies, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax.set_xlabel('Configuration', fontweight='bold')
ax.set_ylabel('Accuracy (%)', fontweight='bold')
ax.set_title('Accuracy Across System Configurations\n(Qwen2.5-7B, MedMCQA High-Disagreement n=250)',
             fontweight='bold', pad=15)
ax.set_xticks(x); ax.set_xticklabels(config_names)
ymin = max(0, min(accuracies) - 5)
ymax = max(accuracies) + 5
ax.set_ylim(ymin, ymax)
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., h + 0.3,
            f'{h:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
best_idx = accuracies.index(max(accuracies))
bars[best_idx].set_edgecolor('green'); bars[best_idx].set_linewidth(3)
plt.tight_layout()
fig1.savefig(output_dir / 'accuracy_comparison.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'accuracy_comparison.png'}")
plt.close(fig1)

# ── Figure 2: Calibration Analysis ───────────────────────────────────────────
print("Generating Figure 2: Calibration Analysis...")
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig2.suptitle('Calibration Analysis: Expected Calibration Error\n(Qwen2.5-7B, MedMCQA High-Disagreement n=250)',
              fontweight='bold', fontsize=13)

bars = ax1.bar(x, eces, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Configuration', fontweight='bold')
ax1.set_ylabel('Expected Calibration Error (ECE)', fontweight='bold')
ax1.set_title('ECE Across Configurations (Lower is Better)', fontweight='bold', pad=10)
ax1.set_xticks(x); ax1.set_xticklabels(config_names)
ax1.set_ylim(0, max(eces) * 1.25)
for bar in bars:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., h + 0.005,
             f'{h:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
best_ece_idx = eces.index(min(eces))
bars[best_ece_idx].set_edgecolor('green'); bars[best_ece_idx].set_linewidth(3)

ax2.plot([0,1],[0,1],'k--', linewidth=2, label='Perfect Calibration', alpha=0.5)
colors_cal = ['#888888','#5A9BD4','#F4A460', qwen_color]
markers_cal = ['o','^','D','s']
for i, ck in enumerate(['config1','config2','config3','config4']):
    centers, accs, _ = compute_calibration_curve(configs_data[ck]['results'])
    ax2.plot(centers, accs, marker=markers_cal[i], linestyle='-', color=colors_cal[i],
             linewidth=2.5, markersize=8, markeredgecolor='black', markeredgewidth=1,
             label=f'Config {i+1} (ECE={eces[i]:.3f})')
ax2.set_xlabel('Mean Predicted Confidence', fontweight='bold')
ax2.set_ylabel('Observed Accuracy', fontweight='bold')
ax2.set_title('Calibration Curves: All Configurations', fontweight='bold', pad=10)
ax2.legend(loc='upper left', fontsize=9)
ax2.set_xlim(0,1); ax2.set_ylim(0,1)

plt.tight_layout()
fig2.savefig(output_dir / 'calibration_analysis.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'calibration_analysis.png'}")
plt.close(fig2)

# ── Figure 3: ROC Analysis ────────────────────────────────────────────────────
print("Generating Figure 3: ROC Analysis...")
fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig3.suptitle('Discrimination Analysis: AUROC and ROC Curves\n(Qwen2.5-7B, MedMCQA High-Disagreement n=250)',
              fontweight='bold', fontsize=13)

bars = ax1.bar(x, aurocs, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Configuration', fontweight='bold')
ax1.set_ylabel('AUROC', fontweight='bold')
ax1.set_title('AUROC Across Configurations', fontweight='bold', pad=10)
ax1.set_xticks(x); ax1.set_xticklabels(config_names)
ax1.set_ylim(max(0.40, min(aurocs)-0.05), min(1.0, max(aurocs)+0.05))
for bar in bars:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., h + 0.003,
             f'{h:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
best_auroc_idx = aurocs.index(max(aurocs))
bars[best_auroc_idx].set_edgecolor('green'); bars[best_auroc_idx].set_linewidth(3)

colors  = ['#888888','#5A9BD4','#F4A460', qwen_color]
markers = ['o','^','D','s']
lstyles = ['--','-.',':', '-']
for i, (ck, cd) in enumerate(configs_data.items()):
    y_true   = np.array([r['is_correct']  for r in cd['results']])
    y_scores = np.array([r['confidence']  for r in cd['results']])
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    ax2.plot(fpr, tpr, linestyle=lstyles[i], linewidth=2.5,
             marker=markers[i], markersize=6, markevery=0.1,
             color=colors[i], markeredgecolor='black', markeredgewidth=0.8,
             label=f'{config_names_short[i]} (AUC={roc_auc:.3f})')
ax2.plot([0,1],[0,1],'k--', linewidth=1.5, alpha=0.4, label='Random')
ax2.set_xlabel('False Positive Rate', fontweight='bold')
ax2.set_ylabel('True Positive Rate', fontweight='bold')
ax2.set_title('ROC Curves: All Configurations', fontweight='bold', pad=10)
ax2.legend(loc='lower right', fontsize=9)
ax2.set_xlim(0,1); ax2.set_ylim(0,1)

plt.tight_layout()
fig3.savefig(output_dir / 'roc_analysis.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'roc_analysis.png'}")
plt.close(fig3)

# ── Figure 4: Combined 4-panel ────────────────────────────────────────────────
print("Generating Figure 4: Combined Analysis...")
fig4 = plt.figure(figsize=(14, 10))
gs = fig4.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
fig4.suptitle('Comprehensive System Analysis: Qwen2.5-7B on MedMCQA High-Disagreement (n=250)\n'
              'Ablation Study of Multi-Agent Reasoning and Two-Phase Verification',
              fontweight='bold', fontsize=14, y=0.98)

# Panel A: Accuracy
ax1 = fig4.add_subplot(gs[0,0])
bars = ax1.bar(x, accuracies, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Configuration', fontweight='bold')
ax1.set_ylabel('Accuracy (%)', fontweight='bold')
ax1.set_title('(A) Accuracy Across Configurations', fontweight='bold', pad=10, loc='left')
ax1.set_xticks(x); ax1.set_xticklabels(config_names, fontsize=8)
ax1.set_ylim(max(0, min(accuracies)-5), max(accuracies)+5)
for bar in bars:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., h + 0.3,
             f'{h:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
best_acc = accuracies.index(max(accuracies))
bars[best_acc].set_edgecolor('green'); bars[best_acc].set_linewidth(3)

# Panel B: ECE
ax2 = fig4.add_subplot(gs[0,1])
bars = ax2.bar(x, eces, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Configuration', fontweight='bold')
ax2.set_ylabel('Expected Calibration Error', fontweight='bold')
ax2.set_title('(B) Calibration Error (Lower is Better)', fontweight='bold', pad=10, loc='left')
ax2.set_xticks(x); ax2.set_xticklabels(config_names, fontsize=8)
ax2.set_ylim(0, max(eces) * 1.25)
for bar in bars:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., h + 0.005,
             f'{h:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
best_ece = eces.index(min(eces))
bars[best_ece].set_edgecolor('green'); bars[best_ece].set_linewidth(3)

# Panel C: AUROC
ax3 = fig4.add_subplot(gs[1,0])
bars = ax3.bar(x, aurocs, color=qwen_color, alpha=0.85, edgecolor='black', linewidth=1.5)
ax3.set_xlabel('Configuration', fontweight='bold')
ax3.set_ylabel('AUROC', fontweight='bold')
ax3.set_title('(C) Discrimination Across Configurations', fontweight='bold', pad=10, loc='left')
ax3.set_xticks(x); ax3.set_xticklabels(config_names, fontsize=8)
ax3.set_ylim(max(0.40, min(aurocs)-0.05), min(1.0, max(aurocs)+0.05))
for bar in bars:
    h = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., h + 0.003,
             f'{h:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
best_auroc = aurocs.index(max(aurocs))
bars[best_auroc].set_edgecolor('green'); bars[best_auroc].set_linewidth(3)

# Panel D: Improvement over baseline (Config 1 → 4)
ax4 = fig4.add_subplot(gs[1,1])
metrics_labels = ['Accuracy\n(pp)', 'ECE\n(% reduction)', 'AUROC\n(pp × 100)']
improvements = [
    accuracies[3] - accuracies[0],
    -((eces[3] - eces[0]) / eces[0] * 100),
    (aurocs[3] - aurocs[0]) * 100,
]
colors_imp = ['#2E86AB','#27AE60','#E67E22']
bars = ax4.bar(np.arange(3), improvements, color=colors_imp, alpha=0.85, edgecolor='black', linewidth=1.5)
ax4.set_xlabel('Metric', fontweight='bold')
ax4.set_ylabel('Improvement (Config 1 → Config 4)', fontweight='bold')
ax4.set_title('(D) System Improvement Over Baseline', fontweight='bold', pad=10, loc='left')
ax4.set_xticks(np.arange(3)); ax4.set_xticklabels(metrics_labels, fontsize=9)
ax4.axhline(y=0, color='black', linestyle='-', linewidth=1)
for bar in bars:
    h = bar.get_height()
    offset = 0.5 if h >= 0 else -0.5
    va = 'bottom' if h >= 0 else 'top'
    ax4.text(bar.get_x() + bar.get_width()/2., h + offset,
             f'{h:.1f}', ha='center', va=va, fontsize=9, fontweight='bold')

plt.tight_layout()
fig4.savefig(output_dir / 'combined_analysis.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'combined_analysis.png'}")
plt.close(fig4)

# ── Figure 5: Calibration Grid (4-column style) ───────────────────────────────
print("Generating Figure 5: Calibration Grid...")
plt.rcParams['font.size'] = 9

fig5 = plt.figure(figsize=(20, 8.5))
gs5 = fig5.add_gridspec(2, 4, height_ratios=[1,1], hspace=0.35, wspace=0.25,
                         top=0.95, bottom=0.15, left=0.05, right=0.98)

for col_idx, (ck, ctitle) in enumerate(zip(
        ['config1','config2','config3','config4'], config_titles)):
    config  = configs_data[ck]
    results = config['results']
    confs   = np.array([r['confidence'] for r in results])
    correct = np.array([r['is_correct']  for r in results])
    acc, ece_v, auroc_v = config['accuracy'], config['ece'], config['auroc']

    ax_hist = fig5.add_subplot(gs5[0, col_idx])
    ax_cal  = fig5.add_subplot(gs5[1, col_idx])

    # Top: stacked confidence histogram
    bins = np.linspace(50, 100, 11)
    conf_corr = confs[correct]  * 100
    conf_incr = confs[~correct] * 100
    ax_hist.hist([conf_incr, conf_corr], bins=bins,
                 color=['#E74C3C','#3498DB'], alpha=0.8,
                 label=['wrong','correct'], edgecolor='black', linewidth=0.5, stacked=True)
    ax_hist.set_title(f'{ctitle}\nACC {acc:.2f} / AUROC {auroc_v:.2f} / ECE {ece_v:.2f}',
                      fontweight='bold', fontsize=9, pad=10)
    if col_idx == 0:
        ax_hist.set_ylabel('Count', fontweight='bold')
    ax_hist.set_xlabel('Confidence (%)', fontweight='bold')
    ax_hist.set_xlim(50, 100)
    ax_hist.set_ylim(0, len(results) * 0.5)
    ax_hist.legend(loc='upper left', fontsize=7)
    ax_hist.grid(False)

    # Bottom: calibration bar chart
    bcenters, baccs, _ = compute_calibration_bins(results, bin_size=0.05)
    ax_cal.bar(bcenters * 100, baccs, width=4.5,
               color='#3498DB', alpha=0.7, edgecolor='black', linewidth=0.5)
    ax_cal.plot([0,100],[0,1],'k--', linewidth=1.5, alpha=0.5, label='Perfect calibration')
    ax_cal.set_xlabel('Confidence (%)', fontweight='bold')
    if col_idx == 0:
        ax_cal.set_ylabel('Accuracy within bin', fontweight='bold')
        ax_cal.legend(loc='upper left', fontsize=8)
    ax_cal.set_xlim(0, 100); ax_cal.set_ylim(0, 1)
    ax_cal.set_xticks([0,20,40,60,80,100])
    ax_cal.grid(False)

caption = ('Figure: Calibration Analysis of Qwen2.5-7B on MedMCQA High-Disagreement (n=250). '
           'Top row shows confidence distribution for correct (blue) and incorrect (red) predictions. '
           'Bottom row shows calibration histograms with 5% bins, where bar height represents observed accuracy '
           'and the diagonal line represents perfect calibration.')
fig5.text(0.05, 0.03, caption, ha='left', va='bottom', fontsize=10, transform=fig5.transFigure)
fig5.savefig(output_dir / 'calibration_grid_4configs.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'calibration_grid_4configs.png'}")
plt.close(fig5)

# ── LaTeX table ───────────────────────────────────────────────────────────────
print("Generating LaTeX metrics table...")
avg_confs = [np.mean([r['confidence'] for r in configs_data[f'config{i}']['results']]) for i in range(1,5)]

latex_table = r"""\begin{table}[h]
\centering
\caption{Performance Comparison: Qwen2.5-7B on MedMCQA High-Disagreement (250 Questions)}
\label{tab:medmcqa250_results}
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

# ── Analysis Summary ──────────────────────────────────────────────────────────
print("\n" + "="*80)
print("QWEN2.5-7B  —  MedMCQA HIGH-DISAGREEMENT 250Q  —  ABLATION RESULTS")
print("="*80)
print(f"\n{'Configuration':<38} {'Accuracy':>10} {'ECE':>8} {'AUROC':>8} {'AvgConf':>9}")
print("-"*75)
for i, name in enumerate(config_names_short):
    print(f"{name:<38} {accuracies[i]:>9.1f}% {eces[i]:>8.3f} {aurocs[i]:>8.3f} {avg_confs[i]:>9.3f}")

print("\n" + "-"*80)
print("ABLATION INSIGHTS:")
print("-"*80)

deltas = {
    '2P on Single (C1->C2)':    (1, 0),
    'Multi-Agent  (C1->C3)':    (2, 0),
    'Full System  (C1->C4)':    (3, 0),
    '2P on Multi  (C3->C4)':    (3, 2),
}
for label, (new_i, base_i) in deltas.items():
    da = accuracies[new_i] - accuracies[base_i]
    de = eces[new_i]       - eces[base_i]
    dr = aurocs[new_i]     - aurocs[base_i]
    pct_ece = de / eces[base_i] * 100
    print(f"\n  {label}:")
    print(f"    Accuracy: {da:+.1f} pp   ECE: {de:+.3f} ({pct_ece:+.1f}%)   AUROC: {dr:+.3f}")

print("\n" + "="*80)
print("KEY FINDINGS:")
print("="*80)
print(f"  Best Accuracy : Config {accuracies.index(max(accuracies))+1}  -> {max(accuracies):.1f}%")
print(f"  Best ECE      : Config {eces.index(min(eces))+1}  -> {min(eces):.3f}")
print(f"  Best AUROC    : Config {aurocs.index(max(aurocs))+1}  -> {max(aurocs):.3f}")
ece_reduction = (eces[0] - eces[3]) / eces[0] * 100
print(f"\n  Full system ECE reduction : {ece_reduction:.1f}% (C1->C4)")
print(f"  Full system acc gain      : {accuracies[3]-accuracies[0]:+.1f} pp (C1->C4)")
print(f"  Full system AUROC gain    : {aurocs[3]-aurocs[0]:+.3f} (C1->C4)")
print("="*80)
print(f"\nAll figures saved to: {output_dir}/")
print("  accuracy_comparison.png | calibration_analysis.png | roc_analysis.png")
print("  combined_analysis.png   | calibration_grid_4configs.png | metrics_table.tex")
