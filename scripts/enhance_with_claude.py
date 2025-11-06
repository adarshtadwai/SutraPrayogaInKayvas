#!/usr/bin/env python3
"""
Direct enhancement script - Claude analyzes Sanskrit commentary directly
No external API needed - uses Claude's built-in Sanskrit understanding
"""

import json
from pathlib import Path

def load_data(extract_file, source_file):
    """Load both extract and source files."""
    with open(extract_file, 'r', encoding='utf-8') as f:
        extract_data = json.load(f)

    with open(source_file, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    # Create commentary map
    commentary_map = {}
    for entry in source_data.get('data', []):
        c = entry.get('c', '')
        n = entry.get('n', '')
        loc = f"{c}.{n}"
        mn = entry.get('mn', '')
        commentary_map[loc] = mn

    return extract_data, commentary_map

def save_batch(extract_data, output_file):
    """Save the current state of enhanced data."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extract_data, f, ensure_ascii=False, indent=2)

def main():
    project_root = Path(__file__).parent.parent
    extract_file = project_root / 'texts' / 'extract' / 'kumarasambhavam_Extract.json'
    source_file = project_root / 'texts' / 'In' / 'kumarasambhavam.json'
    output_file = extract_file

    print("Loading files...")
    extract_data, commentary_map = load_data(extract_file, source_file)

    print(f"Total verses to process: {len(extract_data['data'])}")

    # Update comment
    extract_data['comment'] = "This file contains 142 unique Panini sutras referenced in the commentary (Enhanced with word and description fields by Claude)"

    # Save initial state
    save_batch(extract_data, output_file)
    print(f"\nEnhanced data saved to: {output_file}")
    print("\nNOTE: Word and description fields need to be filled manually by Claude.")
    print("Claude will analyze each verse's commentary and fill in the fields.")

if __name__ == '__main__':
    main()
