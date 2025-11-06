#!/usr/bin/env python3
"""
Enhance JSON Files with Word and Description Fields

This script enhances the extracted JSON files by:
1. Finding the word referenced by each sutra from the commentary
2. Adding a description field with relevant commentary text

Uses Vertex AI (Google Cloud) with Gemini models for Sanskrit analysis.

Usage:
    python3 EnhanceJsonWithWordsAndDescriptions.py [input_filename.json] [--model model_name]

Requirements:
    - Google Cloud authentication configured (gcloud auth)
    - GOOGLE_CLOUD_PROJECT environment variable set
    - Input file should be in texts/extract/ directory
    - Source commentary file should be in texts/In/ directory
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai


class SutraEnhancer:
    """Enhance sutra entries with word and description fields using Gemini via Vertex AI."""

    def __init__(self, project_id: Optional[str] = None,
                 model: str = "gemini-1.5-pro"):
        """
        Initialize the enhancer with Vertex AI Gemini.

        Args:
            project_id: Google Cloud project ID. If None, reads from GOOGLE_CLOUD_PROJECT env var.
            model: Gemini model to use. Options:
                   - "gemini-1.5-pro" (default, best for complex Sanskrit analysis)
                   - "gemini-1.5-flash" (faster, good quality)
                   - "gemini-pro" (older, still capable)
        """
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")

        self.model_name = model

        # Configure Gemini API
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))

        # Initialize model
        self.model = genai.GenerativeModel(model)

        print(f"Using Gemini model: {model}")
        print(f"Project: {self.project_id}")

        # Pattern to match Panini sutra references in commentary
        # Supports both formats: (पा.X।X।X) and (पा.X|X|X)
        self.sutra_pattern = r'\(पा\.(\d+)[।|](\d+)[।|](\d+)\)'

    def find_word_and_description(
        self,
        sutra: str,
        sentence: str,
        verse_loc: str,
        commentary: str
    ) -> Tuple[str, str]:
        """
        Use Gemini to find the word referenced by the sutra and extract description.

        Args:
            sutra: Sutra number in format "X.X.X"
            sentence: The sentence containing the sutra reference
            verse_loc: Location of the verse (e.g., "1.2")
            commentary: Full commentary text for the verse

        Returns:
            Tuple of (word, description)
        """
        prompt = f"""You are analyzing Sanskrit grammatical commentary. You need to:

1. Identify the WORD that the Panini sutra {sutra} is describing/explaining in the commentary
2. Extract the relevant DESCRIPTION - the specific lines in the commentary where this sutra is being discussed

Context:
- Verse Location: {verse_loc}
- Sutra Number: {sutra}
- Sentence containing sutra: {sentence}

Full Commentary (mn field):
{commentary}

Instructions:
- The "word" should be the specific Sanskrit word from the verse that this sutra is explaining (often mentioned near the sutra reference)
- The "description" should be the portion of the commentary that discusses this sutra (usually starts before the sutra reference and ends at a । or ॥)
- Both should be in Sanskrit (Devanagari script)
- If the word is not clearly identifiable, return an empty string for word
- The description should include context about what the sutra is explaining

Return your answer ONLY in the following JSON format (no markdown, no extra text):
{{
  "word": "sanskrit_word_here",
  "description": "relevant_commentary_text_here"
}}"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text

            # Extract JSON from response
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*$', '', response_text)

            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group(0))
                return result.get("word", ""), result.get("description", "")
            else:
                print(f"Warning: Could not parse JSON from Gemini response for sutra {sutra}")
                print(f"Response: {response_text[:200]}")
                return "", ""

        except Exception as e:
            print(f"Error calling Gemini API for sutra {sutra}: {e}")
            return "", ""

    def enhance_sutra_entry(
        self,
        sutra_entry: Dict,
        verse_loc: str,
        commentary: str
    ) -> Dict:
        """
        Enhance a single sutra entry with word and description.

        Args:
            sutra_entry: Dictionary with sutra, word (empty), and sentence
            verse_loc: Location of the verse
            commentary: Full commentary text

        Returns:
            Enhanced sutra entry
        """
        sutra = sutra_entry["sutra"]
        sentence = sutra_entry["sentence"]

        # Find word and description using Gemini
        word, description = self.find_word_and_description(
            sutra, sentence, verse_loc, commentary
        )

        # Update the entry
        enhanced = sutra_entry.copy()
        enhanced["word"] = word
        enhanced["description"] = description

        return enhanced

    def enhance_verse_entry(
        self,
        verse_entry: Dict,
        source_commentary_map: Dict[str, str]
    ) -> Dict:
        """
        Enhance all sutra entries for a single verse.

        Args:
            verse_entry: Dictionary with loc, v, and sutra_sentences
            source_commentary_map: Map of loc to full commentary (mn field)

        Returns:
            Enhanced verse entry
        """
        loc = verse_entry["loc"]
        commentary = source_commentary_map.get(loc, "")

        if not commentary:
            print(f"Warning: No commentary found for verse {loc}")
            return verse_entry

        enhanced = verse_entry.copy()
        enhanced_sutras = []

        for i, sutra_entry in enumerate(verse_entry.get("sutra_sentences", []), 1):
            print(f"  Processing sutra {i}/{len(verse_entry['sutra_sentences'])}: {sutra_entry['sutra']}")
            enhanced_sutra = self.enhance_sutra_entry(sutra_entry, loc, commentary)
            enhanced_sutras.append(enhanced_sutra)

        enhanced["sutra_sentences"] = enhanced_sutras
        return enhanced

    def load_source_commentary(self, source_file: Path) -> Dict[str, str]:
        """
        Load source commentary file and create a map of loc to mn field.

        Args:
            source_file: Path to source JSON file in texts/In/

        Returns:
            Dictionary mapping loc (e.g., "1.2") to commentary (mn field)
        """
        commentary_map = {}

        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for entry in data.get('data', []):
            c = entry.get('c', '')
            n = entry.get('n', '')
            loc = f"{c}.{n}"
            mn = entry.get('mn', '')
            commentary_map[loc] = mn

        return commentary_map

    def enhance_file(
        self,
        extract_file: Path,
        source_file: Path,
        output_file: Path
    ) -> None:
        """
        Enhance an entire extract JSON file.

        Args:
            extract_file: Path to extracted JSON file (e.g., kumarasambhavam_Extract.json)
            source_file: Path to source JSON file (e.g., kumarasambhavam.json)
            output_file: Path where enhanced JSON will be saved
        """
        print(f"Loading source commentary from: {source_file}")
        commentary_map = self.load_source_commentary(source_file)
        print(f"Loaded commentary for {len(commentary_map)} verses")

        print(f"\nLoading extract file from: {extract_file}")
        with open(extract_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"Found {len(data.get('data', []))} verses to enhance")

        enhanced_data = data.copy()
        enhanced_verses = []

        for i, verse_entry in enumerate(data.get('data', []), 1):
            print(f"\nEnhancing verse {i}/{len(data['data'])}: {verse_entry['loc']}")
            enhanced_verse = self.enhance_verse_entry(verse_entry, commentary_map)
            enhanced_verses.append(enhanced_verse)

        enhanced_data['data'] = enhanced_verses

        # Update comment to reflect enhancement
        enhanced_data['comment'] = data.get('comment', '') + " (Enhanced with word and description fields using Gemini)"

        print(f"\nSaving enhanced data to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)

        print(f"\nEnhancement complete!")


def main():
    """Main function to run the enhancement."""
    # Parse command-line arguments
    # Usage: python3 script.py [filename] [--model model_name]
    extract_filename = 'kumarasambhavam_Extract.json'  # Default
    model_name = "gemini-1.5-pro"  # Default model

    # Simple argument parsing
    if len(sys.argv) > 1:
        extract_filename = sys.argv[1]

    if len(sys.argv) > 2 and sys.argv[2] == '--model':
        if len(sys.argv) > 3:
            model_name = sys.argv[3]
        else:
            print("Error: --model requires a model name")
            print("Available models:")
            print("  - gemini-1.5-pro (default, best for complex analysis)")
            print("  - gemini-1.5-flash (faster, good quality)")
            print("  - gemini-pro (older version)")
            sys.exit(1)

    # Paths
    project_root = Path(__file__).parent.parent
    extract_file = project_root / 'texts' / 'extract' / extract_filename

    # Derive source filename from extract filename
    # e.g., kumarasambhavam_Extract.json -> kumarasambhavam.json
    # Also handle test files: kumarasambhavam_Extract_test.json -> kumarasambhavam.json
    if '_Extract_test.json' in extract_filename:
        source_basename = extract_filename.replace('_Extract_test.json', '.json')
    elif '_Extract.json' in extract_filename:
        source_basename = extract_filename.replace('_Extract.json', '.json')
    else:
        source_basename = extract_filename
    source_file = project_root / 'texts' / 'In' / source_basename

    # Output file (same as input for now, we'll update in place)
    output_file = extract_file

    # Verify files exist
    if not extract_file.exists():
        print(f"Error: Extract file not found: {extract_file}")
        print(f"Usage: python3 {Path(__file__).name} [extract_filename.json] [--model model_name]")
        sys.exit(1)

    if not source_file.exists():
        print(f"Error: Source file not found: {source_file}")
        sys.exit(1)

    # Check for Google Cloud/API key configuration
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        print("Error: GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set")
        print("Please set it with: export GEMINI_API_KEY=your-api-key")
        sys.exit(1)

    print("="*80)
    print("Sutra Enhancement Tool (Gemini)")
    print("="*80)
    print(f"Model: {model_name}")
    print(f"Extract file: {extract_filename}")
    print("="*80)

    # Create enhancer and process
    enhancer = SutraEnhancer(model=model_name)
    enhancer.enhance_file(extract_file, source_file, output_file)


if __name__ == '__main__':
    main()
