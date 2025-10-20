#!/usr/bin/env python3
"""
Unit tests for SutraSentenceProcessor

This module tests the Phase 2 enhancement functionality for sutra sentence processing.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path to import the processor
sys.path.insert(0, str(Path(__file__).parent.parent))

from SutraSentenceProcessor import SutraSentenceProcessor


class TestSutraSentenceProcessor(unittest.TestCase):
    """Test cases for SutraSentenceProcessor functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = SutraSentenceProcessor()

    def test_extract_sutra_reference_simple(self):
        """Test extracting simple sutra reference."""
        text = "माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।"
        sutra = self.processor.extract_sutra_reference(text)
        self.assertEqual(sutra, "1.2.70")

    def test_extract_sutra_reference_triple_digits(self):
        """Test extracting sutra with triple digit numbers."""
        text = "`ईषद्दुःसुषु-` (पा.3।3।126) इत्यादिना खल्प्रत्ययः।"
        sutra = self.processor.extract_sutra_reference(text)
        self.assertEqual(sutra, "3.3.126")

    def test_extract_sutra_reference_no_match(self):
        """Test text without sutra reference."""
        text = "यह कोई सूत्र नहीं है।"
        sutra = self.processor.extract_sutra_reference(text)
        self.assertIsNone(sutra)

    def test_clean_sentence_remove_sutra(self):
        """Test that sutra reference is removed from sentence."""
        text = "माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।"
        cleaned = self.processor.clean_sentence(text, text)

        # Should not contain the (पा.X।X।X) pattern
        self.assertNotIn("(पा.", cleaned)
        self.assertNotIn("1।2।70", cleaned)

    def test_clean_sentence_keep_backticks(self):
        """Test that backticks are kept (they mark sutra names)."""
        text = "`पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।"
        cleaned = self.processor.clean_sentence(text, text)

        # Should contain backticks (changed behavior)
        self.assertIn("`", cleaned)

        # And should contain the text that was in backticks
        self.assertIn("पिता मात्रा", cleaned)

    def test_clean_sentence_fix_leading_number(self):
        """Test fixing sentences with leading numbers like '57)।'."""
        text = "57)। `अकर्तरि च कारके संज्ञायाम्` (पा.3।3।19) इति साधुः।"
        cleaned = self.processor.clean_sentence(text, text)

        # Should not start with number and parenthesis
        self.assertFalse(cleaned.startswith("57)"))

        # Should start with backtick (since we keep them now)
        self.assertTrue(cleaned.startswith("`"))
        # And should contain the Sanskrit text
        self.assertIn("अकर्तरि", cleaned)

    def test_clean_sentence_remove_leading_dandas(self):
        """Test that leading dandas are removed."""
        text = "। यह एक वाक्य है।"
        cleaned = self.processor.clean_sentence(text, text)

        # Should not start with danda
        self.assertFalse(cleaned.startswith("।"))
        self.assertFalse(cleaned.startswith("॥"))

    def test_clean_sentence_multiple_spaces(self):
        """Test that multiple spaces are cleaned up."""
        text = "यह   एक    वाक्य   है।"
        cleaned = self.processor.clean_sentence(text, text)

        # Should not have multiple consecutive spaces
        self.assertNotIn("  ", cleaned)

    def test_process_sentence_complete(self):
        """Test complete sentence processing."""
        sentence = "माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।"
        result = self.processor.process_sentence(sentence)

        # Should have both fields
        self.assertIn('sutra', result)
        self.assertIn('sentence', result)

        # Verify sutra format
        self.assertEqual(result['sutra'], "1.2.70")

        # Verify sentence is cleaned (backticks are now kept)
        self.assertIn("`", result['sentence'])  # Changed: backticks kept
        self.assertNotIn("(पा.", result['sentence'])
        self.assertIn("पिता मात्रा", result['sentence'])

    def test_process_sentence_no_sutra(self):
        """Test processing sentence without sutra returns None."""
        sentence = "यह एक सामान्य वाक्य है।"
        result = self.processor.process_sentence(sentence)

        self.assertIsNone(result)

    def test_process_sentences_list(self):
        """Test processing multiple sentences."""
        sentences = [
            "माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।",
            "`ॠदोरप्` (पा.3।3।57)।",
            "No sutra here",
            "`अकर्तरि च कारके संज्ञायाम्` (पा.3।3।19) इति साधुः।"
        ]

        results = self.processor.process_sentences(sentences)

        # Should have 3 results (excluding the one without sutra)
        self.assertEqual(len(results), 3)

        # All should have sutra and sentence
        for result in results:
            self.assertIn('sutra', result)
            self.assertIn('sentence', result)

    def test_enhance_entry_structure(self):
        """Test enhancing a complete entry."""
        entry = {
            "c": "1",
            "n": "1",
            "v": "Test verse",
            "sutra_sentences": [
                "माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।",
                "`ॠदोरप्` (पा.3।3।57)।"
            ]
        }

        enhanced = self.processor.enhance_entry(entry)

        # Should preserve original fields
        self.assertEqual(enhanced['c'], "1")
        self.assertEqual(enhanced['n'], "1")
        self.assertEqual(enhanced['v'], "Test verse")

        # sutra_sentences should be enhanced
        self.assertEqual(len(enhanced['sutra_sentences']), 2)

        # Each sentence should be a dict with sutra and sentence
        for sent in enhanced['sutra_sentences']:
            self.assertIsInstance(sent, dict)
            self.assertIn('sutra', sent)
            self.assertIn('sentence', sent)

    def test_enhance_entry_empty_sentences(self):
        """Test enhancing entry with no sutra sentences."""
        entry = {
            "c": "1",
            "n": "1",
            "v": "Test verse",
            "sutra_sentences": []
        }

        enhanced = self.processor.enhance_entry(entry)

        # Should have empty list
        self.assertEqual(enhanced['sutra_sentences'], [])

    def test_enhance_data_multiple_entries(self):
        """Test enhancing multiple entries."""
        data = [
            {
                "c": "1",
                "n": "1",
                "v": "Verse 1",
                "sutra_sentences": ["माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।"]
            },
            {
                "c": "1",
                "n": "2",
                "v": "Verse 2",
                "sutra_sentences": ["`ॠदोरप्` (पा.3।3।57)।"]
            }
        ]

        enhanced = self.processor.enhance_data(data)

        # Should have same number of entries
        self.assertEqual(len(enhanced), 2)

        # All entries should be enhanced
        for entry in enhanced:
            for sent in entry['sutra_sentences']:
                self.assertIsInstance(sent, dict)
                self.assertIn('sutra', sent)
                self.assertIn('sentence', sent)

    def test_sutra_format_consistency(self):
        """Test that all sutras are in X.X.X format."""
        sentences = [
            "`पिता मात्रा` (पा.1।2।70) इति",
            "`ॠदोरप्` (पा.3।3।57)।",
            "`test` (पा.10।20।130) test"
        ]

        for sentence in sentences:
            result = self.processor.process_sentence(sentence)
            if result:
                # Should be in format X.X.X
                parts = result['sutra'].split('.')
                self.assertEqual(len(parts), 3)
                # All parts should be numeric
                for part in parts:
                    self.assertTrue(part.isdigit())

    def test_sentence_not_empty_after_cleaning(self):
        """Test that sentences are not empty after cleaning."""
        sentences = [
            "माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।",
            "`अकर्तरि च कारके संज्ञायाम्` (पा.3।3।19) इति साधुः।"
        ]

        for sentence in sentences:
            result = self.processor.process_sentence(sentence)
            self.assertIsNotNone(result)
            self.assertGreater(len(result['sentence']), 0)


class TestSutraSentenceProcessorIntegration(unittest.TestCase):
    """Integration tests for SutraSentenceProcessor."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = SutraSentenceProcessor()

    def test_real_world_examples(self):
        """Test with real examples from raghuvansham."""
        examples = [
            {
                "input": "माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।",
                "expected_sutra": "1.2.70",
                "should_contain": ["माता", "पिता", "इति"]
            },
            {
                "input": "`ॠदोरप्` (पा.3।3।57)।",
                "expected_sutra": "3.3.57",
                "should_contain": ["ॠदोरप्"]
            },
            {
                "input": "57)। `अकर्तरि च कारके संज्ञायाम्` (पा.3।3।19) इति साधुः।",
                "expected_sutra": "3.3.19",
                "should_contain": ["अकर्तरि", "साधुः"],
                "should_not_start_with": "57"
            }
        ]

        for example in examples:
            result = self.processor.process_sentence(example['input'])

            # Check sutra
            self.assertEqual(result['sutra'], example['expected_sutra'])

            # Check sentence contains expected words
            for word in example['should_contain']:
                self.assertIn(word, result['sentence'])

            # Check sentence doesn't start with certain patterns
            if 'should_not_start_with' in example:
                self.assertFalse(result['sentence'].startswith(example['should_not_start_with']))


def run_tests():
    """Run all tests and display results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSutraSentenceProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestSutraSentenceProcessorIntegration))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
