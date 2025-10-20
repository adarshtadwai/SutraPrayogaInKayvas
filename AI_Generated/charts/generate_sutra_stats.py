#!/usr/bin/env python3
"""
Generate statistical visualizations for Sutra Prayoga data.

This script creates various charts showing the distribution and overlap
of Panini sutras across रघुवंशम् and कुमारसम्भवम् commentaries.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# Set up matplotlib for better-looking charts
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (12, 8)

def load_data():
    """Load sutra data from extract files."""
    base_path = Path(__file__).parent.parent.parent

    raghuvansham = json.load(open(base_path / 'texts/extract/raghuvansham_Extract.json'))
    kumarasambhavam = json.load(open(base_path / 'texts/extract/kumarasambhavam_Extract.json'))

    # Extract unique sutras
    raghuvansham_sutras = set()
    raghuvansham_refs = 0
    for entry in raghuvansham['data']:
        for ss in entry['sutra_sentences']:
            raghuvansham_sutras.add(ss['sutra'])
            raghuvansham_refs += 1

    kumarasambhavam_sutras = set()
    kumarasambhavam_refs = 0
    for entry in kumarasambhavam['data']:
        for ss in entry['sutra_sentences']:
            kumarasambhavam_sutras.add(ss['sutra'])
            kumarasambhavam_refs += 1

    return {
        'raghuvansham_sutras': raghuvansham_sutras,
        'kumarasambhavam_sutras': kumarasambhavam_sutras,
        'raghuvansham_refs': raghuvansham_refs,
        'kumarasambhavam_refs': kumarasambhavam_refs
    }

def create_pie_chart(data, output_path):
    """Create pie chart showing distribution of unique sutras."""
    raghuvansham_sutras = data['raghuvansham_sutras']
    kumarasambhavam_sutras = data['kumarasambhavam_sutras']

    common = raghuvansham_sutras & kumarasambhavam_sutras
    only_raghuvansham = raghuvansham_sutras - kumarasambhavam_sutras
    only_kumarasambhavam = kumarasambhavam_sutras - raghuvansham_sutras

    sizes = [len(only_raghuvansham), len(only_kumarasambhavam), len(common)]
    labels = [
        f'Only in Raghuvamsham\n({len(only_raghuvansham)} sutras)',
        f'Only in Kumarasambhavam\n({len(only_kumarasambhavam)} sutras)',
        f'In Both Texts\n({len(common)} sutras)'
    ]
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    explode = (0.05, 0.05, 0.1)

    plt.figure(figsize=(10, 8))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('Distribution of Unique Panini Sutras\nAcross Raghuvamsham and Kumarasambhavam',
              fontsize=14, fontweight='bold', pad=20)
    plt.axis('equal')

    plt.tight_layout()
    plt.savefig(output_path / 'sutra_distribution_pie.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path / 'sutra_distribution_pie.png'}")

def create_venn_diagram(data, output_path):
    """Create a bar chart representing Venn diagram concept."""
    raghuvansham_sutras = data['raghuvansham_sutras']
    kumarasambhavam_sutras = data['kumarasambhavam_sutras']

    common = len(raghuvansham_sutras & kumarasambhavam_sutras)
    only_raghuvansham = len(raghuvansham_sutras - kumarasambhavam_sutras)
    only_kumarasambhavam = len(kumarasambhavam_sutras - raghuvansham_sutras)

    fig, ax = plt.subplots(figsize=(12, 6))

    categories = ['Only\nRaghuvamsham', 'Both\nTexts', 'Only\nKumarasambhavam']
    values = [only_raghuvansham, common, only_kumarasambhavam]
    colors = ['#ff9999', '#99ff99', '#66b3ff']

    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value}\n({value/(only_raghuvansham+common+only_kumarasambhavam)*100:.1f}%)',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Number of Unique Sutras', fontsize=12, fontweight='bold')
    ax.set_title('Overlap of Panini Sutras Between Texts', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, max(values) * 1.15)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path / 'sutra_overlap_bars.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path / 'sutra_overlap_bars.png'}")

def create_coverage_chart(data, output_path):
    """Create stacked bar chart showing coverage."""
    raghuvansham_sutras = data['raghuvansham_sutras']
    kumarasambhavam_sutras = data['kumarasambhavam_sutras']
    total_unique = len(raghuvansham_sutras | kumarasambhavam_sutras)

    common = raghuvansham_sutras & kumarasambhavam_sutras
    only_raghuvansham = raghuvansham_sutras - kumarasambhavam_sutras
    only_kumarasambhavam = kumarasambhavam_sutras - raghuvansham_sutras

    fig, ax = plt.subplots(figsize=(12, 6))

    # Data for stacked bars
    texts = ['Raghuvamsham', 'Kumarasambhavam']
    exclusive = [len(only_raghuvansham), len(only_kumarasambhavam)]
    shared = [len(common), len(common)]

    x = range(len(texts))
    width = 0.5

    bars1 = ax.bar(x, exclusive, width, label='Exclusive Sutras', color='#ff9999')
    bars2 = ax.bar(x, shared, width, bottom=exclusive, label='Shared Sutras', color='#99ff99')

    # Add value labels
    for i, (e, s) in enumerate(zip(exclusive, shared)):
        # Exclusive label
        ax.text(i, e/2, f'{e}\n({e/total_unique*100:.1f}%)',
                ha='center', va='center', fontsize=11, fontweight='bold')
        # Shared label
        ax.text(i, e + s/2, f'{s}\n({s/total_unique*100:.1f}%)',
                ha='center', va='center', fontsize=11, fontweight='bold')
        # Total label
        ax.text(i, e + s + 10, f'Total: {e+s}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel('Number of Unique Sutras', fontsize=12, fontweight='bold')
    ax.set_title('Sutra Coverage by Text (Exclusive vs Shared)', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(texts, fontsize=12)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_ylim(0, max([e+s for e, s in zip(exclusive, shared)]) * 1.15)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path / 'sutra_coverage_stacked.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path / 'sutra_coverage_stacked.png'}")

def create_references_chart(data, output_path):
    """Create chart comparing unique sutras vs total references."""
    raghuvansham_sutras = data['raghuvansham_sutras']
    kumarasambhavam_sutras = data['kumarasambhavam_sutras']
    raghuvansham_refs = data['raghuvansham_refs']
    kumarasambhavam_refs = data['kumarasambhavam_refs']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Chart 1: Unique Sutras
    texts = ['Raghuvamsham', 'Kumarasambhavam']
    unique_counts = [len(raghuvansham_sutras), len(kumarasambhavam_sutras)]
    colors1 = ['#ff9999', '#66b3ff']

    bars1 = ax1.bar(texts, unique_counts, color=colors1, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax1.set_title('Unique Sutras by Text', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    for bar, value in zip(bars1, unique_counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{value}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Chart 2: Total References
    ref_counts = [raghuvansham_refs, kumarasambhavam_refs]
    colors2 = ['#ffcc99', '#99ccff']

    bars2 = ax2.bar(texts, ref_counts, color=colors2, edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax2.set_title('Total References by Text', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    for bar, value, unique in zip(bars2, ref_counts, unique_counts):
        height = bar.get_height()
        avg = value / unique
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{value}\n(avg {avg:.2f}/sutra)',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.suptitle('Unique Sutras vs Total References', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path / 'sutra_references_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path / 'sutra_references_comparison.png'}")

def create_summary_stats_image(data, output_path):
    """Create an image with key statistics."""
    raghuvansham_sutras = data['raghuvansham_sutras']
    kumarasambhavam_sutras = data['kumarasambhavam_sutras']
    raghuvansham_refs = data['raghuvansham_refs']
    kumarasambhavam_refs = data['kumarasambhavam_refs']

    common = raghuvansham_sutras & kumarasambhavam_sutras
    total_unique = len(raghuvansham_sutras | kumarasambhavam_sutras)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')

    # Title
    title_text = 'Panini Sutra Statistics Summary\nKavya Prayogas'
    ax.text(0.5, 0.95, title_text, ha='center', va='top', fontsize=18,
            fontweight='bold', transform=ax.transAxes)

    # Statistics text
    stats_text = f"""
Total Unique Sutras: {total_unique}

Raghuvamsham Coverage:
  • Unique Sutras: {len(raghuvansham_sutras)} ({len(raghuvansham_sutras)/total_unique*100:.1f}% of total)
  • Total References: {raghuvansham_refs}
  • Average: {raghuvansham_refs/len(raghuvansham_sutras):.2f} references per sutra
  • Exclusive Sutras: {len(raghuvansham_sutras - kumarasambhavam_sutras)} ({len(raghuvansham_sutras - kumarasambhavam_sutras)/len(raghuvansham_sutras)*100:.1f}%)

Kumarasambhavam Coverage:
  • Unique Sutras: {len(kumarasambhavam_sutras)} ({len(kumarasambhavam_sutras)/total_unique*100:.1f}% of total)
  • Total References: {kumarasambhavam_refs}
  • Average: {kumarasambhavam_refs/len(kumarasambhavam_sutras):.2f} references per sutra
  • Exclusive Sutras: {len(kumarasambhavam_sutras - raghuvansham_sutras)} ({len(kumarasambhavam_sutras - raghuvansham_sutras)/len(kumarasambhavam_sutras)*100:.1f}%)

Overlap Analysis:
  • Sutras in Both Texts: {len(common)} ({len(common)/total_unique*100:.1f}% of total)
  • Overlap from Raghuvamsham perspective: {len(common)/len(raghuvansham_sutras)*100:.1f}%
  • Overlap from Kumarasambhavam perspective: {len(common)/len(kumarasambhavam_sutras)*100:.1f}%

Total References Across Both Texts: {raghuvansham_refs + kumarasambhavam_refs}
"""

    ax.text(0.5, 0.82, stats_text, ha='center', va='top', fontsize=11,
            family='monospace', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    plt.savefig(output_path / 'sutra_statistics_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path / 'sutra_statistics_summary.png'}")

def main():
    """Generate all charts."""
    output_path = Path(__file__).parent

    print("Loading sutra data...")
    data = load_data()

    print("\nGenerating charts...")
    create_pie_chart(data, output_path)
    create_venn_diagram(data, output_path)
    create_coverage_chart(data, output_path)
    create_references_chart(data, output_path)
    create_summary_stats_image(data, output_path)

    print("\n✓ All charts generated successfully!")
    print(f"Charts saved to: {output_path}")

if __name__ == '__main__':
    main()
