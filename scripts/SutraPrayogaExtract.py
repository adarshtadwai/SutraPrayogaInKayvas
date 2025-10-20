#!/usr/bin/env python3
"""
Extract Panini Sutra Prayogas from Raghuvamsham JSON

This script extracts all entries from raghuvansham.json that contain references
to Panini sutras (pattern: *>.XdXdX) in the commentary field.

For each entry containing a sutra reference, it extracts:
- c (chapter number)
- n (verse number)
- v (verse text)
- The complete sentence containing the sutra reference (bounded by dandas)
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any
from SutraSentenceProcessor import SutraSentenceProcessor


def extract_sentences_with_sutra(text: str, sutra_pattern: str) -> List[str]:
    """
    Extract sentences containing Panini sutra references.

    A sentence is defined as text between dandas (। or ॥), but we need to be
    careful because sutra references themselves contain dandas (e.g., पा.1।2।3).

    Strategy: Find each sutra reference, then expand left and right to find
    the sentence boundaries. If another sutra reference is found within the
    sentence, look for natural break points (comma, space before backtick) to
    separate the content for each sutra.

    Args:
        text: The commentary text (mn field)
        sutra_pattern: Regex pattern to match Panini sutras

    Returns:
        List of sentences containing sutra references
    """
    sentences = []
    seen_sentences = set()  # To avoid duplicates

    # Find all sutra matches
    for match in re.finditer(sutra_pattern, text):
        sutra_start = match.start()
        sutra_end = match.end()

        # Find the sentence start: look backward for danda or start of text
        # Also check for comma as a potential start if there's another sutra before
        sentence_start = 0
        found_comma_start = False

        # First, check if there's a previous sutra reference nearby
        text_before_sutra = text[max(0, sutra_start - 200):sutra_start]
        prev_sutra_match = None
        for m in re.finditer(sutra_pattern, text_before_sutra):
            prev_sutra_match = m

        if prev_sutra_match:
            # There's a previous sutra nearby
            # Look for comma or space after the previous sutra
            prev_sutra_abs_pos = max(0, sutra_start - 200) + prev_sutra_match.end()

            # Search from after the previous sutra to before current sutra
            for i in range(prev_sutra_abs_pos, sutra_start):
                if text[i] == ',':
                    # Found a comma, this could be our start
                    # But only if this comma is between the two sutras
                    # Check if there's text between comma and current sutra
                    text_between = text[i+1:sutra_start].strip()
                    if text_between and not re.search(sutra_pattern, text_between):
                        sentence_start = i + 1  # Start after comma
                        found_comma_start = True
                        break

        if not found_comma_start:
            # No comma found, look for danda before the sutra
            for i in range(sutra_start - 1, -1, -1):
                if text[i] in '।॥':
                    # Found a danda - need to determine if it's a sentence boundary or part of Panini sutra
                    # Panini sutras look like: (पा.X।Y।Z) where dandas are INSIDE parentheses
                    # Other references look like: (अ.को.X|Y|Z) । where danda is OUTSIDE

                    # Check if this danda is inside a Panini sutra reference
                    # Count open/close parens from this danda back to last complete reference
                    text_segment = text[max(0, i-50):i+1]

                    # Find the last '(' before this danda
                    last_open_paren = text_segment.rfind('(')
                    if last_open_paren != -1:
                        # Check if there's a matching ')' between the '(' and this danda
                        text_between = text_segment[last_open_paren:]
                        if ')' in text_between:
                            # The parentheses are closed before this danda
                            # This is a sentence boundary (e.g., "(अ.को.2|7|12) ।")
                            sentence_start = i + 1
                            break
                        else:
                            # No closing paren yet, this danda is inside the reference (Panini sutra)
                            # Skip this danda and keep looking
                            continue
                    else:
                        # No open paren found nearby, this is a regular sentence boundary
                        sentence_start = i + 1
                        break

        # Find the sentence end: look forward for danda or end of text
        sentence_end = len(text)
        for i in range(sutra_end, len(text)):
            if text[i] in '।॥':
                # Look ahead to see if this is part of another sutra
                text_before = text[sutra_end:i]
                open_parens = text_before.count('(')
                close_parens = text_before.count(')')
                if open_parens <= close_parens:
                    # We're not inside a sutra reference
                    sentence_end = i + 1  # Include the danda
                    break

        # Check if there's another sutra reference after this one
        # If yes, look for a comma to cut the sentence
        next_sutra_match = re.search(sutra_pattern, text[sutra_end:sentence_end])
        if next_sutra_match:
            # Found another sutra in this sentence
            next_sutra_pos = sutra_end + next_sutra_match.start()

            # Look for a comma between current sutra and next sutra
            for i in range(sutra_end, next_sutra_pos):
                if text[i] == ',':
                    sentence_end = i
                    break

        # Extract sentence
        sentence = text[sentence_start:sentence_end].strip()

        # Add to results if not already seen
        if sentence and sentence not in seen_sentences:
            sentences.append(sentence)
            seen_sentences.add(sentence)

    return sentences


def extract_sutra_prayogas(json_file_path: str) -> List[Dict[str, Any]]:
    """
    Extract all entries containing Panini sutra references.

    Args:
        json_file_path: Path to the raghuvansham.json file

    Returns:
        List of dictionaries containing extracted information
    """
    # Regex pattern for Panini sutras
    # Matches both formats:
    # - (पा.X।X।X) - danda-separated (raghuvansham)
    # - (पा.X|X|X) - pipe-separated (kumarasambhavam)
    sutra_pattern = r'\(पा\.\d+[।|]\d+[।|]\d+\)'

    results = []

    # Load JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process each entry in the data array
    for entry in data.get('data', []):
        mn = entry.get('mn', '')

        # Check if the commentary contains a sutra reference
        if re.search(sutra_pattern, mn):
            # Extract sentences containing sutra references
            sentences = extract_sentences_with_sutra(mn, sutra_pattern)

            # Create result entry with loc field (c.n format)
            c = entry.get('c', '')
            n = entry.get('n', '')
            loc = f"{c}.{n}"

            result = {
                'loc': loc,
                'v': entry.get('v'),
                'sutra_sentences': sentences
            }

            results.append(result)

    return results


def main():
    """Main function to run the extraction."""
    # Check for command-line argument for input filename
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
    else:
        # Default to raghuvansham.json if no argument provided
        input_filename = 'raghuvansham.json'

    # Input and output paths
    input_file = Path(__file__).parent.parent / 'texts' / 'In' / input_filename

    # Verify input file exists
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        print(f"Usage: python3 {Path(__file__).name} [input_filename.json]")
        sys.exit(1)

    # Generate output filename based on input filename: input_Extract.json
    input_basename = input_file.stem  # e.g., 'raghuvansham' or 'kumarasambhavam'
    output_filename = f"{input_basename}_Extract.json"
    output_file = Path(__file__).parent.parent / 'texts' / 'extract' / output_filename

    print(f"Reading from: {input_file}")

    # Phase 1: Extract sutra prayogas
    print("\n[Phase 1] Extracting sutra sentences...")
    results = extract_sutra_prayogas(str(input_file))
    print(f"Found {len(results)} entries with Panini sutra references")

    # Phase 2: Enhance with structured sutra data
    print("\n[Phase 2] Processing and cleaning sutra sentences...")
    processor = SutraSentenceProcessor()
    enhanced_results = processor.enhance_data(results)

    # Count total processed sentences and unique sutras
    total_sentences = sum(len(entry['sutra_sentences']) for entry in enhanced_results)
    print(f"Processed {total_sentences} sutra sentences")

    # Count unique sutras
    unique_sutras = set()
    for entry in enhanced_results:
        for sent_obj in entry['sutra_sentences']:
            unique_sutras.add(sent_obj['sutra'])

    print(f"Found {len(unique_sutras)} unique Panini sutras")

    # Create output structure with metadata
    # Read the original file to get the title
    with open(input_file, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    # Text name is derived from input filename (e.g., 'raghuvansham' from raghuvansham.json)
    text_name = input_basename
    title = source_data.get('title', '')

    output_data = {
        "text": text_name,
        "title": title,
        "base_link": "https://sanskritsahitya.org/",
        "comment": f"This file contains {len(unique_sutras)} unique Panini sutras referenced in the commentary",
        "data": enhanced_results
    }

    # Save results to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Print a few examples
    print("\n" + "="*80)
    print("Sample results (Phase 2 Enhanced):")
    print("="*80)

    for i, result in enumerate(enhanced_results[:3], 1):
        print(f"\n{i}. Location {result['loc']}")
        print(f"   Verse: {result['v'][:50]}...")
        print(f"   Sutra sentences found: {len(result['sutra_sentences'])}")
        for j, entry in enumerate(result['sutra_sentences'][:2], 1):
            # Show structured output
            print(f"      {j}. Sutra: {entry['sutra']}")
            # Show only first 80 characters of sentence
            sentence_preview = entry['sentence'][:80] + "..." if len(entry['sentence']) > 80 else entry['sentence']
            print(f"         Sentence: {sentence_preview}")


if __name__ == '__main__':
    main()
