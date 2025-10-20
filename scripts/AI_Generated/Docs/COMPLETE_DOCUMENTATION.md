# Sutra Prayoga Extraction - Complete Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Installation and Setup](#installation-and-setup)
3. [Quick Start Guide](#quick-start-guide)
4. [Input/Output Specifications](#inputoutput-specifications)
5. [Core Functionality](#core-functionality)
6. [API Reference](#api-reference)
7. [Testing](#testing)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Usage](#advanced-usage)

---

## System Overview

### Purpose

Extracts and structures Panini sutra references from Sanskrit commentary texts, creating a searchable database of grammatical rule citations.

### Components

- **SutraPrayogaExtract.py** - Main extraction and integration module
- **SutraSentenceProcessor.py** - Sentence processing and structuring module
- **Test Suite** - 32 comprehensive tests
- **Documentation** - Complete guides and design docs

### Requirements

- Python 3.6 or higher
- UTF-8 capable terminal (for Devanagari display)
- No external dependencies

---

## Installation and Setup

### Directory Structure

```
texts/
├── In/                      # Place input JSON files here
│   └── raghuvansham.json
└── extract/                 # Output files generated here
    └── raghuvansham_Extract.json

scripts/AI_Generated/
├── SutraPrayogaExtract.py
├── SutraSentenceProcessor.py
├── tests/
│   ├── test_sutra_prayoga_extract.py
│   └── test_sutra_sentence_processor.py
└── Docs/
    ├── COMPLETE_DOCUMENTATION.md (this file)
    └── DESIGN_OVERVIEW.md
```

### Setup Steps

1. Ensure Python 3.6+ is installed:
   ```bash
   python3 --version
   ```

2. Navigate to project root:
   ```bash
   cd /path/to/SutraPrayogaInKayvas
   ```

3. Verify input file exists:
   ```bash
   ls texts/In/raghuvansham.json
   ```

---

## Quick Start Guide

### Running the Extraction

From project root:

```bash
python3 scripts/AI_Generated/SutraPrayogaExtract.py
```

### Expected Output

```
Reading from: /path/to/texts/In/raghuvansham.json

[Phase 1] Extracting sutra sentences...
Found 498 entries with Panini sutra references

[Phase 2] Processing and cleaning sutra sentences...
Processed 698 sutra sentences
Found 446 unique Panini sutras

Results saved to: /path/to/texts/extract/raghuvansham_Extract.json

================================================================================
Sample results (Phase 2 Enhanced):
================================================================================

1. Location 1.1
   Verse: वागर्थाविव संपृक्तौ वागर्थप्रतिपत्तये । जगतः पितरौ...
   Sutra sentences found: 3
      1. Sutra: 1.2.70
         Sentence: माता च पिता च पितरौ, `पिता मात्रा` इति द्वन्द्वैकशेषः।
      ...
```

### Viewing Results

Output file: `texts/extract/raghuvansham_Extract.json`

Open in text editor or process programmatically.

---

## Input/Output Specifications

### Input Format

**File:** JSON with UTF-8 encoding

**Structure:**
```json
{
  "title": "रघुवंशम्",
  "custom": {...},
  "chapters": [...],
  "data": [
    {
      "c": "1",
      "n": "1",
      "v": "verse text in Devanagari",
      "mn": "commentary text with (पा.X।X।X) references",
      ...
    }
  ]
}
```

**Required Fields per Entry:**
- `c` - Chapter number (string)
- `n` - Verse number (string)
- `v` - Verse text
- `mn` - Commentary text (where sutras are found)

### Output Format

**File:** JSON with UTF-8 encoding

**Structure:**
```json
{
  "text": "raghuvansham",
  "base_link": "https://sanskritsahitya.org/",
  "comment": "This file contains 446 unique Panini sutras referenced in the commentary",
  "data": [
    {
      "loc": "1.1",
      "v": "verse text",
      "sutra_sentences": [
        {
          "sutra": "1.2.70",
          "sentence": "cleaned commentary text"
        }
      ]
    }
  ]
}
```

**Field Descriptions:**

**Metadata Level:**
- `text` - Identifier (derived from input filename)
- `base_link` - Source URL
- `comment` - Statistical information
- `data` - Array of processed entries

**Entry Level:**
- `loc` - Location as "chapter.verse" (e.g., "1.1")
- `v` - Original verse text
- `sutra_sentences` - Array of sutra-sentence objects

**Sutra-Sentence Level:**
- `sutra` - Clean format (e.g., "3.1.124")
- `sentence` - Cleaned commentary with semantic markers preserved

### Filename Convention

- **Input:** `{text_name}.json`
- **Output:** `{text_name}_Extract.json`

Example: `raghuvansham.json` → `raghuvansham_Extract.json`

---

## Core Functionality

### Sutra Pattern Recognition

**Pattern Matched:** `(पा.X।X।X)` where X are digits

**Examples:**
- `(पा.3।3।19)` → sutra "3.3.19"
- `(पा.1।2।70)` → sutra "1.2.70"
- `(पा.4।1।92)` → sutra "4.1.92"

### Sentence Boundary Detection

**Delimiters:**
- Single danda: `।`
- Double danda: `॥`

**Challenge:** Dandas appear in both sentence delimitation and sutra notation

**Solution:** Context-aware parsing that tracks:
- Parenthesis balance (inside/outside sutra notation)
- Position relative to sutra references
- Previous and next delimiters

### Multi-Sutra Handling

When multiple sutras appear in one sentence:

1. Detect subsequent sutra references
2. Find natural split points (commas)
3. Create separate entries for each sutra
4. Ensure each entry relates to one sutra only

### Text Cleaning Operations

**Performed Automatically:**

1. **Remove Sutra Notation**
   - Strip `(पा.X।X।X)` patterns
   - Sutra moved to separate field

2. **Preserve Backticks**
   - Keep `` ` `` markers around sutra names
   - Semantic information for quoted text

3. **Remove Leading Artifacts**
   - Clean number fragments (e.g., "57)। ")
   - Remove partial parsing remnants

4. **Remove Leading Dandas**
   - Strip leading punctuation
   - Ensure clean sentence start

5. **Normalize Whitespace**
   - Collapse multiple spaces
   - Trim leading/trailing whitespace

---

## API Reference

### SutraPrayogaExtract Module

#### `extract_sentences_with_sutra(text: str, sutra_pattern: str) -> List[str]`

Extracts sentences containing sutra references from commentary text.

**Parameters:**
- `text` - Commentary text to process
- `sutra_pattern` - Regex pattern for sutra references

**Returns:**
- List of sentence strings containing sutras

**Notes:**
- Handles danda ambiguity
- Prevents duplicates
- Splits multi-sutra sentences

#### `extract_sutra_prayogas(json_file_path: str) -> List[Dict[str, Any]]`

Main extraction function.

**Parameters:**
- `json_file_path` - Path to input JSON file

**Returns:**
- List of dictionaries with `loc`, `v`, and `sutra_sentences`

**Processes:**
- Loads JSON file
- Finds entries with sutra references
- Extracts sentences
- Returns structured data

#### `main()`

Entry point for command-line execution.

**Actions:**
- Defines input/output paths
- Runs extraction
- Integrates sentence processing
- Generates metadata
- Saves output
- Displays sample results

### SutraSentenceProcessor Module

#### `extract_sutra_reference(text: str) -> Optional[str]`

Extracts and formats sutra reference from text.

**Parameters:**
- `text` - Text containing sutra reference

**Returns:**
- Formatted sutra string (e.g., "3.1.124") or None

**Example:**
```python
processor = SutraSentenceProcessor()
sutra = processor.extract_sutra_reference("text (पा.3।1।124) more")
# Returns: "3.1.124"
```

#### `clean_sentence(text: str, original_sentence: str) -> str`

Cleans sentence text while preserving semantic information.

**Parameters:**
- `text` - Text to clean
- `original_sentence` - Original for context

**Returns:**
- Cleaned sentence string

**Operations:**
- Removes sutra patterns
- Fixes leading fragments
- Preserves backticks
- Normalizes whitespace

#### `process_sentence(sentence: str) -> Optional[Dict[str, str]]`

Processes complete sentence into structured object.

**Parameters:**
- `sentence` - Raw sentence with sutra reference

**Returns:**
- Dictionary with `sutra` and `sentence` keys, or None

**Example:**
```python
processor = SutraSentenceProcessor()
result = processor.process_sentence("text (पा.1।2।70) more")
# Returns: {"sutra": "1.2.70", "sentence": "cleaned text"}
```

#### `process_sentences(sentences: List[str]) -> List[Dict[str, str]]`

Processes list of sentences.

**Parameters:**
- `sentences` - List of raw sentence strings

**Returns:**
- List of structured sentence objects

#### `enhance_entry(entry: Dict[str, Any]) -> Dict[str, Any]`

Enhances single entry with structured data.

**Parameters:**
- `entry` - Entry dictionary with `sutra_sentences` as strings

**Returns:**
- Entry with `sutra_sentences` as structured objects

#### `enhance_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]`

Processes all entries.

**Parameters:**
- `data` - List of entries

**Returns:**
- List of enhanced entries

---

## Testing

### Running All Tests

From project root:

```bash
# Run extraction tests
python3 -m scripts.AI_Generated.tests.test_sutra_prayoga_extract

# Run processing tests
python3 -m scripts.AI_Generated.tests.test_sutra_sentence_processor
```

### Test Coverage

**Extraction Tests (15):**
- Pattern matching
- Sentence boundary detection
- Danda handling
- Duplicate prevention
- Data structure validation
- Empty/missing data handling
- Integration with real data

**Processing Tests (17):**
- Sutra reference parsing
- Text cleaning operations
- Backtick preservation
- Edge cases
- Data structure validation
- Real-world examples

**All Tests:** 32/32 passing ✓

### Running Individual Tests

```bash
# Specific test class
python3 -m unittest scripts.AI_Generated.tests.test_sutra_prayoga_extract.TestSutraPrayogaExtract

# Specific test method
python3 -m unittest scripts.AI_Generated.tests.test_sutra_prayoga_extract.TestSutraPrayogaExtract.test_extract_sentences_basic
```

---

## Configuration

### Modifying Input/Output Paths

Edit in `SutraPrayogaExtract.py`:

```python
def main():
    # Modify these paths
    input_file = Path(__file__).parent.parent.parent / 'texts' / 'In' / 'raghuvansham.json'
    # Output is auto-generated from input filename
```

### Changing Base URL

Edit in `SutraPrayogaExtract.py`:

```python
output_data = {
    "text": text_name,
    "base_link": "https://your-custom-url.org/",  # Modify here
    "comment": f"This file contains {len(unique_sutras)} unique Panini sutras...",
    "data": enhanced_results
}
```

### Adding Custom Cleaning Rules

Edit `clean_sentence()` in `SutraSentenceProcessor.py`:

```python
def clean_sentence(self, text: str, original_sentence: str) -> str:
    cleaned = text

    # Add custom cleaning here
    cleaned = re.sub(r'your_pattern', 'replacement', cleaned)

    # Existing cleaning operations...
    return cleaned.strip()
```

**Important:** Add corresponding tests for new cleaning rules.

---

## Troubleshooting

### Common Issues

#### Issue: "File not found" error

**Cause:** Input file missing or incorrect path

**Solution:**
- Verify file exists: `ls texts/In/raghuvansham.json`
- Check file permissions
- Ensure running from project root

#### Issue: Unicode/encoding errors

**Cause:** Terminal doesn't support UTF-8

**Solution:**
- Set terminal encoding: `export LANG=en_US.UTF-8`
- Use UTF-8 capable editor for viewing output
- On Windows, use `chcp 65001` for UTF-8

#### Issue: Import errors when running tests

**Cause:** Python module path issues

**Solution:**
- Run from project root directory
- Use: `python3 -m scripts.AI_Generated.tests.test_name`
- Not: `python3 scripts/AI_Generated/tests/test_name.py`

#### Issue: Empty output or missing sutras

**Cause:** Pattern not matching or data format changed

**Solution:**
- Verify input data format matches specification
- Check for modified sutra notation format
- Review extraction logs for warnings

### Debugging

**Enable Verbose Output:**

Add print statements in main loop:

```python
for entry in data.get('data', []):
    mn = entry.get('mn', '')
    if re.search(sutra_pattern, mn):
        print(f"Processing: c={entry.get('c')}, n={entry.get('n')}")
        # Continue processing...
```

**Test with Sample Data:**

Create minimal input file to isolate issues:

```json
{
  "title": "test",
  "data": [
    {
      "c": "1",
      "n": "1",
      "v": "test verse",
      "mn": "test `sutra` (पा.1।2।3) commentary।"
    }
  ]
}
```

---

## Advanced Usage

### Programmatic Access

```python
from pathlib import Path
from SutraPrayogaExtract import extract_sutra_prayogas
from SutraSentenceProcessor import SutraSentenceProcessor

# Load and process
input_path = Path('texts/In/raghuvansham.json')
results = extract_sutra_prayogas(str(input_path))

# Enhance with processor
processor = SutraSentenceProcessor()
enhanced = processor.enhance_data(results)

# Access data
for entry in enhanced:
    print(f"Location: {entry['loc']}")
    for sent_obj in entry['sutra_sentences']:
        print(f"  Sutra {sent_obj['sutra']}: {sent_obj['sentence']}")
```

### Querying Output Data

**Find all uses of specific sutra:**

```python
import json

with open('texts/extract/raghuvansham_Extract.json', 'r') as f:
    data = json.load(f)

target_sutra = "3.3.19"
for entry in data['data']:
    for sent_obj in entry['sutra_sentences']:
        if sent_obj['sutra'] == target_sutra:
            print(f"Found at {entry['loc']}: {sent_obj['sentence']}")
```

**Count sutra frequency:**

```python
from collections import Counter

sutras = []
for entry in data['data']:
    for sent_obj in entry['sutra_sentences']:
        sutras.append(sent_obj['sutra'])

frequency = Counter(sutras)
print("Top 10 sutras:")
for sutra, count in frequency.most_common(10):
    print(f"  {sutra}: {count} times")
```

**Group by chapter:**

```python
by_chapter = {}
for entry in data['data']:
    chapter = entry['loc'].split('.')[0]
    if chapter not in by_chapter:
        by_chapter[chapter] = []
    by_chapter[chapter].extend(entry['sutra_sentences'])

for chapter, sentences in sorted(by_chapter.items()):
    print(f"Chapter {chapter}: {len(sentences)} references")
```

### Batch Processing Multiple Texts

```python
from pathlib import Path

input_dir = Path('texts/In')
output_dir = Path('texts/extract')

for json_file in input_dir.glob('*.json'):
    print(f"Processing {json_file.name}...")

    # Extract and process
    results = extract_sutra_prayogas(str(json_file))
    processor = SutraSentenceProcessor()
    enhanced = processor.enhance_data(results)

    # Save output
    output_file = output_dir / f"{json_file.stem}_Extract.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced, f, ensure_ascii=False, indent=2)

    print(f"  Saved to {output_file.name}")
```

### Custom Output Formats

**Export to CSV:**

```python
import csv
import json

with open('texts/extract/raghuvansham_Extract.json', 'r') as f:
    data = json.load(f)

with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Location', 'Verse', 'Sutra', 'Sentence'])

    for entry in data['data']:
        for sent_obj in entry['sutra_sentences']:
            writer.writerow([
                entry['loc'],
                entry['v'],
                sent_obj['sutra'],
                sent_obj['sentence']
            ])
```

**Generate HTML Report:**

```python
import json

with open('texts/extract/raghuvansham_Extract.json', 'r') as f:
    data = json.load(f)

html = ['<html><body>']
html.append(f"<h1>{data['text']}</h1>")
html.append(f"<p>{data['comment']}</p>")

for entry in data['data'][:10]:  # First 10 entries
    html.append(f"<h2>Location {entry['loc']}</h2>")
    html.append(f"<p><em>{entry['v']}</em></p>")
    html.append('<ul>')
    for sent_obj in entry['sutra_sentences']:
        html.append(f"<li><strong>{sent_obj['sutra']}</strong>: {sent_obj['sentence']}</li>")
    html.append('</ul>')

html.append('</body></html>')

with open('report.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(html))
```

---

## Statistics and Metrics

### Raghuvansham Processing Results

| Metric | Value |
|--------|-------|
| Total verses in source | 1,569 |
| Verses with sutra references | 498 (31.7%) |
| Total sutra-sentence pairs | 698 |
| Unique sutras referenced | 446 |
| Processing time | < 1 second |
| Test coverage | 32/32 passing |

### Data Quality Metrics

- Sutra references extracted: 100%
- Sentences with preserved backticks: 99.6%
- Clean sentence format: 100%
- Structured data validation: 100%

---

## Best Practices

### For Researchers

1. **Verify Output:** Spot-check random entries against source
2. **Track Versions:** Keep input files version-controlled
3. **Document Queries:** Save query scripts for reproducibility
4. **Export Results:** Use CSV/HTML for non-technical audiences

### For Developers

1. **Run Tests:** Always run full test suite after modifications
2. **Type Hints:** Maintain type hints for clarity
3. **Add Tests:** Write tests for new functionality
4. **Document Changes:** Update docs when changing behavior

### For Data Users

1. **Understand Format:** Review output specification
2. **Handle Unicode:** Ensure UTF-8 support in tools
3. **Validate Data:** Check statistics match expectations
4. **Preserve Metadata:** Keep `text`, `base_link`, `comment` fields

---

## Support and Resources

### Documentation Files

- `COMPLETE_DOCUMENTATION.md` - This file (comprehensive reference)
- `DESIGN_OVERVIEW.md` - High-level system design
- `ExtractSutraPrayogas.md` - Original requirements
- `README.md` - Quick start guide (if exists)

### Code Files

- `SutraPrayogaExtract.py` - Main extraction script
- `SutraSentenceProcessor.py` - Processing module
- `tests/` - Test suite with examples

### Getting Help

1. Review documentation
2. Check test files for usage examples
3. Examine sample output files
4. Run tests to verify installation

---

## Appendix

### Glossary

- **Sutra:** Aphoristic rule in Panini's grammar
- **Danda:** Sentence delimiter in Sanskrit (। or ॥)
- **Commentary (mn):** Explanatory text by scholar (Mallinatha)
- **Prayoga:** Usage, application of grammatical rule
- **Backtick:** Marker (`) used to quote sutra names

### Related Resources

- Panini's Ashtadhyayi (source of sutra system)
- Sanskrit grammar resources
- Digital Sanskrit repositories
- Computational linguistics tools

### Version Information

**Current Version:** 1.0
**Python Requirement:** 3.6+
**Encoding:** UTF-8
**Test Status:** 32/32 passing

---

*Last Updated: October 2025*
