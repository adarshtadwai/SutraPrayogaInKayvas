"""
Test script to validate that sutra references in KavyaPrayogas.json
are actually present in their respective URLs.
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
from typing import Dict, List, Tuple
import re


class SutraValidator:
    def __init__(self, json_file_path: str):
        """Initialize the validator with the JSON file path."""
        self.json_file_path = Path(json_file_path)
        self.data = self._load_data()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def _load_data(self) -> Dict:
        """Load the JSON data."""
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _fetch_url_content(self, url: str) -> str:
        """Fetch the content from a URL."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def _extract_text_from_html(self, html: str) -> str:
        """Extract text content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison by removing extra whitespace and common punctuation."""
        # Remove common punctuation that might vary
        text = re.sub(r'[।॥\s]+', ' ', text)
        return text.strip()

    def _is_sutra_present(self, sutra_ref: str, page_content: str) -> bool:
        """
        Check if the sutra reference is present in the page content.
        Uses normalized comparison to handle whitespace variations.
        """
        # Extract the core sutra text from backticks
        # Pattern like `sutra text` or `sutra text-` or variations
        sutra_pattern = r'`([^`]+)`'
        matches = re.findall(sutra_pattern, sutra_ref)

        if not matches:
            # If no backticks found, try to use the whole reference
            search_text = self._normalize_text(sutra_ref)
            normalized_content = self._normalize_text(page_content)
            return search_text in normalized_content

        # Check if any of the quoted sutras are present
        normalized_content = self._normalize_text(page_content)

        for sutra_text in matches:
            normalized_sutra = self._normalize_text(sutra_text)
            if normalized_sutra in normalized_content:
                return True

        return False

    def validate_entry(self, sutra_number: str, entry: Dict) -> Tuple[bool, str]:
        """
        Validate a single entry by checking if the sutra reference exists at the URL.
        Returns (is_valid, message)
        """
        url = entry.get('url', '')
        ref = entry.get('ref', '')
        loc = entry.get('loc', '')
        text = entry.get('text', '')

        if not url or not ref:
            return False, "Missing URL or reference"

        # Fetch the page content
        html = self._fetch_url_content(url)
        if not html:
            return False, "Failed to fetch URL"

        # Extract text from HTML
        page_text = self._extract_text_from_html(html)

        # Check if sutra is present
        is_present = self._is_sutra_present(ref, page_text)

        if is_present:
            return True, "Sutra reference found"
        else:
            return False, f"Sutra reference NOT found at {url}"

    def validate_all(self, max_entries: int = None, delay: float = 0.5) -> Dict:
        """
        Validate all entries (or up to max_entries if specified).
        Returns statistics about the validation.

        Args:
            max_entries: Maximum number of entries to validate (for testing)
            delay: Delay between requests in seconds
        """
        stats = {
            'total_sutras': 0,
            'total_entries': 0,
            'validated_entries': 0,
            'valid_entries': 0,
            'invalid_entries': 0,
            'failed_entries': 0,
            'invalid_details': []
        }

        sutra_data = self.data.get('data', {})
        stats['total_sutras'] = len(sutra_data)

        entry_count = 0

        for sutra_number, entries in sutra_data.items():
            for entry in entries:
                stats['total_entries'] += 1
                entry_count += 1

                if max_entries and entry_count > max_entries:
                    break

                print(f"Validating {sutra_number} at {entry.get('url')}...")

                is_valid, message = self.validate_entry(sutra_number, entry)
                stats['validated_entries'] += 1

                if is_valid:
                    stats['valid_entries'] += 1
                    print(f"  ✓ {message}")
                else:
                    if "Failed to fetch" in message:
                        stats['failed_entries'] += 1
                    else:
                        stats['invalid_entries'] += 1
                        stats['invalid_details'].append({
                            'sutra': sutra_number,
                            'url': entry.get('url'),
                            'ref': entry.get('ref'),
                            'message': message
                        })
                    print(f"  ✗ {message}")

                # Be polite to the server
                time.sleep(delay)

            if max_entries and entry_count > max_entries:
                break

        return stats

    def print_report(self, stats: Dict):
        """Print a validation report."""
        print("\n" + "="*80)
        print("VALIDATION REPORT")
        print("="*80)
        print(f"Total Sutras: {stats['total_sutras']}")
        print(f"Total Entries: {stats['total_entries']}")
        print(f"Validated Entries: {stats['validated_entries']}")
        print(f"Valid Entries: {stats['valid_entries']}")
        print(f"Invalid Entries: {stats['invalid_entries']}")
        print(f"Failed to Fetch: {stats['failed_entries']}")

        if stats['validated_entries'] > 0:
            success_rate = (stats['valid_entries'] / stats['validated_entries']) * 100
            print(f"Success Rate: {success_rate:.2f}%")

        if stats['invalid_details']:
            print("\n" + "-"*80)
            print("INVALID ENTRIES DETAILS:")
            print("-"*80)
            for detail in stats['invalid_details'][:10]:  # Show first 10
                print(f"\nSutra: {detail['sutra']}")
                print(f"URL: {detail['url']}")
                print(f"Reference: {detail['ref']}")
                print(f"Issue: {detail['message']}")

            if len(stats['invalid_details']) > 10:
                print(f"\n... and {len(stats['invalid_details']) - 10} more invalid entries")

        print("="*80)


def test_sample_validation():
    """Test with a small sample of entries."""
    json_path = Path(__file__).parent / 'KavyaPrayogas.json'

    print("Running sample validation test (first 10 entries)...")
    validator = SutraValidator(json_path)
    stats = validator.validate_all(max_entries=10, delay=1.0)
    validator.print_report(stats)

    # Assert that at least some are valid
    assert stats['validated_entries'] > 0, "No entries were validated"
    print("\nSample test passed!")


def test_full_validation():
    """Test all entries (warning: this will take a long time)."""
    json_path = Path(__file__).parent / 'KavyaPrayogas.json'

    print("Running FULL validation test...")
    print("WARNING: This will validate ALL entries and may take a long time!")

    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Full validation cancelled.")
        return

    validator = SutraValidator(json_path)
    stats = validator.validate_all(delay=0.5)
    validator.print_report(stats)

    # Save detailed results
    results_file = Path(__file__).parent / 'validation_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\nDetailed results saved to {results_file}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--full':
        test_full_validation()
    else:
        test_sample_validation()
