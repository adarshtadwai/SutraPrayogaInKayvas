# Sutra Prayoga Extraction - AI Generated Scripts

This directory contains AI-generated scripts for extracting Panini sutra references from Sanskrit texts.

## Project Structure

```
scripts/AI_Generated/
├── README.md                        # This file
├── SutraPrayogaExtract.py          # Main extraction script (Phase 1 + Phase 2)
├── Phase2Processor.py              # Phase 2 enhancement module
├── Docs/
│   ├── ExtractSutraPrayogas.md     # Original task specification
│   ├── SutraPrayogaExtraction_Documentation.md  # Phase 1 documentation
│   └── Phase2_Documentation.md     # Phase 2 documentation
└── tests/
    ├── README.md                    # Test suite documentation
    ├── test_sutra_prayoga_extract.py  # Phase 1 tests (15 tests)
    └── test_phase2_processor.py    # Phase 2 tests (17 tests)
```

## Quick Start

### 1. Run the Extraction Script

From the project root:

```bash
python3 scripts/AI_Generated/SutraPrayogaExtract.py
```

**Input**: `texts/In/raghuvansham.json`
**Output**: `texts/extract/raghuvansham_Extract.json`

### 2. Run Tests

```bash
cd scripts/AI_Generated
python3 tests/test_sutra_prayoga_extract.py
```

## What It Does

The script extracts and processes Panini sutra references from Sanskrit commentary text in two phases:

### Phase 1: Extraction
1. **Identifies Sutra Patterns**: Finds references like `(पा.3।3।19)`, `(पा.1।2।70)`
2. **Extracts Context**: Gets the complete sentence containing each sutra
3. **Structures Output**: Organizes by chapter (c), verse number (n), and verse text (v)

### Phase 2: Enhancement
1. **Parses Sutra References**: Converts `(पा.3।3।19)` → `"3.3.19"`
2. **Cleans Sentences**: Removes backticks, sutra refs, fixes formatting
3. **Structures Data**: Creates `{sutra: "3.3.19", sentence: "cleaned text"}` objects

### Example Input

JSON entry with commentary (`mn` field):
```json
{
  "c": "1",
  "n": "2",
  "mn": "प्रभवत्यस्मादिति प्रभवः कारणम्। `ॠदोरप्` (पा.3।3।57)। ..."
}
```

### Example Output (Phase 2 Enhanced)

```json
{
  "c": "1",
  "n": "2",
  "v": "क्व सूर्यप्रभवो वंशः...",
  "sutra_sentences": [
    {
      "sutra": "3.3.57",
      "sentence": "ॠदोरप् ।"
    },
    {
      "sutra": "3.3.19",
      "sentence": "अकर्तरि च कारके संज्ञायाम् इति साधुः।"
    }
  ]
}
```

## Key Features

### Smart Sentence Extraction

The script handles a tricky problem: the danda character `।` appears both as:
- A sentence delimiter in Sanskrit text
- Part of sutra notation (e.g., `पा.3।3।19`)

The algorithm finds sutras first, then expands to sentence boundaries without breaking the sutra references.

### Comprehensive Testing

- **32 total test cases** (15 for Phase 1, 17 for Phase 2)
- Tests for edge cases, error handling, and data validation
- Integration tests with actual Sanskrit text data
- All tests passing ✓

### Performance

- Processes 1,569 verses in ~0.2 seconds
- Extracts 498 entries with 698 sutra sentences
- Output file: ~274 KB

## Documentation

### For Users

- **[Task Specification](Docs/ExtractSutraPrayogas.md)** - Original requirements (Phase 1 & 2)
- **[Phase 1 Documentation](Docs/SutraPrayogaExtraction_Documentation.md)** - Extraction details
- **[Phase 2 Documentation](Docs/Phase2_Documentation.md)** - Enhancement & cleaning details

### For Developers

- **[Test Documentation](tests/README.md)** - Test suite details, how to run tests
- **Code Comments** - Inline documentation in source files

## Requirements

- **Python**: 3.6 or higher
- **Dependencies**: None (uses only standard library)
- **Input File**: `texts/In/raghuvansham.json` (UTF-8 encoded)

## Results Summary

From Raghuvamsham analysis:

| Metric | Count |
|--------|-------|
| Total verses | 1,569 |
| Verses with sutras | 498 |
| Total sutra sentences | 698 |
| Output size | 274 KB |

### Top Sutras Referenced

The extracted data allows for analysis of which Panini sutras are most commonly used in commentary.

## Use Cases

This tool is valuable for:

1. **Sanskrit Grammar Research**: Analyze sutra usage patterns
2. **Educational Materials**: Create study resources for Paninian grammar
3. **Linguistic Analysis**: Study grammatical rule application in classical texts
4. **Digital Humanities**: Build databases of grammatical annotations

## Error Handling

The script gracefully handles:
- Missing `mn` fields in entries
- Malformed sutra references
- Empty text
- Duplicate sentences
- Encoding issues

## Future Enhancements

Potential improvements:

1. **Command-line arguments** for custom input/output paths
2. **Filtering options** by sutra adhyaya or pada
3. **Additional output formats** (CSV, HTML)
4. **Statistics generation** (frequency analysis, sutra distribution)
5. **Support for multiple texts** (batch processing)

## Contributing

When modifying the code:

1. Update tests in `tests/test_sutra_prayoga_extract.py`
2. Run the test suite to ensure nothing breaks
3. Update documentation if changing functionality
4. Follow existing code style and commenting patterns

## License

[Add license information here]

## Author

Generated by Claude (Anthropic) as part of the SutraPrayogaInKayvas project.

## Support

For issues or questions:
1. Check the [Full Documentation](Docs/SutraPrayogaExtraction_Documentation.md)
2. Review [Test Documentation](tests/README.md)
3. Examine test cases for usage examples
