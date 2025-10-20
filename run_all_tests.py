#!/usr/bin/env python3
"""
Comprehensive test runner for the SutraPrayogaInKayvas project.

This script runs all tests in the project including:
- Unit tests for SutraPrayogaExtract
- Unit tests for SutraSentenceProcessor
- Integration tests
- URL validation tests (optional)

Usage:
    python3 run_all_tests.py              # Run all unit/integration tests
    python3 run_all_tests.py --with-url   # Also run URL validation tests (slower)
"""

import sys
import unittest
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'scripts' / 'AI_Generated' / 'tests'))


def discover_and_run_tests(test_dir, pattern='test_*.py'):
    """Discover and run all tests in a directory."""
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


def run_url_validation_tests():
    """Run URL validation tests."""
    print("\n" + "="*80)
    print("RUNNING URL VALIDATION TESTS (SAMPLE)")
    print("="*80 + "\n")

    # Import and run the validation test
    sys.path.insert(0, str(project_root / 'textAggregator'))

    try:
        from test_url_validation import test_sample_validation
        test_sample_validation()
        return True
    except Exception as e:
        print(f"Error running URL validation tests: {e}")
        return False


def main():
    """Main test runner."""
    import argparse

    parser = argparse.ArgumentParser(description='Run all project tests')
    parser.add_argument('--with-url', action='store_true',
                       help='Also run URL validation tests (slower)')
    args = parser.parse_args()

    print("="*80)
    print("SUTRA PRAYOGA IN KAYVAS - TEST SUITE")
    print("="*80)

    # Run unit and integration tests
    print("\n" + "="*80)
    print("RUNNING UNIT & INTEGRATION TESTS")
    print("="*80 + "\n")

    test_dir = project_root / 'scripts' / 'AI_Generated' / 'tests'
    result = discover_and_run_tests(str(test_dir))

    unit_tests_passed = result.wasSuccessful()

    # Optionally run URL validation tests
    url_tests_passed = True
    if args.with_url:
        url_tests_passed = run_url_validation_tests()

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Unit/Integration Tests: {'✓ PASSED' if unit_tests_passed else '✗ FAILED'}")

    if args.with_url:
        print(f"URL Validation Tests:   {'✓ PASSED' if url_tests_passed else '✗ FAILED'}")
    else:
        print("URL Validation Tests:   SKIPPED (use --with-url to run)")

    print("="*80)

    # Return exit code
    all_passed = unit_tests_passed and (url_tests_passed if args.with_url else True)
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
