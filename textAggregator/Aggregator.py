import json
import os
import re
from pathlib import Path
from collections import defaultdict

def read_extract_files(extract_dir):
    """Read all JSON files from the extract directory."""
    extract_path = Path(extract_dir)
    json_files = list(extract_path.glob("*.json"))

    all_data = []
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
            all_data.append(file_data)

    return all_data

def clean_ai_ref_description(description):
    """
    Clean AI_ref description by removing Panini sutra references and adjusting spacing.

    Removes patterns like:
    - (पा.1।1।33)
    - (पा.1|1|33)

    Args:
        description: The description string to clean

    Returns:
        Cleaned description string
    """
    if not description:
        return description

    # Pattern to match Panini sutra references: (पा.X।X।X) or (पा.X|X|X)
    sutra_pattern = r'\(पा\.\d+[।|]\d+[।|]\d+\)'

    # Remove the sutra references
    cleaned = re.sub(sutra_pattern, '', description)

    # Clean up extra spaces (multiple spaces to single space)
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Remove leading/trailing spaces
    cleaned = cleaned.strip()

    # Clean up spaces before punctuation
    cleaned = re.sub(r'\s+([।॥,])', r'\1', cleaned)

    return cleaned


def build_ai_ref_lookup(all_data):
    """
    Build a lookup map for AI_ref and pada data from the same extract files.
    Extract files already have description and pada fields from enhancement.

    Returns a dict with key: (text_name, loc, sutra) -> value: (description, pada) tuple
    """
    ai_ref_lookup = {}

    for file_data in all_data:
        text_name = file_data.get('text', '')

        for verse in file_data.get('data', []):
            loc = verse.get('loc', '')

            for sutra_sentence in verse.get('sutra_sentences', []):
                sutra = sutra_sentence.get('sutra', '')
                description = sutra_sentence.get('description', '')
                pada = sutra_sentence.get('pada', '')

                # Only add if we have description (AI-enhanced entries)
                if description:
                    # Clean the description
                    cleaned_description = clean_ai_ref_description(description)
                    key = (text_name, loc, sutra)
                    ai_ref_lookup[key] = (cleaned_description, pada)

    print(f"Built AI_ref lookup map with {len(ai_ref_lookup)} enhanced entries")
    return ai_ref_lookup

def aggregate_by_sutra(all_data, enhanced_lookup=None):
    """
    Aggregate data by sutra number.

    Args:
        all_data: List of file data from extract files
        enhanced_lookup: Optional dict mapping (text_name, loc, sutra) to AI_ref data

    Returns:
        Dictionary with sutra numbers as keys and list of metadata as values
    """
    sutra_dict = defaultdict(list)
    enhanced_lookup = enhanced_lookup or {}

    for file_data in all_data:
        text = file_data.get('text', '')
        title = file_data.get('title', '')
        base_link = file_data.get('base_link', '')
        data_entries = file_data.get('data', [])

        for entry in data_entries:
            loc = entry.get('loc', '')
            sutra_sentences = entry.get('sutra_sentences', [])

            for sutra_sentence in sutra_sentences:
                sutra_number = sutra_sentence.get('sutra', '')
                word = sutra_sentence.get('word', '')
                sentence = sutra_sentence.get('sentence', '')
                pada = sutra_sentence.get('pada', '')

                # Determine AI_ref and pada values
                lookup_key = (text, loc, sutra_number)
                if lookup_key in enhanced_lookup:
                    ai_ref_value, enhanced_pada = enhanced_lookup[lookup_key]
                    # Use enhanced pada if available, otherwise use the one from extract
                    pada_value = enhanced_pada if enhanced_pada else pada
                else:
                    # If no AI_ref available, use the sentence value
                    ai_ref_value = sentence
                    pada_value = pada

                # Create the metadata object (with pada before AI_ref)
                metadata = {
                    "word": word,
                    "text": title,
                    "loc": loc,
                    "url": f"{base_link}{text}/{loc}",
                    "pada": pada_value,
                    "AI_ref": ai_ref_value
                }

                sutra_dict[sutra_number].append(metadata)

    return sutra_dict

def sort_sutra_dict(sutra_dict):
    """Sort the dictionary by sutra number."""
    def sutra_key(sutra):
        """Convert sutra number to sortable tuple (e.g., '1.2.70' -> (1, 2, 70))."""
        try:
            parts = sutra.split('.')
            return tuple(int(p) for p in parts)
        except (ValueError, AttributeError):
            # If conversion fails, sort it at the end
            return (float('inf'),)

    sorted_items = sorted(sutra_dict.items(), key=lambda x: sutra_key(x[0]))
    return dict(sorted_items)

def main():
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    extract_dir = project_root / 'texts' / 'extract'
    output_file = script_dir / 'KavyaPrayogas.json'

    # Read all extract files
    print(f"Reading files from {extract_dir}...")
    all_data = read_extract_files(extract_dir)
    print(f"Found {len(all_data)} files")

    # Build AI_ref lookup from the extract files (they have descriptions)
    print("\nBuilding AI_ref lookup from extract files...")
    ai_ref_lookup = build_ai_ref_lookup(all_data)

    # Aggregate by sutra with AI_ref data
    print("\nAggregating by sutra number...")
    sutra_dict = aggregate_by_sutra(all_data, ai_ref_lookup)
    print(f"Found {len(sutra_dict)} unique sutras")

    # Count how many entries have AI_ref
    total_entries = sum(len(entries) for entries in sutra_dict.values())
    ai_ref_count = sum(1 for entries in sutra_dict.values()
                       for entry in entries if entry.get('AI_ref') is not None)
    print(f"Total entries: {total_entries}")
    print(f"Entries with AI_ref: {ai_ref_count}")
    print(f"Entries with AI_ref = null: {total_entries - ai_ref_count}")

    # Sort by sutra number
    print("\nSorting by sutra number...")
    sorted_sutra_dict = sort_sutra_dict(sutra_dict)

    # Create final output with title and comment
    output = {
        "title": "काव्यप्रयोगाः",
        "comment": f"This file contains {len(sorted_sutra_dict)} unique Panini sutras covered in the commentaries",
        "data": sorted_sutra_dict
    }

    # Write to output file
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("Done!")

if __name__ == '__main__':
    main()
