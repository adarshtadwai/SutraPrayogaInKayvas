#!/usr/bin/env python3
"""
Enhanced script to fill word and description fields for sutra entries.
Uses Sanskrit understanding to properly analyze commentary and extract relevant information.
"""

import json
import re
from pathlib import Path

def analyze_sutra_in_commentary(mn_text, sutra_ref, verse_text, sentence):
    """
    Analyze the commentary to find the word and description for a sutra.

    This function uses Sanskrit understanding to:
    1. Find where the sutra is referenced in the commentary
    2. Extract the word from the verse that this sutra applies to
    3. Extract the full explanation/description

    Args:
        mn_text: Full commentary text
        sutra_ref: Sutra reference like "2.1.49"
        verse_text: The actual verse being commented on
        sentence: The sentence already extracted with sutra

    Returns:
        tuple: (word, description)
    """

    # Convert sutra ref to the format used in commentary (पा.2|1|49)
    sutra_pattern = sutra_ref.replace(".", r"\|")

    # Find the sutra mention in commentary
    # Pattern: `sutra text` (पा.X|Y|Z) इति explanation
    full_pattern = rf'([^`]*?)\s*`([^`]+)`\s*\(पा\.{sutra_pattern}\)(.*?)(?:।|॥|\s*`)'

    match = re.search(full_pattern, mn_text, re.DOTALL)

    if not match:
        # Fallback: just use the sentence as description
        return "", sentence

    preceding_text = match.group(1).strip()
    sutra_text = match.group(2).strip()
    following_text = match.group(3).strip()

    # The description includes the sutra and the explanation following it
    # Usually ends at the next । or ॥
    description = f"`{sutra_text}` (पा.{sutra_ref}) {following_text}"

    # Clean up description - find the end marker
    end_markers = ['।', '॥']
    min_end = len(description)
    for marker in end_markers:
        pos = description[len(f"`{sutra_text}` (पा.{sutra_ref})"):].find(marker)
        if pos != -1:
            actual_pos = len(f"`{sutra_text}` (पा.{sutra_ref})") + pos + 1
            min_end = min(min_end, actual_pos)

    if min_end < len(description):
        description = description[:min_end].strip()

    # Now find the word being explained
    # Look in the preceding text for the word from the verse
    # Common patterns:
    # - "wordX । `sutra`" - word appears before the sutra
    # - "wordX word explanation । `sutra`" - compound explanation before sutra

    word = extract_word_from_context(preceding_text, verse_text, sutra_text)

    return word, description


def extract_word_from_context(preceding_text, verse_text, sutra_text):
    """
    Extract the word being explained from the context before the sutra.

    Args:
        preceding_text: Text before the sutra reference
        verse_text: The verse being commented on
        sutra_text: The sutra rule text

    Returns:
        str: The word being explained
    """

    # Split preceding text into sentences
    sentences = re.split(r'[।॥]', preceding_text)

    if not sentences:
        return ""

    # The last sentence before the sutra usually contains the word
    last_sentence = sentences[-1].strip()

    # Look for common patterns:
    # 1. "word1 च word2 च word-compound" - compound formation
    # 2. "word explanation" - simple explanation
    # 3. "word । description" - word followed by description

    # Pattern 1: Look for compound words (often bold in original)
    # Example: "सर्वे च ते शैलाश्च सर्वशैलाः"
    compound_pattern = r'([^\s।॥]+)(?:\s+च\s+[^\s।॥]+\s+च\s+)?([^\s।॥]+)\s*$'
    match = re.search(compound_pattern, last_sentence)

    if match:
        # The last word is usually the compound or result
        word = match.group(2) if match.group(2) else match.group(1)
        return word.strip()

    # Pattern 2: Last substantial word before sutra
    words = last_sentence.split()
    if words:
        # Filter out particles and short words
        for w in reversed(words):
            if len(w) > 2 and not w in ['इति', 'अत्र', 'तत्र', 'यत्र']:
                return w.strip()

    return ""


def process_verse_sutras(verse_loc, verse_text, mn_text, sutra_sentences):
    """
    Process all sutras for a single verse.

    Args:
        verse_loc: Location string like "1.2"
        verse_text: The verse text
        mn_text: The commentary text
        sutra_sentences: List of sutra sentence dicts to fill

    Returns:
        int: Number of sutras successfully filled
    """
    filled_count = 0

    print(f"\nAnalyzing verse {verse_loc}")
    print(f"Verse: {verse_text[:50]}...")

    for sutra_sent in sutra_sentences:
        sutra_ref = sutra_sent['sutra']
        sentence = sutra_sent['sentence']

        print(f"  Sutra {sutra_ref}:")

        # Analyze the commentary
        word, description = analyze_sutra_in_commentary(
            mn_text, sutra_ref, verse_text, sentence
        )

        if word or description:
            sutra_sent['word'] = word
            sutra_sent['description'] = description
            filled_count += 1
            print(f"    Word: {word}")
            print(f"    Desc: {description[:60]}...")
        else:
            print(f"    Warning: Could not extract full context")

    return filled_count


def main():
    """Main processing function."""

    base_path = Path(__file__).parent.parent.parent
    source_path = base_path / "texts" / "In" / "kumarasambhavam.json"
    extract_path = base_path / "texts" / "extract" / "kumarasambhavam_Extract.json"
    output_path = extract_path

    print(f"Loading source commentary: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    print(f"Loading extract file: {extract_path}")
    with open(extract_path, 'r', encoding='utf-8') as f:
        extract_data = json.load(f)

    # Create lookup for source verses
    source_lookup = {}
    for verse in source_data.get('data', []):
        loc = f"{verse['c']}.{verse['n']}"
        source_lookup[loc] = verse

    total_sutras = 0
    filled_sutras = 0

    # Process each verse
    for verse in extract_data['data']:
        loc = verse['loc']
        verse_text = verse.get('v', '')

        # Get source commentary
        source_verse = source_lookup.get(loc)
        if not source_verse:
            print(f"Warning: No source verse for {loc}")
            continue

        mn_text = source_verse.get('mn', '')
        if not mn_text:
            print(f"Warning: No commentary for {loc}")
            continue

        # Process all sutras in this verse
        sutra_sentences = verse.get('sutra_sentences', [])
        total_sutras += len(sutra_sentences)

        filled = process_verse_sutras(
            loc, verse_text, mn_text, sutra_sentences
        )
        filled_sutras += filled

    # Save enhanced extract
    print(f"\nSaving enhanced extract to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extract_data, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Processing Complete!")
    print(f"{'='*60}")
    print(f"Total verses: {len(extract_data['data'])}")
    print(f"Total sutras: {total_sutras}")
    print(f"Successfully filled: {filled_sutras}")
    print(f"Success rate: {filled_sutras/total_sutras*100:.1f}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
