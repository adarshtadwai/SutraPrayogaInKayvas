#!/bin/bash
# Script to run the validation tests

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

echo "Running sample validation test (first 10 entries)..."
python3 test_url_validation.py

echo ""
echo "To run full validation, use:"
echo "  source venv/bin/activate && python3 test_url_validation.py --full"
