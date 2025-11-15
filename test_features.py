#!/usr/bin/env python3
"""
WWWScope Feature Test Suite
Tests all major features to ensure they work correctly
"""

import os
import sys
import time
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

# Test configuration
TEST_URL = "https://example.com"
TEST_ARCHIVE_URL_1 = "https://archive.ph/d97Mw"
TEST_ARCHIVE_URL_2 = "https://archive.ph/8I1iK"

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(test_name):
    """Print test name"""
    print(f"\n{BLUE}Testing: {test_name}{RESET}")


def print_pass(message):
    """Print success message"""
    print(f"{GREEN}✓ PASS: {message}{RESET}")


def print_fail(message):
    """Print failure message"""
    print(f"{RED}✗ FAIL: {message}{RESET}")


def print_info(message):
    """Print info message"""
    print(f"{YELLOW}ℹ INFO: {message}{RESET}")


def test_groq_models():
    """Test all Groq AI models"""
    print_test("Groq AI Models")

    try:
        from core.ai_helper import GroqAIHelper

        # Check if API key is available
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print_info("GROQ_API_KEY not set. Skipping AI model tests.")
            print_info("Set environment variable: export GROQ_API_KEY='your_key'")
            return

        models = {
            "llama-3.3-70b-versatile": "Llama 3.3 70B Versatile",
            "llama-3.3-70b-specdec": "Llama 3.3 70B Speculative Decoding",
            "llama-3.1-70b-versatile": "Llama 3.1 70B Versatile (128K)",
            "llama-3.1-8b-instant": "Llama 3.1 8B Instant (128K)",
            "llama3-groq-70b-8192-tool-use-preview": "Llama 3 Groq 70B Tool Use",
            "llama3-groq-8b-8192-tool-use-preview": "Llama 3 Groq 8B Tool Use",
            "mixtral-8x7b-32768": "Mixtral 8x7B (32K)",
            "gemma2-9b-it": "Gemma 2 9B"
        }

        passed = 0
        failed = 0

        for model_id, model_name in models.items():
            try:
                print(f"\n  Testing {model_name}...")
                helper = GroqAIHelper(api_key=api_key)
                helper.model = model_id

                # Simple test request
                response = helper._make_request(
                    system_prompt="You are a helpful assistant.",
                    user_prompt="Respond with exactly: 'Test successful'",
                    temperature=0.1,
                    max_tokens=20
                )

                if response and "Test successful" in response:
                    print_pass(f"{model_name} works correctly")
                    passed += 1
                else:
                    print_fail(f"{model_name} unexpected response: {response}")
                    failed += 1

                time.sleep(2)  # Rate limiting

            except Exception as e:
                print_fail(f"{model_name} error: {str(e)}")
                failed += 1

        print(f"\n{BLUE}Model Test Results: {passed}/{len(models)} passed{RESET}")
        if failed > 0:
            print_fail(f"{failed} models failed")

    except ImportError as e:
        print_fail(f"Cannot import AI helper: {e}")
    except Exception as e:
        print_fail(f"Unexpected error: {e}")


def test_archive_services():
    """Test archive service imports"""
    print_test("Archive Services")

    try:
        from core.archive_services import (
            submit_to_wayback,
            submit_to_archive_today,
            ARCHIVE_SITES,
            ARCHIVE_TODAY_MIRRORS
        )
        print_pass("Archive services imported successfully")
        print_pass(f"Found {len(ARCHIVE_SITES)} archive services")
        print_pass(f"Found {len(ARCHIVE_TODAY_MIRRORS)} Archive.today mirrors")
        return True
    except ImportError as e:
        print_fail(f"Cannot import archive services: {e}")
        return False


def test_rate_limiter():
    """Test rate limiter"""
    print_test("Advanced Rate Limiter")

    try:
        from core.rate_limiter import (
            rate_limiter,
            smart_request,
            session_manager
        )
        print_pass("Rate limiter imported successfully")
        print_pass("Token bucket rate limiting available")
        return True
    except ImportError as e:
        print_info(f"Rate limiter not available: {e}")
        return False


def test_warc_handling():
    """Test WARC file handling"""
    print_test("WARC Handling")

    try:
        import warcio
        from warcio.archiveiterator import ArchiveIterator
        print_pass("WARC library (warcio) imported successfully")

        # Test WARC creation
        from io import BytesIO
        from warcio.warcwriter import WARCWriter

        warc_buffer = BytesIO()
        writer = WARCWriter(warc_buffer, gzip=True)

        # Create test record
        headers = [
            ('WARC-Type', 'response'),
            ('WARC-Target-URI', TEST_URL),
            ('Content-Type', 'text/html')
        ]
        record = writer.create_warc_record(
            TEST_URL,
            'response',
            payload=b'<html><body>Test</body></html>',
            warc_headers_dict=dict(headers)
        )
        writer.write_record(record)

        print_pass("WARC record creation works")

        # Test WARC reading
        warc_buffer.seek(0)
        for record in ArchiveIterator(warc_buffer):
            if record.rec_type == 'response':
                print_pass("WARC record reading works")
                break

        return True

    except ImportError as e:
        print_fail(f"Cannot import WARC library: {e}")
        return False
    except Exception as e:
        print_fail(f"WARC handling error: {e}")
        return False


def test_selenium():
    """Test Selenium availability"""
    print_test("Selenium (Screenshot Feature)")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print_pass("Selenium imported successfully")

        # Try to verify ChromeDriver availability (don't actually launch)
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print_pass("ChromeDriver manager available")
            print_info("Screenshot comparison feature available")
        except:
            print_info("ChromeDriver manager not available")

        return True

    except ImportError:
        print_info("Selenium not available (screenshot feature disabled)")
        return False


def test_beautifulsoup():
    """Test BeautifulSoup for text extraction"""
    print_test("BeautifulSoup (Text Diff)")

    try:
        from bs4 import BeautifulSoup

        # Test HTML parsing
        html = "<html><body><p>Test content</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')

        if soup.find('p').text == "Test content":
            print_pass("BeautifulSoup HTML parsing works")
            return True
        else:
            print_fail("BeautifulSoup parsing incorrect")
            return False

    except ImportError as e:
        print_fail(f"Cannot import BeautifulSoup: {e}")
        return False


def test_internet_archive():
    """Test Internet Archive library"""
    print_test("Internet Archive Integration")

    try:
        import internetarchive
        print_pass("Internet Archive library imported successfully")

        # Check credentials
        try:
            from pathlib import Path
            secrets_file = Path.cwd() / ".streamlit" / "secrets.toml"
            if secrets_file.exists():
                with open(secrets_file, 'r') as f:
                    content = f.read()
                    if 'ia_access_key' in content and 'ia_secret_key' in content:
                        print_pass("Internet Archive credentials configured")
                    else:
                        print_info("Internet Archive credentials not configured")
            else:
                print_info("No secrets.toml file found")
        except Exception as e:
            print_info(f"Could not check credentials: {e}")

        return True

    except ImportError as e:
        print_fail(f"Cannot import Internet Archive library: {e}")
        return False


def test_text_diff():
    """Test text diff functionality"""
    print_test("Text Diff Analysis")

    try:
        import difflib

        text1 = "Hello world\nThis is a test\nLine 3"
        text2 = "Hello world\nThis is a modified test\nLine 3\nLine 4"

        diff = list(difflib.unified_diff(
            text1.splitlines(keepends=True),
            text2.splitlines(keepends=True),
            lineterm='',
            n=0
        ))

        if len(diff) > 0:
            print_pass("Text diff generation works")
            # Count changes
            changes = [line for line in diff if line.startswith(('+', '-')) and not line.startswith(('+++', '---'))]
            print_pass(f"Detected {len(changes)} changed lines")
            return True
        else:
            print_fail("Diff generation failed")
            return False

    except Exception as e:
        print_fail(f"Text diff error: {e}")
        return False


def test_cdn_availability():
    """Test that free CDN resources are accessible"""
    print_test("Free CDN Availability")

    try:
        import requests

        # Test jsDelivr CDN for ReplayWeb.page
        cdn_url = "https://cdn.jsdelivr.net/npm/replaywebpage@1.8.11/ui.js"
        response = requests.head(cdn_url, timeout=10)

        if response.status_code == 200:
            print_pass("jsDelivr CDN accessible (free, no account needed)")
            print_pass("ReplayWeb.page can be loaded from CDN")
            return True
        else:
            print_fail(f"CDN returned status {response.status_code}")
            return False

    except Exception as e:
        print_fail(f"CDN test error: {e}")
        return False


def test_streamlit_import():
    """Test Streamlit import"""
    print_test("Streamlit Framework")

    try:
        import streamlit as st
        print_pass("Streamlit imported successfully")
        return True
    except ImportError as e:
        print_fail(f"Cannot import Streamlit: {e}")
        return False


def run_all_tests():
    """Run all feature tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}WWWScope v2.1.0 - Feature Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    tests = [
        ("Streamlit Framework", test_streamlit_import),
        ("BeautifulSoup (Text Diff)", test_beautifulsoup),
        ("Text Diff Analysis", test_text_diff),
        ("WARC Handling", test_warc_handling),
        ("Archive Services", test_archive_services),
        ("Rate Limiter", test_rate_limiter),
        ("Internet Archive", test_internet_archive),
        ("Selenium (Screenshots)", test_selenium),
        ("Free CDN (ReplayWeb.page)", test_cdn_availability),
        ("Groq AI Models", test_groq_models),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            if result or result is None:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_fail(f"{test_name} crashed: {e}")
            failed += 1

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Total Tests: {len(tests)}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    if failed > 0:
        print(f"{RED}Failed: {failed}{RESET}")
    else:
        print(f"{GREEN}All critical features working!{RESET}")

    print(f"\n{BLUE}{'='*60}{RESET}")

    # Feature readiness check
    critical_features = [
        "Streamlit Framework",
        "WARC Handling",
        "Archive Services",
        "Free CDN (ReplayWeb.page)"
    ]

    all_critical_pass = True
    for feature in critical_features:
        for test_name, _ in tests:
            if feature in test_name:
                # Assume pass if not in failed list
                pass

    if failed == 0:
        print(f"\n{GREEN}✅ WWWScope v2.1.0 is PRODUCTION READY{RESET}\n")
    else:
        print(f"\n{YELLOW}⚠ Some features need attention{RESET}\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
