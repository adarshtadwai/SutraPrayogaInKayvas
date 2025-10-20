#!/usr/bin/env python3
"""
Unit tests for SutraPrayogaExtract.py

This module contains comprehensive tests for the Sutra Prayoga extraction script.
"""

import json
import re
import sys
import unittest
from pathlib import Path

# Add scripts directory to path to import the script
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from SutraPrayogaExtract import (
    extract_sentences_with_sutra,
    extract_sutra_prayogas
)


class TestSutraPrayogaExtract(unittest.TestCase):
    """Test cases for Sutra Prayoga extraction functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.sutra_pattern = r'\(पा\.\d+।\d+।\d+\)'

        # Sample commentary text with sutra references
        self.sample_text_1 = (
            "माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः। "
            "`तस्यापत्यम्` (पा.4।1।92) इच्यण्, `टिङ्ढाणञ्-` (पा.4।1।15)इत्यादिना ङीप्।"
        )

        self.sample_text_2 = (
            "प्रभवत्यस्मादिति प्रभवः कारणम्। `ॠदोरप्` (पा.3।3।57)। "
            "`अकर्तरि च कारके संज्ञायाम्` (पा.3।3।19) इति साधुः।"
        )

        self.sample_text_no_sutra = (
            "यह कोई सूत्र नहीं है। यह केवल एक परीक्षण है।"
        )

    def test_sutra_pattern_matching(self):
        """Test that the sutra pattern correctly identifies sutra references."""
        # Should match valid sutras
        self.assertTrue(re.search(self.sutra_pattern, "(पा.1।2।70)"))
        self.assertTrue(re.search(self.sutra_pattern, "(पा.3।3।19)"))
        self.assertTrue(re.search(self.sutra_pattern, "(पा.4।1।92)"))

        # Should not match invalid formats
        self.assertFalse(re.search(self.sutra_pattern, "पा.1।2।70"))  # Missing parentheses
        self.assertFalse(re.search(self.sutra_pattern, "(पा.1.2.70)"))  # Wrong delimiter
        self.assertFalse(re.search(self.sutra_pattern, "(पा.1।2)"))  # Missing third number

    def test_extract_sentences_basic(self):
        """Test basic sentence extraction with sutra references."""
        sentences = extract_sentences_with_sutra(self.sample_text_1, self.sutra_pattern)

        # Should extract at least one sentence
        self.assertGreater(len(sentences), 0)

        # Each extracted sentence should contain a sutra reference
        for sentence in sentences:
            self.assertTrue(
                re.search(self.sutra_pattern, sentence),
                f"Sentence does not contain sutra: {sentence}"
            )

    def test_extract_sentences_no_sutra(self):
        """Test that no sentences are extracted when there are no sutras."""
        sentences = extract_sentences_with_sutra(self.sample_text_no_sutra, self.sutra_pattern)
        self.assertEqual(len(sentences), 0)

    def test_extract_sentences_multiple_sutras(self):
        """Test extraction when text contains multiple sutra references."""
        sentences = extract_sentences_with_sutra(self.sample_text_2, self.sutra_pattern)

        # Should extract sentences for both sutras
        self.assertGreater(len(sentences), 0)

        # Find all sutra references in original text
        original_sutras = re.findall(self.sutra_pattern, self.sample_text_2)
        self.assertGreater(len(original_sutras), 1, "Test text should have multiple sutras")

    def test_no_duplicate_sentences(self):
        """Test that duplicate sentences are not returned."""
        # Text with the same sentence containing multiple sutras
        text = "`पिता मात्रा` (पा.1।2।70) और (पा.2।3।80) इति।"
        sentences = extract_sentences_with_sutra(text, self.sutra_pattern)

        # Convert to set and compare lengths
        unique_sentences = set(sentences)
        self.assertEqual(
            len(sentences),
            len(unique_sentences),
            "Duplicate sentences found in extraction"
        )

    def test_danda_handling(self):
        """Test that dandas within sutra references don't break extraction."""
        # Sutra reference contains । which is also a sentence delimiter
        text = "यह वाक्य है। `सूत्र` (पा.3।3।19) यहाँ है। अगला वाक्य।"
        sentences = extract_sentences_with_sutra(text, self.sutra_pattern)

        # Should extract one sentence containing the sutra
        self.assertGreater(len(sentences), 0)

        # The extracted sentence should contain the complete sutra reference
        found_complete_sutra = any("(पा.3।3।19)" in s for s in sentences)
        self.assertTrue(
            found_complete_sutra,
            "Complete sutra reference not found in extracted sentences"
        )

    def test_sentence_boundaries(self):
        """Test that sentences are properly bounded by dandas."""
        text = "पहला वाक्य। `सूत्र` (पा.1।2।70) यहाँ है। तीसरा वाक्य।"
        sentences = extract_sentences_with_sutra(text, self.sutra_pattern)

        for sentence in sentences:
            # Sentence should typically end with a danda (। or ॥)
            # or be at the end of text
            if sentence.strip():
                # Check if it contains the sutra
                self.assertTrue(re.search(self.sutra_pattern, sentence))

    def test_empty_text(self):
        """Test extraction from empty text."""
        sentences = extract_sentences_with_sutra("", self.sutra_pattern)
        self.assertEqual(len(sentences), 0)

    def test_extract_sutra_prayogas_structure(self):
        """Test the structure of extracted prayogas data."""
        # Create a minimal test JSON file
        test_data = {
            "title": "Test",
            "data": [
                {
                    "c": "1",
                    "n": "1",
                    "v": "Test verse",
                    "mn": "`सूत्र` (पा.1।2।70) है।"
                },
                {
                    "c": "1",
                    "n": "2",
                    "v": "Another verse",
                    "mn": "No sutra here"
                }
            ]
        }

        # Write test data to temporary file
        test_file = Path(__file__).parent / 'test_temp.json'
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)

        try:
            # Extract sutras
            results = extract_sutra_prayogas(str(test_file))

            # Should have exactly 1 result (only first entry has sutra)
            self.assertEqual(len(results), 1)

            # Check structure of result
            result = results[0]
            self.assertIn('loc', result)
            self.assertIn('v', result)
            self.assertIn('sutra_sentences', result)

            # Verify values
            self.assertEqual(result['loc'], '1.1')
            self.assertEqual(result['v'], 'Test verse')
            self.assertIsInstance(result['sutra_sentences'], list)
            self.assertGreater(len(result['sutra_sentences']), 0)

        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()

    def test_extract_sutra_prayogas_no_matches(self):
        """Test extraction when no entries contain sutras."""
        test_data = {
            "title": "Test",
            "data": [
                {
                    "c": "1",
                    "n": "1",
                    "v": "Test verse",
                    "mn": "No sutra here"
                }
            ]
        }

        test_file = Path(__file__).parent / 'test_temp.json'
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)

        try:
            results = extract_sutra_prayogas(str(test_file))
            self.assertEqual(len(results), 0)
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_missing_mn_field(self):
        """Test handling of entries without 'mn' field."""
        test_data = {
            "title": "Test",
            "data": [
                {
                    "c": "1",
                    "n": "1",
                    "v": "Test verse"
                    # No 'mn' field
                }
            ]
        }

        test_file = Path(__file__).parent / 'test_temp.json'
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)

        try:
            # Should not raise an error
            results = extract_sutra_prayogas(str(test_file))
            self.assertEqual(len(results), 0)
        finally:
            if test_file.exists():
                test_file.unlink()


class TestIntegration(unittest.TestCase):
    """Integration tests using actual raghuvansham.json file."""

    def setUp(self):
        """Set up paths for integration testing."""
        self.input_file = Path(__file__).parent.parent.parent / 'texts' / 'In' / 'raghuvansham.json'

    def test_input_file_exists(self):
        """Test that the input file exists."""
        self.assertTrue(
            self.input_file.exists(),
            f"Input file not found: {self.input_file}"
        )

    def test_input_file_valid_json(self):
        """Test that the input file is valid JSON."""
        if not self.input_file.exists():
            self.skipTest("Input file not found")

        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Verify basic structure
            self.assertIn('data', data)
            self.assertIsInstance(data['data'], list)

        except json.JSONDecodeError as e:
            self.fail(f"Input file is not valid JSON: {e}")

    def test_full_extraction(self):
        """Test full extraction on actual data file."""
        if not self.input_file.exists():
            self.skipTest("Input file not found")

        results = extract_sutra_prayogas(str(self.input_file))

        # Should find multiple entries with sutras
        self.assertGreater(len(results), 0, "No sutra prayogas found")

        # Verify structure of all results
        for result in results:
            self.assertIn('loc', result)
            self.assertIn('v', result)
            self.assertIn('sutra_sentences', result)
            self.assertIsInstance(result['sutra_sentences'], list)

    def test_output_consistency(self):
        """Test that output is consistent across multiple runs."""
        if not self.input_file.exists():
            self.skipTest("Input file not found")

        results1 = extract_sutra_prayogas(str(self.input_file))
        results2 = extract_sutra_prayogas(str(self.input_file))

        # Should produce same number of results
        self.assertEqual(len(results1), len(results2))

        # Compare first few results
        for r1, r2 in zip(results1[:5], results2[:5]):
            self.assertEqual(r1['loc'], r2['loc'])
            self.assertEqual(r1['v'], r2['v'])


def run_tests():
    """Run all tests and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSutraPrayogaExtract))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
