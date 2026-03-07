"""
Generate combined cross-dataset figures for paper submission.
Four datasets: MedQA-100, MedQA-250, MedMCQA-100, MedMCQA-250
Three combined figures:
  1. combined_accuracy_ece_auroc.png  - 3-row x 4-col: Acc / ECE / AUROC bars per dataset
  2. combined_calibration_curves.png  - 2x2 reliability diagrams (one per dataset)
  3. combined_roc_curves.png          - 2x2 ROC curves (one per dataset)
  4. combined_calibration_grid.png    - 4x4 grid: datasets (cols) x configs (rows), calibration histograms
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import json
from pathlib import Path
from sklearn.metrics import roc_curve, auc
import seaborn as sns

sns.set_style("ticks")
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['axes.titlesize'] = 9
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 8

output_dir = Path('results/paper1/figures/no_grid/combined')
output_dir.mkdir(parents=True, exist_ok=True)

# ── Load results ──────────────────────────────────────────────────────────────
RESULT_FILES = {
    'MedQA-100':    'results/4_config_comparison/4_config_qwen_100q_20260228_000721.json',
    'MedQA-250':    'results/4_config_comparison/4_config_qwen_250q_20260301_162510.json',
    'MedMCQA-100':  'results/4_config_comparison/4_config_qwen_100q_medmcqa_20260303_175634.json',
    'MedMCQA-250':  'results/4_config_comparison/4_config_qwen_250q_medmcqa_20260304_173609.json',
}

datasets = {}
for label, path in RESULT_FILES.items():
    d = json.load(open(path, encoding='utf-8'))
    datasets[label] = {k: d['configurations'][k] for k in ['config1','config2','config3','config4']}

DATASET_LABELS = list(datasets.keys())
CONFIG_KEYS    = ['config1','config2','config3','config4']
CONFIG_SHORT   = ['C1: Single\nSpec', 'C2: Single\n+2P', 'C3: Multi\n+S-Score', 'C4: Full\nSystem']
CONFIG_COLORS  = ['#888888', '#5A9BD4', '#F4A460', '#2E86AB']

def get_metric(ds, ck, metric):
    v = datasets[ds][ck][metric]
    return v * 100 if metric == 'accuracy' else v

def compute_calibration_curve(results, n_bins=10):
    confs = np.array([r['confidence'] for r in results])
    corr  = np.array([r['is_correct']  for r in results])
    edges = np.linspace(0, 1, n_bins + 1)
    centers, accs = [], []
    for i in range(n_bins):
        lo, hi = edges[i], edges[i+1]
        mask = (confs >= lo) & (confs <= hi if i == n_bins-1 else confs < hi)
        if mask.sum() > 0:
            centers.append((lo+hi)/2)
            accs.append(corr[mask].mean())
    return np.array(centers), np.array(accs)

def compute_calibration_bins(results, bin_size=0.05):
    confs = np.array([r['confidence'] for r in results])
    corr  = np.array([r['is_correct']  for r in results])
    edges = np.arange(0, 1 + bin_size, bin_size)
    centers, accs, counts = [], [], []
    for i in range(len(edges)-1):
        lo, hi = edges[i], edges[i+1]
        mask = (confs >= lo) & (confs <= hi if i == len(edges)-2 else confs < hi)
        centers.append((lo+hi)/2)
        accs.append(corr[mask].mean() if mask.sum() > 0 else 0)
        counts.append(mask.sum())
    return np.array(centers), np.array(accs), np.array(counts)

# ── Print all numbers ─────────────────────────────────────────────────────────
print("="*80)
print("ALL DATASET RESULTS SUMMARY")
print("="*80)
METRICS = [('accuracy','Acc','%'), ('ece','ECE',''), ('auroc','AUROC','')]
for ds in DATASET_LABELS:
    print(f"\n{ds}:")
    print(f"  {'Config':<10} {'Acc':>8} {'ECE':>8} {'AUROC':>8} {'AvgConf':>9}")
    print(f"  {'-'*48}")
    for i, ck in enumerate(CONFIG_KEYS):
        c = datasets[ds][ck]
        results = c['results']
        avg_conf = np.mean([r['confidence'] for r in results])
        print(f"  C{i+1:<9} {c['accuracy']*100:>7.1f}% {c['ece']:>8.3f} {c['auroc']:>8.3f} {avg_conf:>9.3f}")
    # Deltas vs C1
    c1 = datasets[ds]['config1']
    c4 = datasets[ds]['config4']
    print(f"  C1->C4: Acc {(c4['accuracy']-c1['accuracy'])*100:+.1f}pp  "
          f"ECE {c4['ece']-c1['ece']:+.3f} ({(c4['ece']-c1['ece'])/c1['ece']*100:+.1f}%)  "
          f"AUROC {c4['auroc']-c1['auroc']:+.3f}")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Combined Accuracy / ECE / AUROC bars — 3 rows x 4 cols
# ═════════════════════════════════════════════════════════════════════════════
print("\nGenerating Figure 1: Combined Accuracy/ECE/AUROC bars...")

fig1, axes = plt.subplots(3, 4, figsize=(14, 9))
fig1.suptitle('Ablation Results Across All Datasets and Configurations\n(Qwen2.5-7B-Instruct, High-Disagreement Subsets)',
              fontweight='bold', fontsize=11, y=0.98)

row_labels = ['Accuracy (%)', 'ECE (lower is better)', 'AUROC (higher is better)']
metric_keys = ['accuracy', 'ece', 'auroc']

for col_idx, ds in enumerate(DATASET_LABELS):
    for row_idx, (metric, row_label) in enumerate(zip(metric_keys, row_labels)):
        ax = axes[row_idx, col_idx]
        vals = [get_metric(ds, ck, metric) for ck in CONFIG_KEYS]

        # Highlight best bar
        best_idx = vals.index(min(vals) if metric == 'ece' else max(vals))
        edge_colors = ['black'] * 4
        edge_widths = [1.0] * 4
        edge_colors[best_idx] = '#27AE60'
        edge_widths[best_idx] = 2.5

        bars = ax.bar(range(4), vals, color=CONFIG_COLORS, alpha=0.85,
                      edgecolor=edge_colors, linewidth=edge_widths)

        # Value labels on bars
        for bi, (bar, v) in enumerate(zip(bars, vals)):
            h = bar.get_height()
            fmt = f'{v:.1f}' if metric == 'accuracy' else f'{v:.3f}'
            ax.text(bar.get_x() + bar.get_width()/2., h + (0.3 if metric=='accuracy' else 0.003),
                    fmt, ha='center', va='bottom', fontsize=7, fontweight='bold')

        ax.set_xticks(range(4))
        ax.set_xticklabels(['C1','C2','C3','C4'], fontsize=8)

        if col_idx == 0:
            ax.set_ylabel(row_label, fontweight='bold', fontsize=8)
        if row_idx == 0:
            ax.set_title(ds, fontweight='bold', fontsize=9, pad=8)

        # Y-axis range
        if metric == 'accuracy':
            ymin = max(0, min(vals) - 8)
            ymax = max(vals) + 8
        elif metric == 'ece':
            ymin, ymax = 0, max(vals) * 1.3
        else:
            ymin = max(0.35, min(vals) - 0.05)
            ymax = min(1.0, max(vals) + 0.05)
        ax.set_ylim(ymin, ymax)

# Add config legend at bottom
from matplotlib.patches import Patch
legend_els = [Patch(facecolor=c, label=l, edgecolor='black', linewidth=0.8)
              for c, l in zip(CONFIG_COLORS, ['C1: Single Specialist','C2: Single+Two-Phase',
                                               'C3: Multi+S-Score (No 2P)','C4: Full System'])]
fig1.legend(handles=legend_els, loc='lower center', ncol=4, fontsize=8,
            bbox_to_anchor=(0.5, 0.01), frameon=True)

plt.tight_layout(rect=[0, 0.06, 1, 0.97])
fig1.savefig(output_dir / 'combined_accuracy_ece_auroc.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'combined_accuracy_ece_auroc.png'}")
plt.close(fig1)

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 2: Combined Calibration Curves — 2x2 (one per dataset)
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 2: Combined Calibration Curves...")

fig2, axes = plt.subplots(2, 2, figsize=(10, 8))
fig2.suptitle('Calibration Reliability Diagrams Across All Datasets\n(Diagonal = perfect calibration)',
              fontweight='bold', fontsize=11)

CAL_COLORS  = ['#888888','#5A9BD4','#F4A460','#2E86AB']
CAL_MARKERS = ['o','^','D','s']
CAL_LINES   = ['--','-.',':', '-']

for idx, ds in enumerate(DATASET_LABELS):
    ax = axes[idx//2, idx%2]
    ax.plot([0,1],[0,1],'k--', linewidth=1.5, alpha=0.5, label='Perfect calibration', zorder=1)

    for i, ck in enumerate(CONFIG_KEYS):
        results = datasets[ds][ck]['results']
        ece_v   = datasets[ds][ck]['ece']
        centers, accs = compute_calibration_curve(results)
        ax.plot(centers, accs, marker=CAL_MARKERS[i], linestyle=CAL_LINES[i],
                color=CAL_COLORS[i], linewidth=2, markersize=6,
                markeredgecolor='black', markeredgewidth=0.7,
                label=f'C{i+1} (ECE={ece_v:.3f})', zorder=2+i)

    ax.set_title(ds, fontweight='bold', fontsize=10)
    ax.set_xlabel('Mean Predicted Confidence', fontweight='bold')
    ax.set_ylabel('Observed Accuracy', fontweight='bold')
    ax.legend(loc='upper left', fontsize=7.5, framealpha=0.9)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_aspect('equal')

plt.tight_layout()
fig2.savefig(output_dir / 'combined_calibration_curves.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'combined_calibration_curves.png'}")
plt.close(fig2)

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 3: Combined ROC Curves — 2x2 (one per dataset)
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 3: Combined ROC Curves...")

fig3, axes = plt.subplots(2, 2, figsize=(10, 8))
fig3.suptitle('ROC Curves for Correct/Incorrect Discrimination Across All Datasets',
              fontweight='bold', fontsize=11)

for idx, ds in enumerate(DATASET_LABELS):
    ax = axes[idx//2, idx%2]
    ax.plot([0,1],[0,1],'k--', linewidth=1.2, alpha=0.4, label='Random (AUC=0.500)')

    for i, ck in enumerate(CONFIG_KEYS):
        results  = datasets[ds][ck]['results']
        y_true   = np.array([r['is_correct']  for r in results])
        y_scores = np.array([r['confidence']  for r in results])
        fpr, tpr, _ = roc_curve(y_true, y_scores)
        roc_auc  = auc(fpr, tpr)
        ax.plot(fpr, tpr, linestyle=CAL_LINES[i], linewidth=2,
                marker=CAL_MARKERS[i], markersize=5, markevery=0.12,
                color=CAL_COLORS[i], markeredgecolor='black', markeredgewidth=0.6,
                label=f'C{i+1} (AUC={roc_auc:.3f})')

    ax.set_title(ds, fontweight='bold', fontsize=10)
    ax.set_xlabel('False Positive Rate', fontweight='bold')
    ax.set_ylabel('True Positive Rate', fontweight='bold')
    ax.legend(loc='lower right', fontsize=7.5, framealpha=0.9)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_aspect('equal')

plt.tight_layout()
fig3.savefig(output_dir / 'combined_roc_curves.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'combined_roc_curves.png'}")
plt.close(fig3)

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Combined Calibration Grid
#   Layout: 4 datasets stacked vertically (each as a 2-row block)
#           4 configs as columns
#   Row pair per dataset:
#     - Top sub-row: frequency histogram (stacked wrong=red / correct=blue)
#     - Bottom sub-row: calibration bar (accuracy per confidence bin) + diagonal
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 4: Combined Calibration Grid (original layout, all 4 datasets)...")

CONFIG_FULL_LABELS = [
    'Config 1:\nSingle Specialist',
    'Config 2:\nSingle + Two-Phase',
    'Config 3:\nMulti + S-Score (No 2P)',
    'Config 4:\nMulti + Two-Phase\n+ S-Score',
]

WRONG_COLOR   = '#E74C3C'   # red  = wrong answer
CORRECT_COLOR = '#5B9BD5'   # blue = correct answer
CAL_COLOR     = '#5B9BD5'

N_DS   = len(DATASET_LABELS)  # 4
N_COLS = 4

# Row layout: hist + cal + spacer for each dataset (no spacer after last)
row_heights = []
for i in range(N_DS):
    row_heights.append(1.15)   # histogram
    row_heights.append(0.95)   # calibration
    if i < N_DS - 1:
        row_heights.append(0.20)  # spacer between dataset groups

n_total_rows = len(row_heights)  # 4*2 + 3 = 11

fig4 = plt.figure(figsize=(18, N_DS * 5.0))
fig4.suptitle(
    'Calibration Analysis of Qwen2.5-7B — All Four Datasets\n'
    'Top sub-row: confidence frequency (red = wrong, blue = correct)   '
    'Bottom sub-row: accuracy per 5% confidence bin (diagonal = perfect calibration)',
    fontweight='bold', fontsize=10.5, y=0.995,
)

gs4 = fig4.add_gridspec(
    n_total_rows, N_COLS,
    height_ratios=row_heights,
    hspace=0.08,
    wspace=0.30,
    top=0.955, bottom=0.02, left=0.09, right=0.99,
)

DS_BG_COLORS = ['#EEF3FB', '#FFF5ED', '#EDFBF3', '#FBF0FB']

# Row indexing: each dataset takes 3 rows: hist, cal, spacer (last has no spacer)
def ds_row(ds_idx, sub):
    return ds_idx * 3 + sub

for ds_idx, ds in enumerate(DATASET_LABELS):
    hr = ds_row(ds_idx, 0)
    cr = ds_row(ds_idx, 1)

    for col_idx, ck in enumerate(CONFIG_KEYS):
        results = datasets[ds][ck]['results']
        confs   = np.array([r['confidence'] for r in results])
        corr    = np.array([r['is_correct']  for r in results])
        acc_v   = datasets[ds][ck]['accuracy']
        ece_v   = datasets[ds][ck]['ece']
        auroc_v = datasets[ds][ck]['auroc']

        # ── FREQUENCY HISTOGRAM ─────────────────────────────────────────
        ax_hist = fig4.add_subplot(gs4[hr, col_idx])
        ax_hist.set_facecolor(DS_BG_COLORS[ds_idx])

        wrong_conf   = confs[corr == 0] * 100
        correct_conf = confs[corr == 1] * 100
        ax_hist.hist([wrong_conf, correct_conf],
                     bins=np.arange(50, 101, 5), stacked=True,
                     color=[WRONG_COLOR, CORRECT_COLOR],
                     alpha=0.88, edgecolor='white', linewidth=0.5,
                     label=['wrong answer', 'correct answer'])

        if ds_idx == 0:
            ax_hist.set_title(
                f'{CONFIG_FULL_LABELS[col_idx]}\n'
                f'ACC {acc_v:.2f} / AUROC {auroc_v:.2f} / ECE {ece_v:.2f}',
                fontweight='bold', fontsize=8.5, pad=5,
            )
        else:
            ax_hist.set_title(
                f'ACC {acc_v:.2f} / AUROC {auroc_v:.2f} / ECE {ece_v:.2f}',
                fontsize=7.5, pad=3, color='#333333',
            )

        ax_hist.tick_params(labelbottom=False, bottom=False)
        ax_hist.set_xlim(50, 100)
        ax_hist.grid(False)
        ax_hist.spines['bottom'].set_visible(False)

        if col_idx == 0:
            ax_hist.set_ylabel('Count', fontsize=8)
            ax_hist.text(0.01, 0.97, ds, transform=ax_hist.transAxes,
                         fontweight='bold', fontsize=9, va='top', ha='left',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                   edgecolor='#AAAAAA', alpha=0.85))
            if ds_idx == 0:
                ax_hist.legend(fontsize=7.5, loc='upper right', framealpha=0.85)

        # ── CALIBRATION BAR ──────────────────────────────────────────────
        ax_cal = fig4.add_subplot(gs4[cr, col_idx])
        ax_cal.set_facecolor(DS_BG_COLORS[ds_idx])

        bcenters, baccs, _ = compute_calibration_bins(results, bin_size=0.05)
        ax_cal.bar(bcenters * 100, baccs, width=4.5,
                   color=CAL_COLOR, alpha=0.75, edgecolor='black', linewidth=0.35)
        ax_cal.plot([0, 100], [0, 1], 'k--', linewidth=1.3, alpha=0.5,
                    label='Perfect calibration' if (ds_idx == 0 and col_idx == 0) else '')

        ax_cal.set_xlim(0, 100); ax_cal.set_ylim(0, 1)
        ax_cal.set_xlabel('Confidence (%)', fontsize=8)
        ax_cal.spines['top'].set_visible(False)
        ax_cal.grid(False)

        if col_idx == 0:
            ax_cal.set_ylabel('Accuracy\nwithin bin', fontsize=8)
            if ds_idx == 0:
                ax_cal.legend(fontsize=7.5, loc='upper left', framealpha=0.85)

        if ds_idx < N_DS - 1:
            ax_cal.spines['bottom'].set_linewidth(2.0)
            ax_cal.spines['bottom'].set_color('#999999')


fig4.savefig(output_dir / 'combined_calibration_grid.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'combined_calibration_grid.png'}")
plt.close(fig4)

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 5: ECE reduction summary — grouped bar showing % ECE reduction
#           for C1->C2, C1->C3, C1->C4 across all 4 datasets
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Figure 5: ECE reduction summary...")

fig5, (ax_ece, ax_auroc) = plt.subplots(1, 2, figsize=(12, 5))
fig5.suptitle('Component Contribution Summary Across All Datasets',
              fontweight='bold', fontsize=11)

x = np.arange(4)  # 4 datasets
width = 0.22
transitions = [('C1->C2\n2P only', 'config1','config2', '#5A9BD4'),
               ('C1->C3\nMulti only','config1','config3','#F4A460'),
               ('C3->C4\n2P to Multi','config3','config4','#E74C3C'),
               ('C1->C4\nFull system','config1','config4','#2E86AB')]

# ECE % reduction
for ti, (tlabel, from_ck, to_ck, color) in enumerate(transitions):
    reductions = []
    for ds in DATASET_LABELS:
        base = datasets[ds][from_ck]['ece']
        new  = datasets[ds][to_ck]['ece']
        reductions.append((base - new) / base * 100)
    bars = ax_ece.bar(x + (ti - 1.5) * width, reductions, width,
                      label=tlabel, color=color, alpha=0.85,
                      edgecolor='black', linewidth=0.8)
    for bar, v in zip(bars, reductions):
        ax_ece.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                    f'{v:.0f}%', ha='center', va='bottom', fontsize=7, fontweight='bold')

ax_ece.set_xticks(x)
ax_ece.set_xticklabels(DATASET_LABELS, fontsize=8)
ax_ece.set_ylabel('ECE Reduction (%)', fontweight='bold')
ax_ece.set_title('(A) ECE Reduction by Component', fontweight='bold', loc='left')
ax_ece.legend(fontsize=8, ncol=2)
ax_ece.axhline(0, color='black', linewidth=0.8)
ax_ece.set_ylim(-10, 100)

# AUROC absolute gain
for ti, (tlabel, from_ck, to_ck, color) in enumerate(transitions):
    gains = []
    for ds in DATASET_LABELS:
        base = datasets[ds][from_ck]['auroc']
        new  = datasets[ds][to_ck]['auroc']
        gains.append(new - base)
    bars = ax_auroc.bar(x + (ti - 1.5) * width, gains, width,
                        label=tlabel, color=color, alpha=0.85,
                        edgecolor='black', linewidth=0.8)
    for bar, v in zip(bars, gains):
        offset = 0.001 if v >= 0 else -0.001
        va = 'bottom' if v >= 0 else 'top'
        ax_auroc.text(bar.get_x() + bar.get_width()/2., v + offset,
                      f'{v:+.3f}', ha='center', va=va, fontsize=6.5, fontweight='bold')

ax_auroc.set_xticks(x)
ax_auroc.set_xticklabels(DATASET_LABELS, fontsize=8)
ax_auroc.set_ylabel('AUROC Change', fontweight='bold')
ax_auroc.set_title('(B) AUROC Change by Component', fontweight='bold', loc='left')
ax_auroc.legend(fontsize=8, ncol=2)
ax_auroc.axhline(0, color='black', linewidth=0.8)

plt.tight_layout()
fig5.savefig(output_dir / 'combined_component_contribution.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir / 'combined_component_contribution.png'}")
plt.close(fig5)

print("\nAll combined figures saved to:", output_dir)
print("  combined_accuracy_ece_auroc.png")
print("  combined_calibration_curves.png")
print("  combined_roc_curves.png")
print("  combined_calibration_grid.png")
print("  combined_component_contribution.png")
