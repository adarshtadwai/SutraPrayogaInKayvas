# Sutra Statistics Visualizations

This directory contains statistical visualizations and analysis of Panini sutras referenced in Mallinatha's commentaries on Kalidasa's works.

## Files

### 📊 Visualizations (PNG images)

1. **`sutra_distribution_pie.png`** - Pie chart showing distribution of unique sutras
   - 72.37% only in Raghuvamsham
   - 13.23% only in Kumarasambhavam
   - 14.40% in both texts

2. **`sutra_overlap_bars.png`** - Bar chart showing overlap between texts
   - Exclusive vs shared sutras across both works

3. **`sutra_coverage_stacked.png`** - Stacked bar chart comparing coverage
   - Shows exclusive and shared sutras for each text

4. **`sutra_references_comparison.png`** - Comparison of unique sutras vs total references
   - Raghuvamsham: 446 sutras, 698 references (avg 1.57/sutra)
   - Kumarasambhavam: 142 sutras, 172 references (avg 1.21/sutra)

5. **`sutra_statistics_summary.png`** - Complete statistical summary
   - All key metrics in one image

### 📝 Documentation

- **`STATISTICS.md`** - Comprehensive markdown report with:
  - All statistics and percentages
  - Embedded visualizations
  - Key insights and analysis
  - Instructions for regeneration

### 🔧 Script

- **`generate_sutra_stats.py`** - Python script to generate all visualizations
  - Reads data from `texts/extract/*.json`
  - Uses matplotlib for chart generation
  - Can be re-run to update charts after data changes

## Quick Stats

- **Total Unique Sutras**: 514
- **Raghuvamsham**: 446 sutras (86.77% coverage)
- **Kumarasambhavam**: 142 sutras (27.63% coverage)
- **Common to Both**: 74 sutras (14.40%)
- **Total References**: 870

## Regenerating Charts

To regenerate all visualizations after updating the data:

```bash
python3 AI_Generated/charts/generate_sutra_stats.py
```

**Requirements**: matplotlib (install with `pip3 install matplotlib`)

## Notes

- All text in charts uses English transliteration (Raghuvamsham, Kumarasambhavam) for better font compatibility
- Charts are generated at 300 DPI for high quality
- Source data comes from the extract files in `texts/extract/`
