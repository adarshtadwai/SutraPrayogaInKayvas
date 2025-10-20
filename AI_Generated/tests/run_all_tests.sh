#!/bin/bash
# Comprehensive test runner for SutraPrayogaInKayvas project

cd "$(dirname "$0")"

echo "================================================================================"
echo "SUTRA PRAYOGA IN KAYVAS - COMPREHENSIVE TEST SUITE"
echo "================================================================================"
echo ""

# Run unit and integration tests (no dependencies needed)
echo "================================================================================"
echo "RUNNING UNIT & INTEGRATION TESTS"
echo "================================================================================"
echo ""
python3 run_all_tests.py

unit_test_status=$?

# Check if user wants to run URL validation tests
if [ "$1" == "--with-url" ]; then
    echo ""
    echo "================================================================================"
    echo "RUNNING URL VALIDATION TESTS (SAMPLE)"
    echo "================================================================================"
    echo ""

    cd textAggregator

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Virtual environment not found. Creating..."
        python3 -m venv venv
        source venv/bin/activate
        pip install requests beautifulsoup4
    else
        source venv/bin/activate
    fi

    # Run the validation test
    python3 test_url_validation.py
    url_test_status=$?

    deactivate
    cd ..

    echo ""
    echo "================================================================================"
    echo "FINAL TEST SUMMARY"
    echo "================================================================================"
    if [ $unit_test_status -eq 0 ]; then
        echo "Unit/Integration Tests: ✓ PASSED"
    else
        echo "Unit/Integration Tests: ✗ FAILED"
    fi

    if [ $url_test_status -eq 0 ]; then
        echo "URL Validation Tests:   ✓ PASSED"
    else
        echo "URL Validation Tests:   ✗ FAILED"
    fi
    echo "================================================================================"

    # Exit with failure if any test failed
    if [ $unit_test_status -ne 0 ] || [ $url_test_status -ne 0 ]; then
        exit 1
    fi
else
    echo ""
    echo "================================================================================"
    echo "To also run URL validation tests, use:"
    echo "  ./run_all_tests.sh --with-url"
    echo "================================================================================"
fi

exit 0
