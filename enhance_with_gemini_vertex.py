#!/usr/bin/env python3
"""
Enhance JSON with word and description fields using Gemini via Vertex AI.
Uses Vertex AI authentication (gcloud auth) instead of API keys.
"""

import json
import os
import re
import sys
import time
from pathlib import Path
import vertexai
from vertexai.generative_models import GenerativeModel

class SutraEnhancerGemini:
    """Enhance sutra entries using Gemini via Vertex AI."""

    def __init__(self, project_id=None, location="us-central1", model="gemini-2.0-flash-exp", delay=4):
        """
        Initialize with Vertex AI.

        Args:
            project_id: Google Cloud project ID
            location: Vertex AI location
            model: Gemini model to use (gemini-1.5-pro, gemini-1.5-flash, etc.)
            delay: Delay in seconds between API calls to avoid rate limits
        """
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")

        self.location = location
        self.model_name = model
        self.delay = delay

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)

        # Initialize model
        self.model = GenerativeModel(model)

        print(f"Using Gemini via Vertex AI")
        print(f"Project: {self.project_id}")
        print(f"Location: {self.location}")
        print(f"Model: {model}")
        print(f"Delay between calls: {delay}s")

    def find_word_and_description(self, sutra, sentence, verse_loc, commentary, verse_text):
        """
        Use Gemini to analyze commentary and extract word + description.

        Args:
            sutra: Sutra number (e.g., "2.1.49")
            sentence: Sentence from extract file
            verse_loc: Verse location
            commentary: Full Mallinatha commentary
            verse_text: The actual verse text

        Returns:
            Tuple of (word, description)
        """
        prompt = f"""You are analyzing Sanskrit grammatical commentary by Mallinatha.

Your task: Extract TWO pieces of information about Panini sutra {sutra}:

1. **WORD**: The EXACT Sanskrit word from the verse that this sutra explains
2. **DESCRIPTION**: The exact portion of Mallinatha's commentary where this sutra is discussed

VERSE TEXT (the actual sloka):
{verse_text}

Context:
- Verse Location: {verse_loc}
- Sutra Number: {sutra}
- Sentence mentioning sutra: {sentence}

Mallinatha's Commentary:
{commentary}

CRITICAL INSTRUCTIONS FOR WORD EXTRACTION:
1. Read the commentary to understand WHICH word the sutra is explaining
2. Then SEARCH for that word IN THE VERSE TEXT above
3. Extract the EXACT form as it appears in the verse (with same case ending, compound form, etc.)
4. The word MUST be a substring of the verse text - verify by checking if it exists in the verse
5. DO NOT extract from commentary - ONLY from verse text
6. DO NOT give dictionary form or root form - give the EXACT inflected form from verse

EXAMPLES:
- If verse has "सूर्यप्रभवो" and commentary discusses "प्रभवः", extract "सूर्यप्रभवो" or "प्रभवो" (whichever appears in verse)
- If verse has "पितरौ" and commentary discusses "पितरौ", extract "पितरौ"
- If verse has "पार्वतीपरमेश्वरौ" and commentary discusses "पार्वती", extract "पार्वती" (it's part of compound in verse)

FOR DESCRIPTION:
- Extract ONLY the portion of Mallinatha's commentary that discusses THIS specific sutra
- Look for the sutra reference: (पा.{sutra.replace('.', '|')}) or (पा.{sutra.replace('.', '।')})
- Extract the sentence containing the sutra reference (from । to ।)
- Include ONLY the words/explanation related to this sutra, not the entire commentary

Return ONLY valid JSON, no markdown, no extra text:
{{
  "word": "exact_word_from_verse_text",
  "description": "portion_of_commentary_with_sutra_reference"
}}"""

        try:
            # Add delay to avoid rate limits
            if self.delay > 0:
                time.sleep(self.delay)

            response = self.model.generate_content(prompt)
            response_text = response.text

            # Extract JSON from response
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*$', '', response_text)

            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group(0))
                return result.get("word", ""), result.get("description", "")
            else:
                print(f"⚠️  Could not parse JSON for sutra {sutra}")
                return "", ""

        except Exception as e:
            # Check if it's a rate limit error - retry with exponential backoff
            if "429" in str(e) or "Quota exceeded" in str(e):
                retry_delays = [30, 60, 120, 240]  # Exponential backoff: 30s, 1m, 2m, 4m

                for attempt, retry_delay in enumerate(retry_delays, 1):
                    print(f"⚠️  Rate limit hit for sutra {sutra}, retry {attempt}/{len(retry_delays)} after {retry_delay}s...")
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
                            desc = result.get("description", "")
                            if word and desc:  # Only return if both are filled
                                print(f"   ✓ Retry succeeded!")
                                return word, desc
                    except Exception as retry_error:
                        if attempt < len(retry_delays):
                            print(f"   Retry {attempt} failed: {str(retry_error)[:50]}")
                        continue

                # All retries exhausted
                print(f"❌ All retries exhausted for sutra {sutra}")
                return "", ""

            print(f"❌ Error for sutra {sutra}: {str(e)[:100]}")
            return "", ""

    def enhance_verse(self, verse_entry, commentary_map, skip_filled=True):
        """Enhance all sutras in a verse."""
        loc = verse_entry['loc']
        commentary = commentary_map.get(loc, '')
        verse_text = verse_entry.get('v', '')

        if not commentary:
            print(f"⚠️  No commentary for verse {loc}")
            return verse_entry

        for i, sutra_entry in enumerate(verse_entry.get('sutra_sentences', [])):
            sutra = sutra_entry['sutra']
            sentence = sutra_entry['sentence']

            # Skip if already filled (for resume capability)
            if skip_filled and sutra_entry.get('word') and sutra_entry.get('description'):
                print(f"   Sutra {sutra}... ⏭️  (already filled)")
                continue

            print(f"   Processing sutra {sutra}...", end='', flush=True)

            word, description = self.find_word_and_description(
                sutra, sentence, loc, commentary, verse_text
            )

            sutra_entry['word'] = word
            sutra_entry['description'] = description

            if word:
                print(f" ✓ {word[:30]}")
            else:
                print(" ✗ (no word)")

        return verse_entry

    def enhance_file(self, extract_file, source_file, output_file, save_interval=10):
        """Enhance entire extract file with periodic saving."""
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

        total_verses = len(extract_data.get('data', []))
        total_sutras = sum(len(v.get('sutra_sentences', [])) for v in extract_data['data'])

        # Count already filled sutras for resume
        filled_sutras = sum(1 for v in extract_data['data']
                          for s in v.get('sutra_sentences', [])
                          if s.get('word') and s.get('description'))

        print(f"Found {total_verses} verses with {total_sutras} sutra references")
        print(f"Already filled: {filled_sutras}/{total_sutras} sutras ({filled_sutras/total_sutras*100:.1f}%)")
        print(f"Will save progress every {save_interval} verses\n")
        print("Processing...\n")

        for i, verse_entry in enumerate(extract_data['data'], 1):
            print(f"{i}/{total_verses}: Verse {verse_entry['loc']}")
            self.enhance_verse(verse_entry, commentary_map, skip_filled=True)

            # Periodic save every N verses
            if i % save_interval == 0:
                print(f"\n💾 Auto-saving progress at verse {i}/{total_verses}...")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(extract_data, f, ensure_ascii=False, indent=2)
                print(f"✅ Progress saved!\n")

        # Update comment
        if "(Enhanced with Gemini via Vertex AI)" not in extract_data.get('comment', ''):
            extract_data['comment'] = extract_data.get('comment', '') + " (Enhanced with Gemini via Vertex AI)"

        print(f"\n💾 Saving final version to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extract_data, f, ensure_ascii=False, indent=2)

        print("✅ Complete!")


def main():
    """Main function."""
    extract_filename = sys.argv[1] if len(sys.argv) > 1 else 'kumarasambhavam_Extract.json'
    delay = int(sys.argv[2]) if len(sys.argv) > 2 else 30  # Default to 30 seconds

    project_root = Path(__file__).parent
    extract_file = project_root / 'texts' / 'extract' / extract_filename

    # Derive source filename
    if 'raghuvansham' in extract_filename.lower():
        # Raghuvansham files
        source_basename = 'raghuvansham.json'
    elif 'kumarasambhavam' in extract_filename.lower():
        # Kumarasambhavam files
        source_basename = 'kumarasambhavam.json'
    elif '_Extract_test.json' in extract_filename:
        source_basename = extract_filename.replace('_Extract_test.json', '.json')
    elif '_Extract.json' in extract_filename:
        source_basename = extract_filename.replace('_Extract.json', '.json')
    else:
        # Default fallback
        source_basename = 'kumarasambhavam.json'

    source_file = project_root / 'texts' / 'In' / source_basename
    output_file = extract_file

    # Verify files
    if not extract_file.exists():
        print(f"❌ Extract file not found: {extract_file}")
        sys.exit(1)

    if not source_file.exists():
        print(f"❌ Source file not found: {source_file}")
        sys.exit(1)

    # Check Google Cloud project
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        sys.exit(1)

    print("="*80)
    print("Sutra Enhancement Tool (Gemini via Vertex AI)")
    print("="*80)
    print(f"Extract file: {extract_filename}")
    print("="*80 + "\n")

    # Create enhancer
    enhancer = SutraEnhancerGemini(delay=delay)

    # Iteration loop: keep running until all sutras are filled
    iteration = 1
    while True:
        print(f"\n{'='*80}")
        print(f"ITERATION {iteration}")
        print(f"{'='*80}\n")

        # Run enhancement
        enhancer.enhance_file(extract_file, source_file, output_file)

        # Check if all sutras are filled
        with open(extract_file, 'r', encoding='utf-8') as f:
            extract_data = json.load(f)

        total_sutras = sum(len(v.get('sutra_sentences', [])) for v in extract_data['data'])
        filled_sutras = sum(1 for v in extract_data['data']
                          for s in v.get('sutra_sentences', [])
                          if s.get('word') and s.get('description'))
        empty_sutras = total_sutras - filled_sutras

        print(f"\n{'='*80}")
        print(f"ITERATION {iteration} COMPLETE")
        print(f"Filled: {filled_sutras}/{total_sutras} ({filled_sutras/total_sutras*100:.1f}%)")
        print(f"Empty: {empty_sutras}/{total_sutras} ({empty_sutras/total_sutras*100:.1f}%)")
        print(f"{'='*80}\n")

        if empty_sutras == 0:
            print("✅ ALL SUTRAS SUCCESSFULLY FILLED!")
            break
        else:
            print(f"⚠️  {empty_sutras} sutras still empty. Starting iteration {iteration + 1}...\n")
            iteration += 1
            time.sleep(60)  # Wait 1 minute before next iteration


if __name__ == '__main__':
    main()
