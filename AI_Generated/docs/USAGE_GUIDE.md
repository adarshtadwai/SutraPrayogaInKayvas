# Quick Start Guide: Enhancing JSON Files

## Overview

This guide shows you how to enhance the extracted Sutra Prayoga JSON files with **word** and **description** fields using Claude's Sanskrit understanding capabilities.

## What Gets Enhanced

Each sutra entry is enhanced from:

```json
{
  "sutra": "2.1.49",
  "word": "",
  "sentence": "`पूर्वकालैकसर्वजरत्पुराणनवकेवलाः समानाधिकरणेन` इति समासः ।"
}
```

To:

```json
{
  "sutra": "2.1.49",
  "word": "सर्वशैलाः",
  "sentence": "`पूर्वकालैकसर्वजरत्पुराणनवकेवलाः समानाधिकरणेन` इति समासः ।",
  "description": "सर्वे च ते शैलाश्च सर्वशैलाः । `पूर्वकालैकसर्वजरत्पुराणनवकेवलाः समानाधिकरणेन` इति समासः ।"
}
```

## Prerequisites

1. **Anthropic API Key**: You need an API key from Anthropic
   - Sign up at https://console.anthropic.com/
   - Get your API key from the dashboard

2. **Set the API Key**:
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

3. **Install Python Package**:
   ```bash
   pip3 install anthropic
   ```

## Step-by-Step Usage

### Step 1: View What Will Be Enhanced

Before running, you can see what the script will do:

```bash
cd /Users/adarshtadwai/Documents/GitHub/SutraPrayogaInKayvas
python3 scripts/test_enhancement.py
```

This shows:
- Current state of the data (empty word and description fields)
- What Claude will analyze (the commentary)
- Expected output format

### Step 2: Test on a Small Sample (Recommended)

Create a test file with just one verse:

```bash
python3 -c "
import json
from pathlib import Path

extract_file = Path('texts/extract/kumarasambhavam_Extract.json')
with open(extract_file) as f:
    data = json.load(f)

test_data = data.copy()
test_data['data'] = data['data'][:1]  # Just first verse

with open('texts/extract/kumarasambhavam_Extract_test.json', 'w') as f:
    json.dump(test_data, f, ensure_ascii=False, indent=2)

print('Created test file with 1 verse')
"
```

Run enhancement on the test file:

```bash
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract_test.json
```

### Step 3: Run on Full File

Once you're satisfied with the test results:

```bash
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract.json
```

## Model Selection

You can choose which Claude model to use:

### Default: Claude 3.5 Sonnet (Recommended)
```bash
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract.json
```

### Faster/Cheaper: Claude 3.5 Haiku
```bash
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract.json --model claude-3-5-haiku-20241022
```

### Most Accurate: Claude 3 Opus
```bash
python3 scripts/EnhanceJsonWithWordsAndDescriptions.py kumarasambhavam_Extract.json --model claude-3-opus-20240229
```

## Model Comparison

| Model | Speed | Cost | Sanskrit Quality | Best For |
|-------|-------|------|------------------|----------|
| Claude 3.5 Sonnet | Medium | Medium | Excellent | Most use cases (default) |
| Claude 3.5 Haiku | Fast | Low | Very Good | Large datasets, quick tests |
| Claude 3 Opus | Slow | High | Best | Critical accuracy needs |

## Expected Output

The script will:
1. Load the source commentary from `texts/In/kumarasambhavam.json`
2. Load the extract file from `texts/extract/kumarasambhavam_Extract.json`
3. For each verse:
   - For each sutra reference:
     - Call Claude to analyze the commentary
     - Extract the word being explained
     - Extract the relevant description
     - Update the entry
4. Save the enhanced data back to the extract file

## Progress Tracking

The script shows progress as it runs:

```
================================================================================
Sutra Enhancement Tool
================================================================================
Model: claude-3-5-sonnet-20241022
Extract file: kumarasambhavam_Extract.json
================================================================================
Using Claude model: claude-3-5-sonnet-20241022
Loading source commentary from: texts/In/kumarasambhavam.json
Loaded commentary for 392 verses

Loading extract file from: texts/extract/kumarasambhavam_Extract.json
Found 216 verses to enhance

Enhancing verse 1/216: 1.2
  Processing sutra 1/3: 2.1.49
  Processing sutra 2/3: 2.3.37
  Processing sutra 3/3: 1.4.51

Enhancing verse 2/216: 1.4
  Processing sutra 1/1: 2.3.65
...
```

## Time and Cost Estimates

For the full kumarasambhavam_Extract.json file:

- **Number of sutra references**: ~550
- **Processing time**: 15-30 minutes (depending on model)
- **API cost**:
  - Sonnet: ~$0.30-0.50
  - Haiku: ~$0.10-0.15
  - Opus: ~$1.00-1.50

## Troubleshooting

### "ANTHROPIC_API_KEY environment variable not set"

**Solution**: Set your API key:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

To make it permanent, add to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### "ModuleNotFoundError: No module named 'anthropic'"

**Solution**: Install the package:
```bash
pip3 install anthropic
```

### "Extract file not found"

**Solution**: Make sure you're in the project root directory:
```bash
cd /Users/adarshtadwai/Documents/GitHub/SutraPrayogaInKayvas
```

### API Rate Limiting

If you encounter rate limits, the script will show an error. Wait a few minutes and try again.

For large files, you may want to process in batches. Edit the script to process fewer verses at a time.

## Validating Results

After enhancement, validate the results:

```python
import json

# Load enhanced file
with open('texts/extract/kumarasambhavam_Extract.json') as f:
    data = json.load(f)

# Check first few entries
for verse in data['data'][:3]:
    print(f"\n{'='*80}")
    print(f"Verse {verse['loc']}:")
    print(f"{'='*80}")

    for sutra_entry in verse['sutra_sentences']:
        print(f"\nSutra: {sutra_entry['sutra']}")
        print(f"Word: {sutra_entry.get('word', 'MISSING')}")
        desc = sutra_entry.get('description', 'MISSING')
        print(f"Description: {desc[:80]}..." if len(desc) > 80 else f"Description: {desc}")
```

## Next Steps

After enhancement, you can:

1. **Analyze the data**: Use the word and description fields for linguistic analysis
2. **Create visualizations**: Build charts showing which words are explained by which sutras
3. **Build search tools**: Create interfaces to search by word or sutra number
4. **Export to other formats**: Convert to CSV, database, etc.

## Getting Help

If you encounter issues:

1. Check this guide first
2. Review the detailed documentation: `AI_Generated/docs/EnhancementScript_README.md`
3. Look at the example script: `scripts/test_enhancement.py`
4. Check the original task description: `AI_Generated/docs/EnhanceJsonFiles.md`

## Files Created/Modified

This enhancement process involves:

- **Created**: `scripts/EnhanceJsonWithWordsAndDescriptions.py` - Main enhancement script
- **Created**: `scripts/test_enhancement.py` - Test/demo script
- **Created**: `AI_Generated/docs/EnhancementScript_README.md` - Detailed documentation
- **Created**: `AI_Generated/docs/USAGE_GUIDE.md` - This guide
- **Modified**: `texts/extract/kumarasambhavam_Extract.json` - Enhanced with word and description fields
