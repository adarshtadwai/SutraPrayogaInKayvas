# Test Suite for Sutra Prayoga Extraction

This directory contains comprehensive unit and integration tests for the Sutra Prayoga extraction script.

## Test Coverage

The test suite includes:

### Unit Tests (`TestSutraPrayogaExtract`)

1. **Pattern Matching Tests**
   - Validates regex pattern for identifying Panini sutra references
   - Tests valid formats: `(पा.1।2।70)`, `(पा.3।3।19)`, etc.
   - Tests invalid formats to ensure proper filtering

2. **Sentence Extraction Tests**
   - Basic sentence extraction with sutra references
   - Multiple sutras in one text
   - Empty text handling
   - Texts without sutras

3. **Edge Cases**
   - Duplicate sentence prevention
   - Danda character handling (। within sutras vs sentence delimiters)
   - Sentence boundary detection
   - Missing fields in JSON data

4. **Data Structure Tests**
   - Validates output JSON structure
   - Ensures required fields (c, n, v, sutra_sentences) are present
   - Verifies correct data types

### Integration Tests (`TestIntegration`)

1. **File System Tests**
   - Verifies input file exists at `texts/In/raghuvansham.json`
   - Validates input file is valid JSON
   - Checks JSON structure

2. **Full Extraction Tests**
   - Runs extraction on actual data file
   - Verifies results contain expected entries
   - Ensures consistency across multiple runs

## Running the Tests

### Run All Tests

From the `scripts/AI_Generated` directory:

```bash
python3 tests/test_sutra_prayoga_extract.py
```

From the project root:

```bash
cd scripts/AI_Generated && python3 tests/test_sutra_prayoga_extract.py
```

### Run Specific Test Classes

```python
# Run only unit tests
python3 -m unittest tests.test_sutra_prayoga_extract.TestSutraPrayogaExtract

# Run only integration tests
python3 -m unittest tests.test_sutra_prayoga_extract.TestIntegration
```

### Run Individual Tests

```python
# Run a specific test
python3 -m unittest tests.test_sutra_prayoga_extract.TestSutraPrayogaExtract.test_danda_handling
```

## Test Results

Expected output when all tests pass:

```
test_danda_handling ... ok
test_empty_text ... ok
test_extract_sentences_basic ... ok
test_extract_sentences_multiple_sutras ... ok
test_extract_sentences_no_sutra ... ok
test_extract_sutra_prayogas_no_matches ... ok
test_extract_sutra_prayogas_structure ... ok
test_missing_mn_field ... ok
test_no_duplicate_sentences ... ok
test_sentence_boundaries ... ok
test_sutra_pattern_matching ... ok
test_full_extraction ... ok
test_input_file_exists ... ok
test_input_file_valid_json ... ok
test_output_consistency ... ok

----------------------------------------------------------------------
Ran 15 tests in X.XXXs

OK
```

## Test Data

- **Unit tests** use synthetic test data to validate specific functionality
- **Integration tests** use the actual `raghuvansham.json` file from `texts/In/`
- Temporary test files are created and cleaned up automatically

## Writing New Tests

To add new test cases:

1. Add methods to the appropriate test class (`TestSutraPrayogaExtract` or `TestIntegration`)
2. Use descriptive test method names starting with `test_`
3. Include docstrings explaining what the test validates
4. Use `self.assert*` methods for validation
5. Clean up any temporary files in `finally` blocks

Example:

```python
def test_new_feature(self):
    """Test description of what this validates."""
    # Arrange
    test_data = ...

    # Act
    result = function_to_test(test_data)

    # Assert
    self.assertEqual(result, expected_value)
```

## Test Statistics

- **Total Tests**: 15
- **Unit Tests**: 11
- **Integration Tests**: 4
- **Code Coverage**: Functions for extraction, pattern matching, and file I/O

## Dependencies

- Python 3.6+
- `unittest` (standard library)
- `json` (standard library)
- `re` (standard library)
- `pathlib` (standard library)

No external dependencies required.

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```bash
# Exit with non-zero code if tests fail
python3 tests/test_sutra_prayoga_extract.py
echo $?  # 0 if all tests pass, 1 if any fail
```

## Troubleshooting

### Test Failures

If tests fail, check:

1. **File paths**: Ensure `texts/In/raghuvansham.json` exists
2. **File format**: Verify the JSON file is properly formatted
3. **Encoding**: The file should be UTF-8 encoded
4. **Permissions**: Ensure read access to input file and write access to test directory

### Skipped Tests

Some integration tests will be skipped if the input file is not found:

```
test_full_extraction ... skipped 'Input file not found'
```

This is expected if running tests without the full dataset.

## Test Maintenance

- Update tests when adding new features
- Ensure all edge cases are covered
- Keep test data minimal but representative
- Document complex test scenarios
- Review test coverage periodically
