# Sutra Prayoga Extraction Documentation

## Overview

This document describes the implementation of the Sutra Prayoga extraction script that processes [raghuvansham.json](../../../texts/raghuvansham.json) to extract all instances where Panini sutras are referenced in the commentary.

## Task Description

The goal was to:
1. Extract all entries from `texts/raghuvansham.json` that contain Panini sutra references
2. For each entry, extract only the fields: `c` (chapter), `n` (verse number), and `v` (verse text)
3. Extract complete sentences containing sutra references, where sentences are bounded by dandas (। or ॥)
4. Output the results to a JSON file

## Implementation Details

### Script Location

[SutraPrayogaExtract.py](../SutraPrayogaExtract.py)

### Key Challenges and Solutions

#### Challenge 1: Identifying Panini Sutra References

**Pattern**: Panini sutras follow the format `(पा.X।X।X)` where X represents digits.

**Solution**: Used regex pattern `r'\(पा\.\d+।\d+।\d+\)'` to match sutra references like:
- `(पा.3।3।19)`
- `(पा.1।2।70)`
- `(पा.4।1।92)`

#### Challenge 2: Extracting Sentences Bounded by Dandas

**Problem**: The danda character `।` appears both as:
- A sentence delimiter in Sanskrit text
- Part of the sutra notation itself (e.g., `पा.3।3।19`)

Simply splitting by dandas would break up sutra references.

**Solution**: Implemented a two-step approach:
1. First, find all sutra references using regex
2. For each sutra, expand left and right to find sentence boundaries:
   - Look backward from the sutra to find the preceding danda (that's not part of another sutra)
   - Look forward from the sutra to find the following danda (that's not part of the current or another sutra)
   - Extract the complete sentence including its delimiting danda

#### Challenge 3: Avoiding Duplicate Sentences

Some sentences contain multiple sutra references, which would result in the same sentence being extracted multiple times.

**Solution**: Used a `set` to track already-seen sentences and avoid duplicates.

### Data Structure

#### Input Format

The JSON file contains a `data` array with entries like:

```json
{
  "c": "1",
  "n": "2",
  "v": "क्व सूर्यप्रभवो वंशः क्व चाल्पविषया मतिः । ...",
  "mn": "क्व सूर्येति॥ प्रभवत्यस्मादिति प्रभवः कारणम्। `ॠदोरप्` (पा.3।3।57)। ...",
  ... other fields ...
}
```

#### Output Format

```json
[
  {
    "c": "1",
    "n": "2",
    "v": "क्व सूर्यप्रभवो वंशः क्व चाल्पविषया मतिः । ...",
    "sutra_sentences": [
      "`ॠदोरप्` (पा.3।3।57)।",
      "`अकर्तरि च कारके संज्ञायाम्` (पा.3।3।19) इति साधुः।",
      ...
    ]
  },
  ...
]
```

## Results

### Statistics

- **Total entries in raghuvansham.json**: 1,569
- **Entries containing Panini sutra references**: 498
- **Output file**: `texts/extract/raghuvansham_Extract.json`

### Sample Output

Here are some examples of extracted sutra prayogas:

**Chapter 1, Verse 1**:
```
माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।
`तस्यापत्यम्` (पा.4।1।92) इच्यण्, `टिङ्ढाणञ्-` (पा.4।1।15)इत्यादिना ङीप्।
```

**Chapter 1, Verse 2**:
```
`ॠदोरप्` (पा.3।3।57)।
`अकर्तरि च कारके संज्ञायाम्` (पा.3।3।19) इति साधुः।
`ईषद्दुःसुषु-` (पा.3।3।126) इत्यादिना खल्प्रत्ययः।
```

## Usage

### Running the Script

From the project root directory:

```bash
python3 scripts/AI_Generated/SutraPrayogaExtract.py
```

### Running Tests

To run the comprehensive test suite:

```bash
cd scripts/AI_Generated
python3 tests/test_sutra_prayoga_extract.py
```

### Output

The script will:
1. Read from `texts/In/raghuvansham.json`
2. Process all entries to find sutra references
3. Save results to `texts/extract/raghuvansham_Extract.json`
4. Display summary statistics and sample results

### Example Output

```
Reading from: /path/to/texts/In/raghuvansham.json

Found 498 entries with Panini sutra references
Results saved to: /path/to/texts/extract/raghuvansham_Extract.json

================================================================================
Sample results:
================================================================================

1. Chapter 1, Verse 1
   Verse: वागर्थाविव संपृक्तौ वागर्थप्रतिपत्तये...
   Sutra sentences found: 3
      1. माता च पिता च पितरौ, `पिता मात्रा` (पा.1।2।70) इति द्वन्द्वैकशेषः।
      ...
```

## Code Structure

### Functions

1. **`extract_sentences_with_sutra(text, sutra_pattern)`**
   - Extracts sentences containing sutra references from commentary text
   - Handles the danda character appearing in both sentence delimiters and sutra notation
   - Returns a list of sentences

2. **`extract_sutra_prayogas(json_file_path)`**
   - Main extraction function
   - Loads the JSON file
   - Processes each entry to find sutra references
   - Returns structured results with c, n, v, and sutra_sentences

3. **`main()`**
   - Entry point
   - Handles file I/O
   - Displays results and statistics

## Future Enhancements

Possible improvements for future versions:

1. **Add command-line arguments** to specify:
   - Custom input file path
   - Custom output file path
   - Specific chapters or verse ranges to process

2. **Additional filtering** options:
   - Extract only specific sutra patterns (e.g., only sutras from a particular adhyaya)
   - Group results by sutra reference

3. **Enhanced output formats**:
   - CSV format for spreadsheet analysis
   - HTML format for web viewing
   - Statistics by chapter

4. **Performance optimizations** for larger texts

## Dependencies

- Python 3.6+
- Standard library modules:
  - `json` - For reading/writing JSON files
  - `re` - For regex pattern matching
  - `pathlib` - For file path handling
  - `typing` - For type hints

No external dependencies required.

## Author Notes

This script was created to facilitate the study of Panini sutra usage in Kalidasa's Raghuvamsham, specifically focusing on how grammatical rules are applied and referenced in the traditional Sanskrit commentary.

The extracted data can be useful for:
- Linguistic research on Sanskrit grammar usage
- Educational purposes in Sanskrit grammar teaching
- Statistical analysis of sutra frequency and usage patterns
- Creating study materials for Paninian grammar
