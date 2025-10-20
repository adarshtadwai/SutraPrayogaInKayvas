#!/usr/bin/env python3
"""
Sutra Sentence Processor for Sutra Prayoga Extraction

This module enhances the extracted sutra sentences by:
1. Parsing out the sutra reference (e.g., पा.3।1।124 → 3.1.124)
2. Cleaning the sentence text (removing sutra refs, backticks, fixing dandas)
3. Structuring each sentence as {sutra: "3.1.124", sentence: "cleaned text"}
"""

import re
from typing import List, Dict, Optional


class SutraSentenceProcessor:
    """Process and enhance sutra sentences extracted in Phase 1."""

    def __init__(self):
        # Pattern to match Panini sutra references
        # Supports both danda (।) and pipe (|) separators
        # - (पा.X।X।X) - danda format (raghuvansham)
        # - (पा.X|X|X) - pipe format (kumarasambhavam)
        self.sutra_pattern = r'\(पा\.(\d+)[।|](\d+)[।|](\d+)\)'
        # Pattern to match backticks (used around sutra names)
        self.backtick_pattern = r'`([^`]*)`'

    def extract_sutra_reference(self, text: str) -> Optional[str]:
        """
        Extract sutra reference from text and convert to format X.X.X

        Args:
            text: Text containing sutra reference like (पा.3।1।124)

        Returns:
            Sutra in format "3.1.124" or None if not found
        """
        match = re.search(self.sutra_pattern, text)
        if match:
            # Convert (पा.3।1।124) to "3.1.124"
            return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
        return None

    def clean_sentence(self, text: str, original_sentence: str) -> str:
        """
        Clean sentence by removing sutra references and fixing dandas.
        Backticks are now kept as they mark sutra names.

        Args:
            text: Sentence text to clean
            original_sentence: Original sentence for context

        Returns:
            Cleaned sentence text
        """
        cleaned = text

        # Step 1: Remove the (पा.X।X।X) pattern
        cleaned = re.sub(self.sutra_pattern, '', cleaned)

        # Step 2: Fix issues with partial sutra references at the start
        # Remove patterns like "57)। " or "92) " that are left over
        cleaned = re.sub(r'^\s*\d+\)\s*[।॥]*\s*', '', cleaned)

        # Step 3: Clean up multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)

        # Step 4: Clean leading/trailing spaces
        cleaned = cleaned.strip()

        # Step 5: Remove leading dandas if present
        cleaned = re.sub(r'^[।॥]+\s*', '', cleaned)

        return cleaned.strip()

    def process_sentence(self, sentence: str) -> Optional[Dict[str, str]]:
        """
        Process a single sentence to extract sutra and clean text.

        Args:
            sentence: Raw sentence from Phase 1

        Returns:
            Dictionary with 'sutra' and 'sentence' keys, or None if no sutra found
        """
        # Extract sutra reference
        sutra = self.extract_sutra_reference(sentence)

        if not sutra:
            # No sutra found, skip this sentence
            return None

        # Clean the sentence
        cleaned_text = self.clean_sentence(sentence, sentence)

        # Return structured data
        return {
            "sutra": sutra,
            "word": "",
            "sentence": cleaned_text
        }

    def process_sentences(self, sentences: List[str]) -> List[Dict[str, str]]:
        """
        Process a list of sentences from Phase 1.

        If a sentence contains multiple Panini sutras, create separate entries for each.

        Args:
            sentences: List of raw sentences

        Returns:
            List of processed sentence dictionaries with sutra and cleaned text
        """
        processed = []

        for sentence in sentences:
            # Check if this sentence contains multiple Panini sutras
            all_sutras = re.findall(self.sutra_pattern, sentence)

            if len(all_sutras) > 1:
                # Multiple sutras in one sentence - create an entry for each
                for match in re.finditer(self.sutra_pattern, sentence):
                    sutra_num = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                    # Clean the sentence (removes ALL sutra references)
                    cleaned_text = self.clean_sentence(sentence, sentence)
                    processed.append({
                        "sutra": sutra_num,
                        "word": "",
                        "sentence": cleaned_text
                    })
            else:
                # Single sutra or no sutra - use original logic
                result = self.process_sentence(sentence)
                if result and result['sentence']:  # Only include if we have a sentence
                    processed.append(result)

        return processed

    def enhance_entry(self, entry: Dict) -> Dict:
        """
        Enhance a single entry from Phase 1 output.

        Args:
            entry: Dictionary with c, n, v, and sutra_sentences

        Returns:
            Enhanced entry with processed sutra_sentences
        """
        enhanced = entry.copy()

        # Process the sutra_sentences
        if 'sutra_sentences' in entry and entry['sutra_sentences']:
            enhanced['sutra_sentences'] = self.process_sentences(entry['sutra_sentences'])
        else:
            enhanced['sutra_sentences'] = []

        return enhanced

    def enhance_data(self, data: List[Dict]) -> List[Dict]:
        """
        Enhance all entries from Phase 1 output.

        Args:
            data: List of entries from Phase 1

        Returns:
            List of enhanced entries
        """
        return [self.enhance_entry(entry) for entry in data]


def main():
    """Demo function showing Phase 2 processing."""
    import json
    from pathlib import Path

    # Example usage
    processor = Phase2Processor()

    # Test with sample data
    sample_sentence = "माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।"

    print("Sample Input:")
    print(f"  {sample_sentence}")
    print()

    result = processor.process_sentence(sample_sentence)

    print("Processed Output:")
    print(f"  Sutra: {result['sutra']}")
    print(f"  Sentence: {result['sentence']}")
    print()

    # Test with problematic sentence
    problematic = "57)। `अकर्तरि च कारके संज्ञायाम्` (पा.3।3।19) इति साधुः।"
    print("Problematic Input:")
    print(f"  {problematic}")
    print()

    result2 = processor.process_sentence(problematic)
    print("Cleaned Output:")
    print(f"  Sutra: {result2['sutra']}")
    print(f"  Sentence: {result2['sentence']}")


if __name__ == '__main__':
    main()
