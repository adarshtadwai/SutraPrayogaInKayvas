import json
import os
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

def aggregate_by_sutra(all_data):
    """Aggregate data by sutra number."""
    sutra_dict = defaultdict(list)

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

                # Create the metadata object
                metadata = {
                    "word": word,
                    "text": title,
                    "loc": loc,
                    "url": f"{base_link}{text}/{loc}",
                    "ref": sentence
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

    # Aggregate by sutra
    print("Aggregating by sutra number...")
    sutra_dict = aggregate_by_sutra(all_data)
    print(f"Found {len(sutra_dict)} unique sutras")

    # Sort by sutra number
    print("Sorting by sutra number...")
    sorted_sutra_dict = sort_sutra_dict(sutra_dict)

    # Create final output with title and comment
    output = {
        "title": "काव्यप्रयोगाः",
        "comment": f"This file contains {len(sorted_sutra_dict)} unique Panini sutras covered in the commentaries",
        "data": sorted_sutra_dict
    }

    # Write to output file
    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("Done!")

if __name__ == '__main__':
    main()
