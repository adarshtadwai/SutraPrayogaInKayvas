#!/usr/bin/env python3
"""
Script to enhance kumarasambhavam_Extract.json by filling in word and description fields
for all sutra entries using the commentary from kumarasambhavam.json
"""

import json
import re
from pathlib import Path

def find_sutra_context(mn_text, sutra_ref):
    """
    Extract the word and description for a given sutra reference from commentary.

    Args:
        mn_text: The full commentary text (mn field)
        sutra_ref: The sutra reference (e.g., "2.1.49")

    Returns:
        tuple: (word, description) - the word being explained and its description
    """
    # Clean the sutra reference for searching
    sutra_pattern = sutra_ref.replace(".", r"\|")

    # Find the sutra reference in the commentary
    # Look for pattern like `पूर्वकालैकसर्वजरत्पुराणनवकेवलाः समानाधिकरणेन` (पा.2|1|49) इति समासः ।
    pattern = rf"`([^`]+)`\s*\(पा\.{sutra_pattern}\)(.*?)(?:।|॥|$)"

    match = re.search(pattern, mn_text)

    if not match:
        return "", ""

    sutra_text = match.group(1).strip()
    following_text = match.group(2).strip()

    # The description includes the sutra and the explanation
    description = f"`{sutra_text}` (पा.{sutra_ref}) {following_text}"

    # Find the word being explained - look backwards from the sutra reference
    # Usually it appears before the sutra reference
    pre_text = mn_text[:match.start()]

    # Try to find the word being discussed
    # Look for patterns like "सर्वे च ते शैलाश्च सर्वशैलाः ।"
    # The word is often at the end of a sentence before the sutra
    word_pattern = r'([^\s।]+)\s*।\s*(?:`|$)'
    word_matches = list(re.finditer(word_pattern, pre_text))

    word = ""
    if word_matches:
        # Get the last substantial word before the sutra
        for wm in reversed(word_matches):
            potential_word = wm.group(1).strip()
            if len(potential_word) > 2 and not potential_word.startswith('('):
                word = potential_word
                break

    # Clean up the description - keep until next । or ॥
    desc_end = re.search(r'[।॥]', description[len(f"`{sutra_text}` (पा.{sutra_ref})"):])
    if desc_end:
        description = description[:len(f"`{sutra_text}` (पा.{sutra_ref})") + desc_end.end()]

    return word, description


def extract_commentary_context(mn_text, sutra_sentence):
    """
    Extract the full context around a sutra from the commentary.
    This includes finding the word being explained and the full description.
    """
    sutra_ref = sutra_sentence["sutra"]
    sentence = sutra_sentence["sentence"]

    # The sentence already contains the sutra reference, use it to find context
    # Extract the sutra text from the sentence (the part in backticks)
    sutra_text_match = re.search(r'`([^`]+)`', sentence)
    if not sutra_text_match:
        return "", sentence

    sutra_text = sutra_text_match.group(1)

    # Now find this in the commentary to get the full context
    # Look for the word being explained before this sutra
    escaped_sutra = re.escape(sutra_text)
    pattern = rf'([^\s।]+(?:\s+[^\s।]+)*?)\s*।?\s*`{escaped_sutra}`'

    match = re.search(pattern, mn_text)

    word = ""
    if match:
        # Extract the word - it's often the last compound word before the sutra
        preceding_text = match.group(1)
        # Look for compound words (Sanskrit compounds often end with specific patterns)
        word_candidates = preceding_text.split()
        if word_candidates:
            word = word_candidates[-1].strip('।')

    # The description is what we already have in sentence
    description = sentence

    return word, description


def process_extract_file(source_path, extract_path, output_path):
    """
    Process the extract file and fill in missing word and description fields.
    """
    print(f"Loading source file: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    print(f"Loading extract file: {extract_path}")
    with open(extract_path, 'r', encoding='utf-8') as f:
        extract_data = json.load(f)

    # Create a lookup dictionary for source verses by location
    source_lookup = {}
    for verse in source_data.get('data', []):
        loc = f"{verse['c']}.{verse['n']}"
        source_lookup[loc] = verse

    total_sutras = 0
    filled_sutras = 0

    # Process each verse in extract
    for verse in extract_data['data']:
        loc = verse['loc']
        print(f"\nProcessing verse {loc}")

        # Get the source verse
        source_verse = source_lookup.get(loc)
        if not source_verse:
            print(f"  Warning: No source verse found for {loc}")
            continue

        mn_text = source_verse.get('mn', '')
        if not mn_text:
            print(f"  Warning: No commentary found for {loc}")
            continue

        # Process each sutra sentence
        for sutra_sent in verse.get('sutra_sentences', []):
            total_sutras += 1
            sutra_ref = sutra_sent['sutra']

            print(f"  Processing sutra {sutra_ref}")

            # Extract word and description
            word, description = extract_commentary_context(mn_text, sutra_sent)

            # If we couldn't find the word, try a more detailed search
            if not word:
                word, description = find_sutra_context(mn_text, sutra_ref)

            # Update the sutra sentence
            if word or description:
                sutra_sent['word'] = word
                sutra_sent['description'] = description
                filled_sutras += 1
                print(f"    Found: word='{word}', desc='{description[:50]}...'")
            else:
                print(f"    Warning: Could not extract context for {sutra_ref}")

    # Save the enhanced extract
    print(f"\nSaving enhanced extract to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extract_data, f, ensure_ascii=False, indent=2)

    print(f"\nProcessing complete!")
    print(f"Total sutras: {total_sutras}")
    print(f"Filled sutras: {filled_sutras}")
    print(f"Success rate: {filled_sutras/total_sutras*100:.1f}%")


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.parent
    source_path = base_path / "texts" / "In" / "kumarasambhavam.json"
    extract_path = base_path / "texts" / "extract" / "kumarasambhavam_Extract.json"
    output_path = extract_path  # Save back to the same file

    process_extract_file(source_path, extract_path, output_path)
