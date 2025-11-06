#!/usr/bin/env python3
"""
Test script to demonstrate the enhancement process on a single example.

This shows what the Claude API will do - analyze Sanskrit commentary and extract:
1. The word being explained by the sutra
2. The description (relevant commentary text)
"""

import json
from pathlib import Path


def show_example():
    """Show an example of what needs to be enhanced."""

    # Load the extract file
    extract_file = Path(__file__).parent.parent / 'texts' / 'extract' / 'kumarasambhavam_Extract.json'
    source_file = Path(__file__).parent.parent / 'texts' / 'In' / 'kumarasambhavam.json'

    with open(extract_file, 'r', encoding='utf-8') as f:
        extract_data = json.load(f)

    with open(source_file, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    # Get first verse
    first_verse = extract_data['data'][0]
    loc = first_verse['loc']

    # Find corresponding commentary
    commentary = None
    for entry in source_data['data']:
        if f"{entry['c']}.{entry['n']}" == loc:
            commentary = entry['mn']
            break

    print("="*80)
    print("EXAMPLE: What the enhancement script will do")
    print("="*80)
    print(f"\nVerse Location: {loc}")
    print(f"Verse Text: {first_verse['v']}")
    print(f"\nNumber of sutras to enhance: {len(first_verse['sutra_sentences'])}")

    for i, sutra_entry in enumerate(first_verse['sutra_sentences'], 1):
        print(f"\n{'-'*80}")
        print(f"Sutra {i}:")
        print(f"{'-'*80}")
        print(f"Sutra Number: {sutra_entry['sutra']}")
        print(f"Sentence: {sutra_entry['sentence'][:100]}...")
        print(f"Word (current): '{sutra_entry['word']}' (empty - needs to be filled)")
        print(f"Description (current): Not present - needs to be added")

        print(f"\n📝 What Claude will analyze:")
        print(f"Full commentary:\n{commentary[:300]}...\n")

        print(f"🎯 Claude's task:")
        print(f"1. Find the Sanskrit WORD that sutra {sutra_entry['sutra']} is explaining")
        print(f"2. Extract the DESCRIPTION (commentary lines discussing this sutra)")

    print(f"\n{'='*80}")
    print("To run the actual enhancement:")
    print("="*80)
    print("1. Set your Anthropic API key:")
    print("   export ANTHROPIC_API_KEY='your-key-here'")
    print("\n2. Run the enhancement script:")
    print("   python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract_test.json")
    print("\nOr for the full file:")
    print("   python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract.json")
    print("="*80)


if __name__ == '__main__':
    show_example()
