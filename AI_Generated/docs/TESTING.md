# Testing Guide

This document describes the testing infrastructure for the SutraPrayogaInKayvas project.

## Test Suite Overview

The project includes three types of tests:

1. **Unit Tests** - Test individual functions and components
2. **Integration Tests** - Test the full extraction pipeline with real data
3. **URL Validation Tests** - Verify that sutra references are actually present at their URLs

## Quick Start

### Run All Unit & Integration Tests

```bash
./run_all_tests.sh
```

### Run All Tests Including URL Validation

```bash
./run_all_tests.sh --with-url
```

## Test Files

### Unit & Integration Tests

Located in `scripts/AI_Generated/tests/`:

- **[test_sutra_prayoga_extract.py](scripts/AI_Generated/tests/test_sutra_prayoga_extract.py)** (15 tests)
  - Tests for extracting sentences with sutra references
  - Tests for the full extraction pipeline
  - Integration tests with real raghuvansham.json data

- **[test_sutra_sentence_processor.py](scripts/AI_Generated/tests/test_sutra_sentence_processor.py)** (17 tests)
  - Tests for extracting sutra numbers from sentences
  - Tests for cleaning and processing sentences
  - Tests for enhancing data entries

### URL Validation Tests

Located in `textAggregator/`:

- **[test_url_validation.py](textAggregator/test_url_validation.py)**
  - Fetches actual URLs from the final JSON output
  - Validates that quoted sutras are present on the page
  - Provides detailed validation reports

## Running Individual Test Suites

### Unit Tests Only

```bash
# Test sutra prayoga extraction
python3 scripts/AI_Generated/tests/test_sutra_prayoga_extract.py

# Test sentence processing
python3 scripts/AI_Generated/tests/test_sutra_sentence_processor.py
```

### URL Validation Tests

```bash
cd textAggregator

# Sample test (first 10 entries)
./run_tests.sh

# Or manually
source venv/bin/activate
python3 test_url_validation.py

# Full validation (all entries - takes a long time!)
python3 test_url_validation.py --full
```

## Test Statistics

**Current Status (as of latest run):**

- **Total Unit/Integration Tests:** 32
- **Success Rate:** 100% ✓
- **URL Validation Sample:** 10 entries tested, 100% success rate ✓

### Breakdown by Test Suite

| Test Suite | Tests | Status |
|------------|-------|--------|
| TestSutraPrayogaExtract | 11 | ✓ All Passing |
| TestIntegration | 4 | ✓ All Passing |
| TestSutraSentenceProcessor | 16 | ✓ All Passing |
| TestSutraSentenceProcessorIntegration | 1 | ✓ All Passing |
| URL Validation (Sample) | 10 URLs | ✓ All Passing |

## What the Tests Verify

### Extraction Tests
- ✓ Sutra pattern matching (e.g., `(पा.1।2।70)`)
- ✓ Sentence boundary detection
- ✓ Handling of danda (।) within sutra references
- ✓ Duplicate sentence removal
- ✓ Empty text handling
- ✓ Missing field handling

### Processing Tests
- ✓ Sutra reference extraction and format conversion
- ✓ Sentence cleaning (removing references, fixing formatting)
- ✓ Backtick preservation (marks sutra names)
- ✓ Leading number/danda removal
- ✓ Multiple space cleanup
- ✓ Data structure enhancement

### Integration Tests
- ✓ Full pipeline execution
- ✓ Output consistency across runs
- ✓ Real data processing
- ✓ Valid JSON structure

### URL Validation Tests
- ✓ URLs are accessible
- ✓ Sutra references quoted in JSON exist on the page
- ✓ Text normalization handles spacing/punctuation variations
- ✓ Detailed error reporting for failures

## Understanding Test Output

### Successful Run

```
================================================================================
FINAL TEST SUMMARY
================================================================================
Unit/Integration Tests: ✓ PASSED
URL Validation Tests:   ✓ PASSED
================================================================================
```

### URL Validation Report

```
================================================================================
VALIDATION REPORT
================================================================================
Total Sutras: 513
Total Entries: 11
Validated Entries: 10
Valid Entries: 10
Invalid Entries: 0
Failed to Fetch: 0
Success Rate: 100.00%
================================================================================
```

## Dependencies

### Unit & Integration Tests
- No external dependencies required
- Uses standard library only

### URL Validation Tests
- `requests` - For fetching URLs
- `beautifulsoup4` - For parsing HTML

Dependencies are automatically installed in the virtual environment when you run the tests.

## Continuous Testing

It's recommended to run tests:
- After any code changes to extraction logic
- After adding new source texts
- Before committing changes
- Periodically to ensure URLs remain valid

## Adding New Tests

To add new tests:

1. For unit tests: Add to the appropriate test class in `test_sutra_prayoga_extract.py` or `test_sutra_sentence_processor.py`
2. For integration tests: Add to `TestIntegration` class
3. For URL validation: Modify `test_url_validation.py`

Follow the existing test patterns and ensure tests are:
- Focused on a single behavior
- Well-documented with clear docstrings
- Independent (don't rely on other tests)
- Deterministic (same input → same output)

## Troubleshooting

### Virtual Environment Issues

If URL validation tests fail with "Module not found":

```bash
cd textAggregator
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### URL Validation Failures

If specific URLs fail:
- Check your internet connection
- Verify the URL is still accessible
- Check if the website structure changed
- Review the detailed error report in the output

## Performance Notes

- Unit/Integration tests: < 1 second
- URL Validation (sample, 10 entries): ~15 seconds
- URL Validation (full, all entries): ~10-15 minutes

The URL validation includes delays between requests to be respectful to the server.
