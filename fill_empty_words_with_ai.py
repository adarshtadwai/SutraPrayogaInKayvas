#!/usr/bin/env python3
"""
Fill only the empty word fields using Gemini AI.
Skips entries that already have word filled.
"""

import json
import os
import re
import sys
import time
from pathlib import Path
import vertexai
from vertexai.generative_models import GenerativeModel


class WordFiller:
    """Fill empty word fields using Gemini via Vertex AI."""

    def __init__(self, project_id=None, location="us-central1", model="gemini-2.0-flash-exp", delay=30):
        """Initialize with Vertex AI."""
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")

        self.location = location
        self.model_name = model
        self.delay = delay

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(model)

        print(f"Using Gemini via Vertex AI")
        print(f"Project: {self.project_id}")
        print(f"Model: {model}")
        print(f"Delay: {delay}s\n")

    def find_word(self, sutra, sentence, verse_loc, commentary, verse_text):
        """Use Gemini to find the word that the sutra explains."""

        prompt = f"""You are analyzing Sanskrit grammatical commentary by Mallinatha.

Your task: Find the EXACT Sanskrit word from the verse that Panini sutra {sutra} is explaining.

VERSE TEXT (the actual sloka):
{verse_text}

Context:
- Verse Location: {verse_loc}
- Sutra Number: {sutra}
- Sentence mentioning sutra: {sentence}

Mallinatha's Commentary:
{commentary}

CRITICAL INSTRUCTIONS:
1. Read the commentary to understand WHICH word the sutra is explaining
2. Then SEARCH for that word IN THE VERSE TEXT above
3. Extract the EXACT form as it appears in the verse (with same case ending, compound form, etc.)
4. The word MUST be a substring of the verse text - verify by checking if it exists in the verse
5. DO NOT extract from commentary - ONLY from verse text
6. DO NOT give dictionary form or root form - give the EXACT inflected form from verse

Return ONLY valid JSON with the word:
{{
  "word": "exact_word_from_verse_text"
}}"""

        try:
            if self.delay > 0:
                time.sleep(self.delay)

            response = self.model.generate_content(prompt)
            response_text = response.text

            # Extract JSON
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*$', '', response_text)
            json_match = re.search(r'\{[\s\S]*\}', response_text)

            if json_match:
                result = json.loads(json_match.group(0))
                return result.get("word", "")
            else:
                return ""

        except Exception as e:
            # Retry with exponential backoff
            if "429" in str(e) or "Quota exceeded" in str(e):
                retry_delays = [30, 60, 120]

                for attempt, retry_delay in enumerate(retry_delays, 1):
                    print(f"  ⚠️  Rate limit, retry {attempt}/{len(retry_delays)} after {retry_delay}s...")
                    time.sleep(retry_delay)

                    try:
                        response = self.model.generate_content(prompt)
                        response_text = response.text
                        response_text = re.sub(r'```json\s*', '', response_text)
                        response_text = re.sub(r'```\s*$', '', response_text)
                        json_match = re.search(r'\{[\s\S]*\}', response_text)

                        if json_match:
                            result = json.loads(json_match.group(0))
                            word = result.get("word", "")
                            if word:
                                print(f"  ✓ Retry succeeded!")
                                return word
                    except:
                        continue

            print(f"  ❌ Error: {str(e)[:80]}")
            return ""

    def fill_empty_words(self, extract_file, source_file):
        """Fill empty word fields in extract file."""

        print(f"Loading source commentary: {source_file}")
        with open(source_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)

        # Create commentary map
        commentary_map = {}
        for entry in source_data.get('data', []):
            c = entry.get('c', '')
            n = entry.get('n', '')
            loc = f"{c}.{n}"
            commentary_map[loc] = entry.get('mn', '')

        print(f"Loaded commentary for {len(commentary_map)} verses\n")

        print(f"Loading extract file: {extract_file}")
        with open(extract_file, 'r', encoding='utf-8') as f:
            extract_data = json.load(f)

        # Count empty words
        empty_words = sum(1 for v in extract_data['data']
                         for s in v.get('sutra_sentences', [])
                         if not s.get('word'))

        print(f"Found {empty_words} entries with empty word field")
        print("Processing...\n")

        filled = 0
        failed = 0

        for verse_entry in extract_data['data']:
            loc = verse_entry['loc']
            verse_text = verse_entry.get('v', '')
            commentary = commentary_map.get(loc, '')

            for sutra_entry in verse_entry.get('sutra_sentences', []):
                # Skip if word already filled
                if sutra_entry.get('word'):
                    continue

                sutra = sutra_entry['sutra']
                sentence = sutra_entry['sentence']

                print(f"Verse {loc}, Sutra {sutra}...", end='', flush=True)

                word = self.find_word(sutra, sentence, loc, commentary, verse_text)

                if word:
                    sutra_entry['word'] = word
                    filled += 1
                    print(f" ✓ {word}")
                else:
                    failed += 1
                    print(f" ✗ (failed)")

        # Save
        print(f"\nSaving to: {extract_file}")
        with open(extract_file, 'w', encoding='utf-8') as f:
            json.dump(extract_data, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*80}")
        print(f"Results: Filled {filled}, Failed {failed}")
        print('='*80)


def main():
    """Main function."""
    project_root = Path(__file__).parent

    # Check environment
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        sys.exit(1)

    filler = WordFiller(delay=30)

    # Process both files
    files = [
        ('kumarasambhavam_Extract.json', 'kumarasambhavam.json'),
        ('raghuvansham_Extract.json', 'raghuvansham.json')
    ]

    for extract_name, source_name in files:
        extract_file = project_root / 'texts' / 'extract' / extract_name
        source_file = project_root / 'texts' / 'In' / source_name

        if extract_file.exists() and source_file.exists():
            print(f"\n{'='*80}")
            print(f"Processing: {extract_name}")
            print('='*80 + "\n")
            filler.fill_empty_words(extract_file, source_file)
        else:
            print(f"⚠️  Files not found for {extract_name}")


if __name__ == '__main__':
    main()
