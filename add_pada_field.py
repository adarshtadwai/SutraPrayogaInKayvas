#!/usr/bin/env python3
"""
Add 'pada' field to extract files.
The pada field contains the half of the verse where the word appears.
"""

import json
import sys
from pathlib import Path


def find_pada_for_word(verse_text, word):
    """
    Find which pada (half-verse) contains the word.

    Sanskrit verses are typically divided by । (danda).
    Returns the pada containing the word, or full verse if not found.
    """
    if not word or not verse_text:
        return ""

    # Split verse by danda (।)
    parts = verse_text.split('।')

    # Clean up parts and remove double-danda (॥)
    padas = [p.strip().replace('॥', '').strip() for p in parts if p.strip()]

    # Search for word in each pada
    for pada in padas:
        if word in pada:
            return pada

    # If exact word not found, try to find word as part of compound
    # by checking if any significant portion of the word exists in pada
    if len(word) > 3:
        word_root = word[:len(word)//2]  # Take first half of word
        for pada in padas:
            if word_root in pada:
                return pada

    # Fallback: return first pada if word not found
    return padas[0] if padas else verse_text


def add_pada_field(input_file, output_file=None):
    """Add pada field to all sutra entries in the file."""

    if output_file is None:
        output_file = input_file

    print(f"Loading: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_verses = len(data.get('data', []))
    total_sutras = sum(len(v.get('sutra_sentences', [])) for v in data['data'])

    print(f"Found {total_verses} verses with {total_sutras} sutra references")
    print("Adding pada field...\n")

    processed = 0
    for verse_entry in data['data']:
        verse_text = verse_entry.get('v', '')
        loc = verse_entry.get('loc', '')

        for sutra_entry in verse_entry.get('sutra_sentences', []):
            word = sutra_entry.get('word', '')

            # Find and add pada
            pada = find_pada_for_word(verse_text, word)
            sutra_entry['pada'] = pada

            processed += 1
            if processed % 50 == 0:
                print(f"Processed {processed}/{total_sutras} sutras...")

    # Update comment
    if 'pada field' not in data.get('comment', ''):
        data['comment'] = data.get('comment', '') + " [pada field added]"

    print(f"\nSaving to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Complete!")

    # Show some examples
    print("\nExample entries:")
    for i, verse in enumerate(data['data'][:3], 1):
        print(f"\nVerse {verse['loc']}:")
        print(f"Full: {verse['v']}")
        for s in verse['sutra_sentences'][:2]:  # Show max 2 sutras per verse
            print(f"  Sutra {s['sutra']}")
            print(f"    word: {s.get('word', 'N/A')}")
            print(f"    pada: {s.get('pada', 'N/A')}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 add_pada_field.py <extract_file>")
        print("\nProcessing both default files...")

        project_root = Path(__file__).parent
        files = [
            project_root / 'texts' / 'extract' / 'kumarasambhavam_Extract.json',
            project_root / 'texts' / 'extract' / 'raghuvansham_Extract.json'
        ]

        for file in files:
            if file.exists():
                print(f"\n{'='*80}")
                add_pada_field(file)
                print('='*80)
            else:
                print(f"⚠️  File not found: {file}")
    else:
        input_file = sys.argv[1]
        add_pada_field(input_file)


if __name__ == '__main__':
    main()
