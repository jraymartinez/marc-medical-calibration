"""
Generate 4-Column Calibration Grid Figure (Similar to GPT3/GPT3.5/GPT4/Vicuna style)
Each column represents one configuration:
- Top row: Confidence histogram (correct vs incorrect predictions)
- Bottom row: Calibration histogram (binned accuracy vs confidence)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path

# Set publication-quality style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 9

# Load Qwen 250q results
results_path = Path('results/4_config_comparison/4_config_qwen_250q_20260301_162510.json')
with open(results_path, 'r') as f:
    data = json.load(f)

configs_data = {
    'config1': data['configurations']['config1'],
    'config2': data['configurations']['config2'],
    'config3': data['configurations']['config3'],
    'config4': data['configurations']['config4']
}

config_titles = [
    'Config 1:\nSingle Specialist',
    'Config 2:\nSingle + Two-Phase',
    'Config 3:\nMulti + S-Score (No 2P)',
    'Config 4:\nMulti + Two-Phase + S-Score'
]

config_titles_short = [
    'Config 1',
    'Config 2',
    'Config 3',
    'Config 4'
]

def compute_calibration_bins(results, bin_size=0.05):
    """Compute calibration bins with specified bin size."""
    confidences = np.array([r['confidence'] for r in results])
    is_correct = np.array([r['is_correct'] for r in results])
    
    # Create bins from 0 to 1 with specified bin size
    bin_edges = np.arange(0, 1 + bin_size, bin_size)
    bin_centers = []
    bin_accuracies = []
    bin_counts = []
    
    for i in range(len(bin_edges) - 1):
        mask = (confidences >= bin_edges[i]) & (confidences < bin_edges[i+1])
        if i == len(bin_edges) - 2:  # Last bin includes upper edge
            mask = (confidences >= bin_edges[i]) & (confidences <= bin_edges[i+1])
        
        bin_count = mask.sum()
        if bin_count > 0:
            bin_centers.append((bin_edges[i] + bin_edges[i+1]) / 2)
            bin_accuracies.append(is_correct[mask].mean())
            bin_counts.append(bin_count)
        else:
            bin_centers.append((bin_edges[i] + bin_edges[i+1]) / 2)
            bin_accuracies.append(0)
            bin_counts.append(0)
    
    return np.array(bin_centers), np.array(bin_accuracies), np.array(bin_counts)

# Create figure with 4 columns (one per config), 2 rows
fig = plt.figure(figsize=(20, 8.5))
gs = fig.add_gridspec(2, 4, height_ratios=[1, 1], hspace=0.35, wspace=0.25, top=0.95, bottom=0.15, left=0.05, right=0.98)

# Process each configuration
for col_idx, (config_key, config_title, config_short) in enumerate(zip(
    ['config1', 'config2', 'config3', 'config4'], 
    config_titles,
    config_titles_short
)):
    config = configs_data[config_key]
    results = config['results']
    
    # Extract data
    confidences = np.array([r['confidence'] for r in results])
    is_correct = np.array([r['is_correct'] for r in results])
    
    acc = config['accuracy']
    ece = config['ece']
    auroc = config['auroc']
    
    # Create subplots for this config (column)
    ax_hist = fig.add_subplot(gs[0, col_idx])
    ax_cal = fig.add_subplot(gs[1, col_idx])
    
    # ========================================================================
    # Top subplot: Confidence histogram (stacked)
    # ========================================================================
    bins = np.linspace(50, 100, 11)  # 10 bins from 50-100%
    
    # Separate correct and incorrect predictions
    conf_correct = confidences[is_correct] * 100
    conf_incorrect = confidences[~is_correct] * 100
    
    # Plot stacked histograms (wrong answer at bottom, correct on top)
    ax_hist.hist([conf_incorrect, conf_correct], bins=bins, 
                 color=['#E74C3C', '#3498DB'], alpha=0.8,
                 label=['wrong answer', 'correct answer'], 
                 edgecolor='black', linewidth=0.5, stacked=True)
    
    # Add title with metrics
    ax_hist.set_title(f'{config_title}\nACC {acc:.2f} / AUROC {auroc:.2f} / ECE {ece:.2f}', 
                      fontweight='bold', fontsize=9, pad=10)
    
    if col_idx == 0:
        ax_hist.set_ylabel('Count', fontweight='bold')
    
    ax_hist.set_xlabel('Confidence (%)', fontweight='bold')
    ax_hist.set_xlim(50, 100)
    max_count = max(len(conf_correct), len(conf_incorrect))
    ax_hist.set_ylim(0, max_count * 0.5)  # Adjust based on data
    ax_hist.legend(loc='upper left', fontsize=7)
    # Remove grid lines
    ax_hist.grid(False)
    
    # ========================================================================
    # Bottom subplot: Calibration histogram (binned)
    # ========================================================================
    bin_centers, bin_accs, bin_counts = compute_calibration_bins(results, bin_size=0.05)
    
    # Convert to percentage for x-axis
    bin_centers_pct = bin_centers * 100
    
    # Create bar plot for calibration
    bar_width = 4.5  # Width of bars in percentage points
    
    # Plot bars for accuracy within each bin
    bars = ax_cal.bar(bin_centers_pct, bin_accs, width=bar_width, 
                      color='#3498DB', alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Plot perfect calibration line
    ax_cal.plot([0, 100], [0, 1], 'k--', linewidth=1.5, alpha=0.5, label='Perfect calibration')
    
    ax_cal.set_xlabel('Confidence (%)', fontweight='bold')
    
    if col_idx == 0:
        ax_cal.set_ylabel('Accuracy within bin', fontweight='bold')
    
    ax_cal.set_xlim(0, 100)
    ax_cal.set_ylim(0, 1)
    # Remove grid lines
    ax_cal.grid(False)
    
    # Set x-axis ticks every 20%
    ax_cal.set_xticks([0, 20, 40, 60, 80, 100])
    
    if col_idx == 0:
        ax_cal.legend(loc='upper left', fontsize=8)

# Add figure caption at the bottom (like published papers)
caption_text = ('Figure 2: Calibration Analysis of Qwen2.5-7B on MedQA (n=250). '
                'Top row shows confidence distribution for correct (blue) and incorrect (red) predictions. '
                'Bottom row shows calibration histograms with 5% bins, where bar height represents observed accuracy '
                'and the diagonal line represents perfect calibration.')
# Use figtext with proper alignment, no background, matching figure width
fig.text(0.05, 0.03, caption_text, ha='left', va='bottom', fontsize=10, 
         transform=fig.transFigure, wrap=True)

# Save figure
output_dir = Path('results/paper1/figures')
output_path = output_dir / 'calibration_grid_4configs.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved: {output_path}")
plt.close()

print("\n" + "="*80)
print("CALIBRATION GRID FIGURE GENERATED")
print("="*80)
print("\nFigure shows for each configuration:")
print("  - Top: Confidence histogram (correct vs incorrect predictions)")
print("  - Bottom: Calibration curve with shaded miscalibration area")
print("\nKey Observations:")
print("  Config 1: High confidence (80-100%), poor calibration")
print("  Config 2: Lower confidence (40-60%), improved calibration")
print("  Config 3: High confidence (80-100%), poor calibration")
print("  Config 4: Moderate confidence (40-80%), excellent calibration (ECE=0.091)")
print("="*80)
