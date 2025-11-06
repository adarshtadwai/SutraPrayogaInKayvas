#!/usr/bin/env python3
"""
Fill missing word fields by extracting from sentence field.
No AI needed - uses pattern matching.
"""

import json
import re
from pathlib import Path


def extract_word_from_sentence(sentence, verse_text):
    """
    Extract a word from the sentence that appears in the verse.

    Tries various patterns commonly used in Sanskrit commentary.
    """
    if not sentence or not verse_text:
        return ""

    # Remove common Sanskrit grammatical markers and split
    # Pattern 1: Look for quoted words in backticks
    quoted_pattern = r'`([^`]+)`'
    quoted_matches = re.findall(quoted_pattern, sentence)
    for match in quoted_matches:
        # Clean the match
        clean_match = match.strip()
        # Skip if it's a sutra reference (contains dots or pipes)
        if '।' in clean_match or '|' in clean_match or '.' in clean_match:
            continue
        # Check if this word appears in the verse
        if clean_match in verse_text:
            return clean_match

    # Pattern 2: Look for words ending with common case endings
    # Common pattern: "wordः इति" or "word इति"
    iti_pattern = r'(\S+)\s*इति'
    iti_matches = re.findall(iti_pattern, sentence)
    for match in iti_matches:
        # Clean the match
        clean_match = match.strip()
        # Skip if it looks like a sutra reference
        if '।' in clean_match or '|' in clean_match or '.' in clean_match or '`' in clean_match:
            continue
        # Check if this word appears in the verse
        if clean_match in verse_text:
            return clean_match

    # Pattern 3: Look for compound analysis (word च word च = compound)
    compound_pattern = r'(\S+)\s+च\s+\S+\s+च\s+(\S+)'
    compound_matches = re.findall(compound_pattern, sentence)
    for match_tuple in compound_matches:
        compound_word = match_tuple[1]  # The final compound form
        if compound_word in verse_text:
            return compound_word

    # Pattern 4: First significant Devanagari word in sentence
    # (that's not a common grammatical term)
    devanagari_words = re.findall(r'[\u0900-\u097F]+', sentence)
    common_grammar_terms = ['इति', 'च', 'वा', 'अथ', 'तु', 'एव', 'अपि', 'किम्', 'तत्']

    for word in devanagari_words:
        if word not in common_grammar_terms and len(word) > 2:
            if word in verse_text:
                return word

    return ""


def fill_missing_words(extract_file):
    """Fill missing word fields in the extract file."""

    print(f"Loading: {extract_file}")
    with open(extract_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_sutras = sum(len(v.get('sutra_sentences', [])) for v in data['data'])
    empty_before = sum(1 for v in data['data']
                      for s in v.get('sutra_sentences', [])
                      if not s.get('word'))

    print(f"Found {total_sutras} total sutras")
    print(f"Empty word fields: {empty_before}")
    print("Filling missing words...\n")

    filled_count = 0
    still_empty = 0

    for verse_entry in data['data']:
        verse_text = verse_entry.get('v', '')
        loc = verse_entry.get('loc', '')

        for sutra_entry in verse_entry.get('sutra_sentences', []):
            # Only process if word is empty
            if sutra_entry.get('word'):
                continue

            sutra = sutra_entry.get('sutra', '')
            sentence = sutra_entry.get('sentence', '')

            # Try to extract word
            word = extract_word_from_sentence(sentence, verse_text)

            if word:
                sutra_entry['word'] = word
                filled_count += 1
                print(f"✓ Verse {loc}, Sutra {sutra}: '{word}'")
            else:
                still_empty += 1
                print(f"✗ Verse {loc}, Sutra {sutra}: Could not extract")

    print(f"\n{'='*80}")
    print(f"Results:")
    print(f"  Filled: {filled_count}")
    print(f"  Still empty: {still_empty}")
    print(f"{'='*80}\n")

    # Save the file
    print(f"Saving to: {extract_file}")
    with open(extract_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Complete!")

    # Verify final counts
    empty_after = sum(1 for v in data['data']
                     for s in v.get('sutra_sentences', [])
                     if not s.get('word'))
    filled_total = sum(1 for v in data['data']
                      for s in v.get('sutra_sentences', [])
                      if s.get('word'))

    print(f"\nFinal status:")
    print(f"  Total sutras: {total_sutras}")
    print(f"  Filled: {filled_total} ({filled_total/total_sutras*100:.1f}%)")
    print(f"  Empty: {empty_after} ({empty_after/total_sutras*100:.1f}%)")


def main():
    """Main function."""
    project_root = Path(__file__).parent

    files = [
        project_root / 'texts' / 'extract' / 'kumarasambhavam_Extract.json',
        project_root / 'texts' / 'extract' / 'raghuvansham_Extract.json'
    ]

    for extract_file in files:
        if extract_file.exists():
            print(f"\n{'='*80}")
            print(f"Processing: {extract_file.name}")
            print('='*80)
            fill_missing_words(extract_file)
        else:
            print(f"⚠️  File not found: {extract_file}")


if __name__ == '__main__':
    main()
