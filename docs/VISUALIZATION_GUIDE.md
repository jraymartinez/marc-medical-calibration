# Visualization Guide for Paper 1

This guide explains how to generate publication-quality visualizations from your experimental results.

## Overview

The visualization script (`scripts/visualize_comparison.py`) generates five types of outputs:

1. **Calibration Analysis** - Reliability diagram showing confidence vs accuracy
2. **ROC Analysis** - Discrimination curves for error detection
3. **Accuracy Comparison** - Bar chart with statistical significance testing
4. **Combined Figure** - All three analyses in one publication-ready figure
5. **LaTeX Table** - Formatted table for direct inclusion in papers

## Usage

### Basic Command

```bash
python scripts/visualize_comparison.py <results_file>
```

### Example

```bash
# After running the 4-configuration comparison
python scripts/visualize_comparison.py results/paper1/comparison_4configs_20260108_120000.json
```

### Custom Output Directory

```bash
python scripts/visualize_comparison.py results/paper1/comparison_4configs_20260108_120000.json \
    --output-dir results/paper1/my_figures
```

## Generated Files

All figures are saved at **300 DPI** for publication quality:

### 1. `calibration_analysis.png`
- **Purpose**: Shows how well confidence scores match actual accuracy
- **Metric**: Expected Calibration Error (ECE)
- **Goal**: ECE < 0.05 (well-calibrated)
- **Interpretation**: Points closer to diagonal = better calibration

### 2. `roc_analysis.png`
- **Purpose**: Shows ability to distinguish correct from incorrect predictions using confidence
- **Metric**: Area Under ROC Curve (AUROC)
- **Goal**: AUROC > 0.85 (strong discrimination)
- **Interpretation**: Curves further from diagonal = better discrimination

### 3. `accuracy_comparison.png`
- **Purpose**: Compares diagnostic accuracy across configurations
- **Metric**: Accuracy percentage
- **Test**: McNemar's test for statistical significance
- **Interpretation**: 
  - `***` = p < 0.001 (highly significant)
  - `**` = p < 0.01 (very significant)
  - `*` = p < 0.05 (significant)
  - `ns` = not significant

### 4. `combined_analysis.png` ⭐ **PUBLICATION-READY**
- **Purpose**: Three-panel figure combining all analyses
- **Size**: 16" × 5" (optimal for journal papers)
- **Format**: Publication-quality PNG at 300 DPI
- **Usage**: Ready to insert directly into your paper

### 5. `metrics_table.tex`
- **Purpose**: LaTeX-formatted table of all metrics
- **Usage**: Copy-paste into your paper's LaTeX source
- **Includes**: Accuracy, ECE, AUROC, Average Confidence

## Metrics Explanation

### Expected Calibration Error (ECE)
- Measures difference between predicted confidence and actual accuracy
- **Lower is better** (0 = perfect calibration)
- **Target**: < 0.05

### Area Under ROC Curve (AUROC)
- Measures how well confidence identifies errors
- **Higher is better** (1.0 = perfect discrimination, 0.5 = random)
- **Target**: > 0.85

### Accuracy
- Percentage of correct predictions
- **Higher is better**
- Baseline for improvement

### Average Confidence
- Mean confidence across all predictions
- Should align with accuracy for good calibration

## Visualization Features

### Publication Quality
- **Resolution**: 300 DPI (journal standard)
- **Fonts**: Serif fonts for professional appearance
- **Colors**: Colorblind-friendly palette
- **Format**: PNG with tight bounding boxes

### Statistical Testing
- **McNemar's Test**: Paired test for binary outcomes
- **Baseline**: Compares all configurations to "No Verification"
- **Significance Levels**: Three levels (p < 0.05, 0.01, 0.001)

### Color Scheme
- **Gray** (#95A5A6): Baseline (No Verification)
- **Blue** (#3498DB): Tier 1 Only
- **Green** (#2ECC71): Full Linear (α=0.5)
- **Purple** (#9B59B6): Bayesian

## Example Workflow

### Step 1: Run Experiments
```bash
python scripts/compare_4_configs.py
```

### Step 2: Generate Visualizations
```bash
python scripts/visualize_comparison.py results/paper1/comparison_4configs_20260108_120000.json
```

### Step 3: Use in Paper

**For Figures:**
1. Use `combined_analysis.png` as your main results figure
2. Reference in LaTeX:
```latex
\begin{figure}[h]
\centering
\includegraphics[width=\textwidth]{figures/combined_analysis.png}
\caption{Performance comparison of hierarchical verification configurations...}
\label{fig:main_results}
\end{figure}
```

**For Tables:**
1. Copy contents of `metrics_table.tex`
2. Paste directly into your paper's LaTeX source

**For Individual Panels:**
- Use separate PNG files if you need to discuss each analysis individually
- Great for supplementary materials

## Customization

### Adding More Configurations
The script automatically handles any number of configurations in the input JSON.

### Changing Colors
Edit the `colors` dictionary in the script:
```python
colors = {
    'No Verification': '#95A5A6',
    'Tier 1 Only': '#3498DB',
    'Full Linear (a=0.5)': '#2ECC71',
    'Bayesian': '#9B59B6'
}
```

### Adjusting Figure Size
Modify `figsize` parameters:
```python
# Individual plots
fig, ax = plt.subplots(figsize=(6, 5))

# Combined figure
fig = plt.figure(figsize=(16, 5))
```

### Changing DPI
Edit at the top of the script:
```python
plt.rcParams['figure.dpi'] = 600  # For ultra-high quality
```

## Troubleshooting

### "No module named 'matplotlib'"
```bash
pip install matplotlib scipy
```

### Figures look blurry
- Check DPI setting (should be 300+)
- Ensure `savefig.dpi` is set correctly

### Colors not showing
- Check that your terminal/viewer supports color
- Try opening PNG files in an image viewer

### LaTeX table not rendering
- Ensure you have the required LaTeX packages (`booktabs`, `tabular`)
- Check for special characters in configuration names

## Citation

When using these visualizations in your paper, consider citing the metrics:

**For ECE:**
> Naeini, M. P., Cooper, G., & Hauskrecht, M. (2015). Obtaining well calibrated probabilities using bayesian binning. In AAAI.

**For AUROC:**
> Fawcett, T. (2006). An introduction to ROC analysis. Pattern recognition letters, 27(8), 861-874.

**For McNemar's Test:**
> McNemar, Q. (1947). Note on the sampling error of the difference between correlated proportions or percentages. Psychometrika, 12(2), 153-157.

## Tips for Paper Writing

1. **Main Figure**: Use `combined_analysis.png` as your primary results figure
2. **Emphasis**: Highlight improvements in ECE (calibration) and AUROC (discrimination)
3. **Significance**: Report p-values from McNemar's test
4. **Interpretation**: 
   - Good calibration: ECE close to 0, points follow diagonal
   - Good discrimination: AUROC > 0.85, ROC curve bows upward
   - Significant improvement: p < 0.05 vs baseline

## Next Steps

After generating visualizations:
1. Review all figures for clarity
2. Check that metrics align with your hypotheses
3. Prepare figure captions explaining each panel
4. Include in your manuscript
5. Submit to journal! 🎉
