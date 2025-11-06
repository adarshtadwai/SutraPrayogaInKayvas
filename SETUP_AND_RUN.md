# Setup and Run Guide

## Setup Instructions

### 1. Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the generated API key

### 2. Set the API Key

```bash
export GEMINI_API_KEY='your-api-key-here'

# Or to make it permanent, add to your shell config:
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Verify Setup

```bash
# Check if all required environment variables are set
if [ -n "$GEMINI_API_KEY" ]; then echo "✅ GEMINI_API_KEY is set"; else echo "❌ GEMINI_API_KEY not set"; fi
if [ -n "$GOOGLE_CLOUD_PROJECT" ]; then echo "✅ GOOGLE_CLOUD_PROJECT is set: $GOOGLE_CLOUD_PROJECT"; else echo "❌ GOOGLE_CLOUD_PROJECT not set"; fi
```

## Running the Enhancement Script

### Test on a Small Sample (Recommended First Run)

```bash
# From the project root directory
cd /Users/adarshtadwai/Documents/GitHub/SutraPrayogaInKayvas

# Run on the test file (just 1 verse, 3 sutras)
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract_test.json
```

Expected output:
```
================================================================================
Sutra Enhancement Tool (Gemini)
================================================================================
Model: gemini-1.5-pro
Extract file: kumarasambhavam_Extract_test.json
================================================================================
Using Gemini model: gemini-1.5-pro
Project: anetorg-sinaraya-kartik
Loading source commentary from: texts/In/kumarasambhavam.json
Loaded commentary for 613 verses

Loading extract file from: texts/extract/kumarasambhavam_Extract_test.json
Found 1 verses to enhance

Enhancing verse 1/1: 1.2
  Processing sutra 1/3: 2.1.49
  Processing sutra 2/3: 2.3.37
  Processing sutra 3/3: 1.4.51

Saving enhanced data to: texts/extract/kumarasambhavam_Extract_test.json

Enhancement complete!
```

### Run on Full Kumarasambhavam File

```bash
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract.json
```

Estimated time: 15-20 minutes for ~550 sutra references

### Run on Raghuvamsham File

```bash
# First check if the extract file exists
ls texts/extract/raghuvamsham_Extract.json

# If it doesn't exist, create it first using the extraction script:
python3 scripts/SutraPrayogaExtract.py raghuvansham.json

# Then enhance it:
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py raghuvamsham_Extract.json
```

## Model Options

### Default: Gemini 1.5 Pro (Best Quality)
```bash
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract.json
```

### Faster: Gemini 1.5 Flash
```bash
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract.json --model gemini-1.5-flash
```

### Older: Gemini Pro
```bash
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract.json --model gemini-pro
```

## Verifying Results

After running, check the enhanced file:

```python
import json

with open('texts/extract/kumarasambhavam_Extract_test.json') as f:
    data = json.load(f)

# Check first verse
verse = data['data'][0]
print(f"Verse {verse['loc']}:")

for sutra_entry in verse['sutra_sentences']:
    print(f"\n  Sutra: {sutra_entry['sutra']}")
    print(f"  Word: {sutra_entry.get('word', 'MISSING')}")
    desc = sutra_entry.get('description', 'MISSING')
    print(f"  Description: {desc[:80]}..." if len(desc) > 80 else f"  Description: {desc}")
```

## Troubleshooting

### "GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set"

**Solution**: Set your API key as shown in Setup step 2 above.

### "ModuleNotFoundError: No module named 'google.generativeai'"

**Solution**: Install the package:
```bash
pip3 install google-generativeai
```

### Rate Limiting

If you hit API rate limits, the script will show errors. Wait a few minutes and restart. The script processes one sutra at a time to avoid overwhelming the API.

For large files, you may want to process in batches. You can modify the script to add delays between calls:

```python
import time
# In the enhance_sutra_entry method, add:
time.sleep(1)  # Wait 1 second between API calls
```

## Cost Estimation

Gemini API pricing (as of 2024):
- **Gemini 1.5 Pro**: ~$0.10-0.30 for the full dataset
- **Gemini 1.5 Flash**: ~$0.05-0.15 for the full dataset
- **Free tier**: 60 requests per minute, should be sufficient

## Next Steps

After enhancement:
1. ✅ Verify the results look correct
2. ✅ Run on both kumarasambhavam and raghuvamsham files
3. ✅ Create visualizations or analysis tools using the enhanced data
4. ✅ Export to other formats if needed (CSV, database, etc.)

## Files Overview

- `scripts/EnhanceJsonWithWordsAndDescriptions.py` - Main enhancement script
- `scripts/test_enhancement.py` - Demo/test script
- `texts/extract/kumarasambhavam_Extract.json` - File to enhance
- `texts/extract/raghuvamsham_Extract.json` - File to enhance
- `texts/In/kumarasambhavam.json` - Source commentary
- `texts/In/raghuvamsham.json` - Source commentary
