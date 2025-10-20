# Text Aggregator & Validation

This directory contains scripts to aggregate sutra references from various Sanskrit texts and validate that the references are accurate.

## Files

- **Aggregator.py** - Aggregates sutra references from extract files into a single JSON
- **KavyaPrayogas.json** - Output file containing all sutra references organized by sutra number
- **test_url_validation.py** - Test script to validate that sutra references exist at their URLs
- **run_tests.sh** - Shell script to easily run the validation tests
- **requirements.txt** - Python dependencies needed for testing

## Setup

1. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Aggregator

To generate the `KavyaPrayogas.json` file from the extract files:

```bash
python3 Aggregator.py
```

This will:
- Read all JSON files from `../texts/extract/`
- Aggregate all sutra references by sutra number
- Sort them numerically
- Output to `KavyaPrayogas.json`

## Validation Testing

### Quick Sample Test (Recommended)

Test the first 10 entries to verify the validation is working:

```bash
./run_tests.sh
```

Or manually:
```bash
source venv/bin/activate
python3 test_url_validation.py
```

### Full Validation

To validate ALL entries (warning: this takes a long time):

```bash
source venv/bin/activate
python3 test_url_validation.py --full
```

This will:
- Fetch each URL referenced in the JSON
- Check if the sutra text quoted in `ref` is actually present on the page
- Generate a detailed report with success/failure statistics
- Save results to `validation_results.json`

## How the Validation Works

The test script:

1. **Loads** the `KavyaPrayogas.json` file
2. **Extracts** URLs and sutra references from each entry
3. **Fetches** the HTML content from each URL
4. **Searches** for the sutra text (content within backticks) in the page
5. **Reports** whether the sutra was found or not

The validation uses normalized text comparison to handle:
- Extra whitespace
- Devanagari punctuation variations (।॥)
- HTML formatting differences

## Validation Report

After running tests, you'll see a report like:

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

## Output Structure

The `KavyaPrayogas.json` file has this structure:

```json
{
  "title": "काव्यप्रयोगाः",
  "comment": "This file contains 513 unique Panini sutras covered in the commentaries",
  "data": {
    "1.1.29": [
      {
        "word": "",
        "text": "रघुवंशम्",
        "loc": "5.41",
        "url": "https://sanskritsahitya.org/raghuvansham/5.41",
        "ref": "`न बहुव्रीहौ` इति सर्वनामसंज्ञानिषेधः।"
      }
    ]
  }
}
```

Each sutra number contains an array of references, where each reference includes:
- `word` - The word being analyzed (if applicable)
- `text` - The source text name
- `loc` - Location in the text (e.g., "5.41")
- `url` - Full URL to the verse
- `ref` - The sutra reference from the commentary

## Notes

- The validation includes a delay between requests to be respectful to the server
- Sample tests validate 10 entries, full tests validate all entries
- URLs that fail to fetch are reported separately from invalid references
- The test uses BeautifulSoup to parse HTML and extract text content
