import os
import gzip
import json
import shutil
import urllib3
import hashlib
import time
import streamlit as st
import requests
import concurrent.futures
import random
import contextlib
from functools import lru_cache
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import internetarchive
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import threading
import sys

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent / 'core'))

# Import improved archive services
try:
    from core.archive_services import (
        submit_to_wayback,
        submit_to_archive_today,
        retrieve_memento_links,
        process_service,
        ARCHIVE_SITES,
        ARCHIVE_TODAY_MIRRORS
    )
    IMPROVED_SERVICES_AVAILABLE = True
except ImportError:
    IMPROVED_SERVICES_AVAILABLE = False
    st.warning("⚠️ Improved archive services not available, using basic implementation")

# Import advanced rate limiter
try:
    from core.rate_limiter import (
        rate_limiter,
        rate_limited,
        smart_request,
        session_manager,
        RetryWithBackoff
    )
    RATE_LIMITER_AVAILABLE = True
except ImportError:
    RATE_LIMITER_AVAILABLE = False

# Check if Selenium is available
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def create_warc_record(url: str, response: requests.Response, date: str) -> str:
    """Create a WARC record from a web page response"""
    warc_version = "WARC/1.0"
    warc_id = f"<urn:uuid:{hashlib.sha1(url.encode()).hexdigest()}>"
    
    # Response headers
    headers = "\r\n".join([f"{k}: {v}" for k, v in response.headers.items()])
    content = response.content.decode('utf-8', errors='ignore')
    
    # Create WARC record
    warc_record = f"""\
{warc_version}
WARC-Type: response
WARC-Date: {date}
WARC-Record-ID: {warc_id}
WARC-Target-URI: {url}
Content-Type: application/http; msgtype=response
Content-Length: {len(content)}

HTTP/1.1 {response.status_code} {response.reason}
{headers}

{content}

"""
    return warc_record

def archive_page(url: str) -> Path:
    """Archive a single web page and create a WARC file"""
    try:
        # Make request
        response = requests.get(url, headers={'User-Agent': 'WWWScope Archiver/1.0'})
        response.raise_for_status()
        
        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Create WARC record
        warc_content = create_warc_record(
            url=url,
            response=response,
            date=datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        
        # Save WARC file
        domain = urlparse(url).netloc
        warc_filename = f"{domain}_{timestamp}.warc"
        warc_path = WARC_DIR / warc_filename
        
        with open(warc_path, 'w', encoding='utf-8') as f:
            f.write(warc_content)
        
        # Compress the WARC file
        compressed_path = compress_warc(warc_path)
        
        return compressed_path
    
    except Exception as e:
        raise Exception(f"Failed to archive page: {str(e)}")


# WARC Viewer functionality
import warcio
from warcio.archiveiterator import ArchiveIterator
import streamlit.components.v1 as components

def view_warc_content(warc_file: Path):
    """Display WARC file content with multiple viewer options"""
    st.markdown("### 📄 WARC Content Viewer")

    # Viewer selection
    viewer_mode = st.radio(
        "Choose viewer:",
        ["ReplayWeb.page (Recommended)", "Basic Viewer"],
        horizontal=True,
        help="ReplayWeb.page provides full-featured WARC playback with proper rendering"
    )

    if viewer_mode == "ReplayWeb.page (Recommended)":
        st.info(
            "🎯 **ReplayWeb.page Viewer**\n\n"
            "ReplayWeb.page is a professional WARC viewer that provides:\n"
            "- ✅ Full JavaScript and CSS rendering\n"
            "- ✅ Proper navigation and interaction\n"
            "- ✅ Timeline view of captures\n"
            "- ✅ Works entirely in your browser"
        )

        # Option 1: Download and open in ReplayWeb.page
        st.markdown("#### Option 1: Open in ReplayWeb.page")
        col1, col2 = st.columns(2)

        with col1:
            # Download button
            with open(warc_file, "rb") as file:
                st.download_button(
                    label="📥 Download WARC File",
                    data=file,
                    file_name=warc_file.name,
                    mime="application/warc",
                    help="Download WARC file to your computer"
                )

        with col2:
            st.markdown(
                "[![Open in ReplayWeb.page](https://img.shields.io/badge/Open-ReplayWeb.page-blue)]"
                "(https://replayweb.page/)",
                unsafe_allow_html=True
            )

        st.markdown(
            "**Instructions:**\n"
            "1. Click '📥 Download WARC File' above\n"
            "2. Click 'Open in ReplayWeb.page' or visit https://replayweb.page/\n"
            "3. Drag and drop your WARC file into ReplayWeb.page\n"
            "4. Browse the archived site with full functionality!"
        )

        # Option 2: Embedded ReplayWeb.page viewer
        st.markdown("#### Option 2: Embedded Viewer (Experimental)")
        if st.button("🚀 Launch Embedded ReplayWeb.page Viewer"):
            st.warning(
                "⚠️ Note: Embedded viewer requires the WARC file to be accessible via URL. "
                "For best results, use Option 1 above."
            )

            # Embed ReplayWeb.page
            replayweb_html = f"""
            <iframe
                src="https://replayweb.page/docs/embedding"
                width="100%"
                height="800px"
                style="border:1px solid #ccc;"
                sandbox="allow-scripts allow-same-origin allow-forms allow-downloads"
            ></iframe>
            """
            st.markdown(replayweb_html, unsafe_allow_html=True)

    else:  # Basic Viewer
        st.info("📋 **Basic Viewer** - Simple content extraction (no JavaScript rendering)")

        try:
            with open(warc_file, 'rb') as stream:
                record_count = 0
                for record in ArchiveIterator(stream):
                    if record.rec_type == 'response':
                        record_count += 1
                        # Get content
                        content = record.content_stream().read().decode('utf-8', errors='ignore')
                        headers = record.http_headers
                        url = record.rec_headers.get_header('WARC-Target-URI')

                        # Display in expandable section
                        with st.expander(f"🔗 {url}", expanded=False):
                            st.markdown("#### HTTP Headers:")
                            st.code(str(headers), language="http")

                            st.markdown("#### Content Preview:")
                            st.caption("⚠️ This is a basic HTML render. Use ReplayWeb.page for full functionality.")
                            # Create iframe for HTML content
                            components.html(content, height=600, scrolling=True)

                            # Add download button for this page
                            st.download_button(
                                "💾 Download Page Content",
                                content,
                                file_name=f"page_{url.split('/')[-1]}.html",
                                mime="text/html",
                                key=f"download_{record_count}"
                            )

                if record_count == 0:
                    st.warning("No response records found in WARC file")
                else:
                    st.success(f"✅ Loaded {record_count} pages from WARC file")

        except Exception as e:
            st.error(f"Error reading WARC file: {str(e)}")
            st.info("💡 Try using ReplayWeb.page viewer instead for better compatibility")

# Constants (imported from core.archive_services if available)
if not IMPROVED_SERVICES_AVAILABLE:
    ARCHIVE_TODAY_MIRRORS = [
        "https://archive.today",
        "https://archive.ph",
        "https://archive.is",
        "https://archive.fo"
    ]

    ARCHIVE_SITES = {
        "Wayback Machine": "https://web.archive.org/save/",
        "Archive.today": "https://archive.today/submit/",
        "Memento": "http://timetravel.mementoweb.org/api/json/",
        "Google Cache": "https://webcache.googleusercontent.com/search?q=cache:",
        "WebCite": "http://www.webcitation.org/archive/",
        "Megalodon": "http://megalodon.jp/",
        "Archive.is": "https://archive.is/",
        "TimeTravel": "https://timetravel.mementoweb.org/",
        "Perma.cc": "https://perma.cc/",
    }

# Create necessary directories if they don't exist
import tempfile
from pathlib import Path

# Create a temporary directory for the session
TEMP_DIR = Path(tempfile.gettempdir())
WARC_DIR = TEMP_DIR / "local_archives"
WARC_DIR.mkdir(exist_ok=True)

def check_storage_status():
    with st.sidebar:
        st.markdown("#### 📂 Storage Status")
        st.info(f"Temporary storage path: {WARC_DIR}")
        
        # Check if directory exists and is writable
        if WARC_DIR.exists():
            st.success("✅ Storage directory ready")
            # List any existing files
            files = list(WARC_DIR.glob("*.warc*"))
            if files:
                st.write("Current files:", len(files))
            else:
                st.write("No files currently stored")
        else:
            st.error("❌ Storage directory not available")

def save_warc_file(uploaded_file) -> bool:
    """Save uploaded WARC file locally."""
    try:
        file_path = WARC_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except Exception as e:
        st.error(f"Error saving WARC file: {e}")
        return False

def compress_warc(file_path: Path) -> Path:
    """Compress WARC file if not already compressed."""
    if not str(file_path).endswith('.gz'):
        gz_path = file_path.with_suffix(file_path.suffix + '.gz')
        with open(file_path, 'rb') as f_in:
            with gzip.open(gz_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return gz_path
    return file_path

def get_ia_credentials():
    """Safely get Internet Archive credentials."""
    try:
        access_key = st.secrets["ia_access_key"]
        secret_key = st.secrets["ia_secret_key"]
        return access_key, secret_key
    except Exception:
        st.warning("Internet Archive credentials not configured. WARC sync disabled.")
        return None, None

def upload_to_internet_archive(file_path: Path) -> str:
    """Upload WARC file to Internet Archive."""
    access_key, secret_key = get_ia_credentials()
    
    if not access_key or not secret_key:
        return "❌ Internet Archive credentials not configured"
    
    try:
        config = dict(
            s3=dict(
                access=access_key,
                secret=secret_key
            )
        )
        
        # Create unique identifier
        identifier = f"wwwscope_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create metadata for the archive
        metadata = {
            'title': f'WWWScope Archive - {file_path.stem}',
            'mediatype': 'web',
            'collection': 'opensource',
            'description': f'Web archive created by WWWScope archiver. Original file: {file_path.name}',
            'creator': 'WWWScope Archiver',
            'subject': ['web archiving', 'WARC', 'preservation'],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'language': 'eng',
            'source': 'WWWScope (https://github.com/shadowdevnotreal/wwwscope)',
            'warc_file_name': file_path.name,
            'licenseurl': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'rights': 'This archive is released under CC0 1.0 Universal (Public Domain)'
        }

        item = internetarchive.upload(
            identifier,
            files=[str(file_path)],
            metadata=metadata,
            config=config,
            queue_derive=True,
            verify=True
        )
        
        return f"✅ Successfully uploaded to Internet Archive: https://archive.org/details/{identifier}"
    except Exception as e:
        return f"❌ Upload failed: {str(e)}"
        

def sync_to_internet_archive(file_path: Path) -> str:
    """Sync WARC file to Internet Archive."""
    try:
        return upload_to_internet_archive(file_path)
    except Exception as e:
        return f"❌ Sync failed: {e}"

def list_local_warcs() -> list:
    """List all local WARC files."""
    return list(WARC_DIR.glob("*.warc*"))

def get_warc_info(file_path: Path) -> dict:
    return {
        "name": file_path.name,
        "size": f"{file_path.stat().st_size / 1024 / 1024:.2f} MB",
        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    }
      

# Utility functions
@contextlib.contextmanager
def ignore_thread_context_warning():
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="missing ScriptRunContext")
        yield

def rate_limited_request(url: str) -> requests.Response:
    """Make a rate-limited request to avoid overwhelming servers."""
    if RATE_LIMITER_AVAILABLE:
        # Use advanced rate limiter with smart request handling
        return smart_request(url, service='default', method='GET')
    else:
        # Fallback to basic rate limiting
        time.sleep(1)
        return requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)

def clean_url(url: str) -> str:
    """Clean URL by removing any duplicate protocols."""
    url = url.replace('https://https://', 'https://')
    url = url.replace('http://http://', 'http://')
    url = url.replace('https://http://', 'https://')
    return url

def validate_url(url: str) -> bool:
    """Validate if the URL is accessible and properly formatted."""
    if not url:
        return False
    
    # Add http:// if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return True
    except:
        return False

def take_screenshot(url: str, filename: str) -> Path:
    """Take a screenshot of a URL using Selenium with proper cleanup."""
    driver = None
    try:
        if not SELENIUM_AVAILABLE:
            return None

        driver = get_selenium_driver()
        if not driver:
            return None

        # Load page with timeout
        driver.get(url)
        time.sleep(3)  # Increased wait time for complex archive pages

        # Take screenshot
        screenshot_path = TEMP_DIR / filename
        driver.save_screenshot(str(screenshot_path))

        # Verify file was created
        if screenshot_path.exists():
            return screenshot_path
        else:
            return None

    except Exception as e:
        # Don't display warning here - let caller handle it
        return None
    finally:
        # Guaranteed cleanup
        if driver:
            try:
                driver.quit()
            except:
                pass  # Ignore cleanup errors

def extract_text_from_url(url: str) -> str:
    """Extract visible text content from a URL with rate limit handling."""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            retry_after = e.response.headers.get('Retry-After', 'unknown')
            return f"RATE_LIMIT: Archive service rate limit exceeded. Retry after: {retry_after} seconds. Too many requests in a short time."
        elif e.response.status_code == 403:
            return f"ACCESS_DENIED: Archive service blocked access (403 Forbidden). May require browser access or CAPTCHA."
        elif e.response.status_code == 404:
            return f"NOT_FOUND: Archive not found (404). The URL may not be archived."
        else:
            return f"HTTP_ERROR: HTTP {e.response.status_code} - {e.response.reason}"
    except requests.exceptions.Timeout:
        return "TIMEOUT: Request timed out after 30 seconds. Archive service may be slow or unavailable."
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR: Could not connect to the archive. Check your internet connection."
    except requests.exceptions.SSLError:
        return "SSL_ERROR: SSL certificate error. The archive may have an invalid certificate."
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def compare_text_diff(text1: str, text2: str) -> str:
    """Compare two texts and return a simple diff representation."""
    import difflib

    lines1 = text1.splitlines()
    lines2 = text2.splitlines()

    diff = difflib.unified_diff(lines1, lines2, lineterm='', n=3)
    return '\n'.join(diff)

def compare_archives(url1: str, url2: str) -> None:
    """Compare two archived versions visually."""
    try:
        # Validate URLs
        if not url1.startswith(('http://', 'https://')) or not url2.startswith(('http://', 'https://')):
            st.error("Both URLs must start with http:// or https://")
            return

        # Create comparison view
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Version 1")
            st.markdown(f"Source: {url1}")
            # Use HTML iframe instead of streamlit component
            st.markdown(f'<iframe src="{url1}" width="100%" height="600px"></iframe>', unsafe_allow_html=True)

        with col2:
            st.markdown("### Version 2")
            st.markdown(f"Source: {url2}")
            # Use HTML iframe instead of streamlit component
            st.markdown(f'<iframe src="{url2}" width="100%" height="600px"></iframe>', unsafe_allow_html=True)

        # Add comparison tools
        st.markdown("### Comparison Tools")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📸 Screenshot Comparison"):
                with st.spinner("Taking screenshots..."):
                    if not SELENIUM_AVAILABLE:
                        st.warning(
                            "📸 Screenshot Feature\n\n"
                            "Screenshot comparison requires Selenium. Install with:\n"
                            "```\n"
                            "pip install selenium webdriver-manager\n"
                            "```\n\n"
                            "For now, use the iframe preview above for visual comparison."
                        )
                    else:
                        screenshot1 = take_screenshot(url1, "screenshot1.png")
                        screenshot2 = take_screenshot(url2, "screenshot2.png")

                        if screenshot1 and screenshot2:
                            st.markdown("### 📸 Screenshot Comparison")
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.image(str(screenshot1), caption="Version 1", use_column_width=True)
                            with col_b:
                                st.image(str(screenshot2), caption="Version 2", use_column_width=True)
                            st.success("Screenshots captured successfully!")
                        else:
                            st.error("Failed to capture screenshots. Please ensure Chrome/Chromium is installed.")

        with col2:
            if st.button("📊 Text Diff"):
                with st.spinner("Extracting and comparing text..."):
                    text1 = extract_text_from_url(url1)
                    text2 = extract_text_from_url(url2)

                    if not text1.startswith("Error") and not text2.startswith("Error"):
                        diff = compare_text_diff(text1, text2)

                        st.markdown("### 📊 Text Difference Analysis")

                        # Show statistics
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Version 1 Length", f"{len(text1)} chars")
                        with col_b:
                            st.metric("Version 2 Length", f"{len(text2)} chars")
                        with col_c:
                            diff_lines = [line for line in diff.splitlines() if line.startswith(('+', '-'))]
                            st.metric("Changed Lines", len(diff_lines))

                        # Show diff
                        st.markdown("#### Detailed Differences")
                        st.markdown(
                            "Lines starting with `-` were removed, lines starting with `+` were added."
                        )

                        if diff:
                            st.code(diff, language="diff")
                        else:
                            st.success("✅ No text differences detected! The content appears identical.")

                        # Show side-by-side text samples
                        with st.expander("📄 View Full Text Content"):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.markdown("**Version 1 Text:**")
                                st.text_area("", text1[:5000], height=300, key="text1")
                            with col_b:
                                st.markdown("**Version 2 Text:**")
                                st.text_area("", text2[:5000], height=300, key="text2")
                    else:
                        st.error(f"Failed to extract text:\n{text1}\n{text2}")

        # Add URLs for manual comparison
        st.markdown("### 🔗 Direct Links")
        st.markdown(f"Version 1: [{url1}]({url1})")
        st.markdown(f"Version 2: [{url2}]({url2})")

    except Exception as e:
        st.error(f"Error comparing archives: {str(e)}")
        st.markdown("### Manual Comparison Links")
        st.markdown(f"Version 1: [{url1}]({url1})")
        st.markdown(f"Version 2: [{url2}]({url2})")
        

def verify_archive_status(url: str, service: str) -> bool:
    """Verify if URL was actually archived."""
    try:
        if service == "Wayback Machine":
            check_url = f"https://archive.org/wayback/available?url={url}"
            response = requests.get(check_url, timeout=30)
            data = response.json()
            return bool(data.get('archived_snapshots', {}).get('closest', {}).get('available'))
        return True  # Default to True for other services
    except:
        return False

def get_selenium_driver():
    """Initialize and return a configured Selenium WebDriver."""
    if not SELENIUM_AVAILABLE:
        return None

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")  # Full HD screenshots

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        # Don't show error here - let caller handle it
        return None

# Archive service functions - Use improved versions if available
if not IMPROVED_SERVICES_AVAILABLE:
    # Fallback implementations if improved services not available
    def submit_to_wayback(url: str) -> str:
        """Submit URL to Wayback Machine with basic verification."""
        try:
            check_url = f"https://archive.org/wayback/available?url={url}"
            check_response = requests.get(check_url, timeout=30)
            check_data = check_response.json()

            if check_data.get('archived_snapshots', {}).get('closest', {}).get('available'):
                return f"✅ URL already archived: https://web.archive.org/web/*/{url}"

            response = requests.post(
                ARCHIVE_SITES["Wayback Machine"],
                data={"url": url},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=30,
            )

            if response.status_code == 429:
                return "❌ Rate limit exceeded. Please wait and try again."
            elif not response.ok:
                return f"❌ Archive.org failed with status code: {response.status_code}"

            time.sleep(5)
            return "⚠️ Archive submission accepted but not yet available. Please check back later."

        except Exception as e:
            return f"⚠️ Error: {str(e)}"


    def submit_to_archive_today(url: str) -> str:
        """Submit URL to Archive.today - basic implementation."""
        st.info("⚠️ Archive.today CAPTCHA Notice: May require manual CAPTCHA solving")

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": random.choice(ARCHIVE_TODAY_MIRRORS)
        }

        for mirror in ARCHIVE_TODAY_MIRRORS:
            try:
                response = requests.post(
                    f"{mirror}/submit/",
                    data={"url": url},
                    headers=headers,
                    timeout=60
                )
                if response.ok:
                    archived_url = response.url
                    return f"✅ Archived Successfully at {archived_url}"
            except requests.exceptions.RequestException as e:
                continue

        return "❌ Archive.today failed on all mirrors."


    def retrieve_memento_links(url: str) -> Dict[str, Any]:
        """Retrieve archived versions from Memento Web."""
        try:
            response = rate_limited_request(f"{ARCHIVE_SITES['Memento']}?url={url}")
            if response.ok:
                return response.json()
            return {"success": False, "message": "No archived versions found."}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

# process_service function - fallback only if improved version not available
if not IMPROVED_SERVICES_AVAILABLE:
    def process_service(service: str, url: str, mode: str) -> str:
        """Process a single archive service request - basic implementation."""
        try:
            if mode == "Archive URL":
                if service == "Wayback Machine":
                    return submit_to_wayback(url)
                elif service == "Archive.today":
                    return submit_to_archive_today(url)
            else:  # Retrieve mode
                base_urls = {
                    "Wayback Machine": f"https://web.archive.org/web/*/{url}",
                    "Archive.today": f"https://archive.today/{url}",
                    "Archive.is": f"https://archive.is/{url}",
                    "Google Cache": f"https://webcache.googleusercontent.com/search?q=cache:{url}",
                    "WebCite": f"http://www.webcitation.org/query?url={url}",
                    "Megalodon": f"http://megalodon.jp/?url={url}",
                    "TimeTravel": f"https://timetravel.mementoweb.org/list/{url}",
                    "Perma.cc": f"https://perma.cc/search?q={url}",
                    "Memento": retrieve_memento_links(url)
                }

                if service in base_urls:
                    return base_urls[service]
                return f"Service {service} not configured for retrieval"

        except Exception as e:
            return f"Error processing {service}: {str(e)}"

# Streamlit UI
st.title("🌍 WWWScope – Web Archiving & Retrieval")
st.write("Archive and retrieve web pages from multiple services.")

# System status in sidebar
with st.sidebar:
    st.markdown("### 🔧 System Status")

    # Module status indicators
    if IMPROVED_SERVICES_AVAILABLE:
        st.success("✅ Enhanced Archive Services")
    else:
        st.warning("⚠️ Basic Archive Services")

    if RATE_LIMITER_AVAILABLE:
        st.success("✅ Advanced Rate Limiting")
    else:
        st.warning("⚠️ Basic Rate Limiting")

    if SELENIUM_AVAILABLE:
        st.success("✅ Screenshot Comparison")
    else:
        st.info("ℹ️ Screenshot Feature Disabled")

    st.markdown("---")

# URL input with better validation
url = st.text_input("Enter the URL to archive or retrieve:", 
                    placeholder="https://example.com")

# Create tabs for different modes
tab1, tab2, tab3, tab4 = st.tabs([
    "📥 Archive URL", 
    "🔍 Retrieve Archives",
    "🔄 Compare Archives",
    "📦 WARC Management"
])

# Tab 1: Archive URL
with tab1:
    st.header("Archive URL")
    
    archive_method = st.radio(
        "Choose archive method:",
        ["Online Services", "Local WARC"],
        horizontal=True,
        help="Online Services: Use archive.org, archive.today, etc.\nLocal WARC: Create local WARC file"
    )
    
    if archive_method == "Online Services":
        # Service selection using a more visual approach
        col1, col2, col3 = st.columns(3)
        
        with col1:
            wayback = st.checkbox("Wayback Machine", value=True,
                                help="Internet Archive's Wayback Machine - Most reliable")
        with col2:
            archive_today = st.checkbox("Archive.today", 
                                    help="Good for dynamic content and paywalled sites")
        with col3:
            memento = st.checkbox("Memento", 
                                help="Aggregates multiple archive services")

        selected_services = []
        if wayback:
            selected_services.append("Wayback Machine")
        if archive_today:
            selected_services.append("Archive.today")
        if memento:
            selected_services.append("Memento")

        if st.button("🚀 Archive Now", use_container_width=True):
            if not url:
                st.error("Please enter a URL")
            else:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                url = clean_url(url)
                
                if not validate_url(url):
                    st.error("Unable to access the URL. Please check if it's correct and accessible.")
                else:
                    if not selected_services:
                        st.warning("Please select at least one archive service")
                    else:
                        results = {}
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        with st.spinner("Archiving in progress..."):
                            for idx, service in enumerate(selected_services):
                                status_text.text(f"Processing {service}...")
                                try:
                                    results[service] = process_service(service, url, "Archive URL")
                                except Exception as e:
                                    results[service] = f"Failed: {str(e)}"
                                progress_bar.progress((idx + 1) / len(selected_services))

                        status_text.empty()
                        progress_bar.empty()
                        
                        # Display results
                        for service, result in results.items():
                            with st.expander(f"{service} Result", expanded=True):
                                if "✅" in str(result):
                                    st.success(result)
                                elif "❌" in str(result):
                                    st.error(result)
                                else:
                                    st.info(result)
    
    else:  # Local WARC
        st.markdown("### 📥 Local WARC Archive")
        if st.button("📦 Create WARC Archive", use_container_width=True):
            if not url:
                st.error("Please enter a URL")
            else:
                try:
                    with st.spinner("Creating WARC archive..."):
                        # Clean and validate URL
                        url = clean_url(url)
                        if not url.startswith(('http://', 'https://')):
                            url = 'https://' + url
                            
                        if not validate_url(url):
                            st.error("Unable to access the URL. Please check if it's correct and accessible.")
                        else:
                            # Archive the page
                            warc_path = archive_page(url)
                            
                            # Show success message
                            st.success(f"✅ Page archived successfully!")
                            st.info(f"WARC file created: {warc_path.name}")
                            
                            # Option to view content
                            if st.button("👀 View Archived Content"):
                                view_warc_content(warc_path)
                            
                            # Option to upload to Internet Archive
                            if st.button("🔄 Upload to Internet Archive"):
                                result = upload_to_internet_archive(warc_path)
                                st.write(result)
                                
                except Exception as e:
                    st.error(f"Failed to create WARC: {str(e)}")

# In Tab 2 (Retrieve Archives), ensure results are stored and displayed correctly
with tab2:
    st.header("Retrieve Archives")
    
    retrieve_service = st.radio(
        "Choose archive service to search:",
        ["All Services", "Wayback Machine Only", "Archive.today Only", 
         "Memento Only", "Google Cache Only", "WebCite Only"],
        horizontal=True
    )
    
    if st.button("🔍 Search Archives", use_container_width=True):
        if not url:
            st.error("Please enter a URL")
        else:
            url = clean_url(url)
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            services_to_check = []
            if retrieve_service == "All Services":
                services_to_check = list(ARCHIVE_SITES.keys())
            else:
                service_name = retrieve_service.replace(" Only", "")
                services_to_check = [service_name]

            # Initialize results dictionary
            results = {}

            # Results display
            st.info("Searching archives...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, service in enumerate(services_to_check):
                status_text.text(f"🔍 Checking {service}...")
                progress_bar.progress((idx + 1) / len(services_to_check))
                
                result = process_service(service, url, "Retrieve")
                results[service] = result  # Store result in the dictionary
                
                if isinstance(result, dict):
                    st.json(result)
                else:
                    with st.expander(f"📑 {service} Results", expanded=True):
                        st.markdown(f"🔗 [View Archive]({result})")
                        st.markdown(f"Direct link: `{result}`")
                
            progress_bar.empty()
            status_text.empty()
            st.success("✅ Search complete!")
            
        # Summary of results
        st.subheader("📊 Search Summary")
        summary = []

        for service, result in results.items():
            if isinstance(result, dict):
                summary.append(f"{service}: No archived versions found.")
            else:
                if "No archived versions found." in result:
                    summary.append(f"{service}: No archived versions found.")
                else:
                    summary.append(f"{service}: Archive available")

        # Display the summary
        for entry in summary:
            st.write(entry)

        # Add timestamp
        st.caption(f"Search completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
# Tab 3: Compare Archives - COMPLETELY REDESIGNED WITH SESSION STATE
with tab3:
    st.header("🔄 Archive Comparison")
    st.write("Compare two versions of archived content visually.")

    # Initialize session state for comparison
    if 'comparing' not in st.session_state:
        st.session_state.comparing = False
    if 'compare_url1' not in st.session_state:
        st.session_state.compare_url1 = ""
    if 'compare_url2' not in st.session_state:
        st.session_state.compare_url2 = ""

    # URL inputs with unique keys
    url1 = st.text_input("First Archive URL:", key="input_url1", value=st.session_state.compare_url1)
    url2 = st.text_input("Second Archive URL:", key="input_url2", value=st.session_state.compare_url2)

    # Start comparison button
    if st.button("🚀 Start Comparison", use_container_width=True, key="start_compare_btn"):
        if url1 and url2:
            # Clean URLs
            url1 = clean_url(url1)
            url2 = clean_url(url2)

            # Validate URLs
            parsed1 = urlparse(url1)
            parsed2 = urlparse(url2)

            if not all([parsed1.scheme in ['http', 'https'], parsed1.netloc,
                       parsed2.scheme in ['http', 'https'], parsed2.netloc]):
                st.error("❌ Both URLs must be valid http:// or https:// URLs")
            else:
                st.session_state.comparing = True
                st.session_state.compare_url1 = url1
                st.session_state.compare_url2 = url2
                st.rerun()
        else:
            st.warning("⚠️ Please enter both archive URLs to compare")

    # Show comparison if active
    if st.session_state.comparing and st.session_state.compare_url1 and st.session_state.compare_url2:
        url1 = st.session_state.compare_url1
        url2 = st.session_state.compare_url2

        st.success(f"✅ Comparing: **{url1}** vs **{url2}**")

        # Stop comparison button
        if st.button("❌ Stop Comparison", key="stop_compare_btn"):
            st.session_state.comparing = False
            st.rerun()

        st.markdown("---")

        # Iframe preview
        st.markdown("### 📺 Live Preview")
        st.info("⚠️ Note: Some sites may block iframe embedding due to security policies (X-Frame-Options, CSP). If an archive doesn't display, use the Screenshot Comparison or direct links below.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Version 1")
            st.caption(f"Source: {url1}")
            import html
            safe_url1 = html.escape(url1, quote=True)
            st.markdown(
                f'<iframe src="{safe_url1}" width="100%" height="600px" '
                f'sandbox="allow-same-origin allow-scripts allow-forms" '
                f'style="border:1px solid #ccc;"></iframe>',
                unsafe_allow_html=True
            )

        with col2:
            st.markdown("#### Version 2")
            st.caption(f"Source: {url2}")
            safe_url2 = html.escape(url2, quote=True)
            st.markdown(
                f'<iframe src="{safe_url2}" width="100%" height="600px" '
                f'sandbox="allow-same-origin allow-scripts allow-forms" '
                f'style="border:1px solid #ccc;"></iframe>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        # Comparison Tools - NOW OUTSIDE compare_archives() function!
        st.markdown("### 🔧 Comparison Tools")

        tool_col1, tool_col2 = st.columns(2)

        # Screenshot Comparison Tool
        with tool_col1:
            if st.button("📸 Screenshot Comparison", use_container_width=True, key="screenshot_btn"):
                if not SELENIUM_AVAILABLE:
                    st.warning(
                        "📸 **Screenshot Feature Unavailable**\n\n"
                        "Screenshot comparison requires Selenium and Chrome/Chromium.\n\n"
                        "**Installation:**\n"
                        "1. Install Selenium: `pip install selenium webdriver-manager`\n"
                        "2. Install Chrome:\n"
                        "   - Linux: `sudo apt-get install chromium-browser`\n"
                        "   - Windows/Mac: Download from google.com/chrome\n\n"
                        "For now, use the iframe preview above for visual comparison."
                    )
                else:
                    with st.spinner("📸 Taking screenshots... This may take 10-20 seconds..."):
                        try:
                            screenshot1 = take_screenshot(url1, "screenshot1.png")
                            screenshot2 = take_screenshot(url2, "screenshot2.png")

                            if screenshot1 and screenshot2 and screenshot1.exists() and screenshot2.exists():
                                st.markdown("### 📸 Screenshot Comparison Results")

                                # Side-by-side comparison (constrained by column width)
                                img_col1, img_col2 = st.columns(2)
                                with img_col1:
                                    st.image(str(screenshot1), caption="Version 1", use_column_width=True)
                                with img_col2:
                                    st.image(str(screenshot2), caption="Version 2", use_column_width=True)

                                st.success("✅ Screenshots captured successfully!")

                                # Full-size view in expanders
                                st.markdown("#### 🔍 View Full-Size Screenshots")
                                st.info("💡 Click below to view screenshots at full resolution (1920x1080)")

                                with st.expander("🖼️ Version 1 - Full Size", expanded=False):
                                    st.image(str(screenshot1), caption=f"Version 1 - Full Resolution: {url1}", use_column_width=False)

                                with st.expander("🖼️ Version 2 - Full Size", expanded=False):
                                    st.image(str(screenshot2), caption=f"Version 2 - Full Resolution: {url2}", use_column_width=False)
                            else:
                                st.error(
                                    "❌ **Screenshot capture failed.**\n\n"
                                    "**Possible reasons:**\n"
                                    "- Chrome/Chromium is not installed\n"
                                    "- WebDriver initialization failed\n"
                                    "- URLs could not be loaded (check accessibility)\n"
                                    "- Permission issues writing screenshots\n\n"
                                    "**Troubleshooting:**\n"
                                    "- Ensure Chrome is installed and accessible\n"
                                    "- Check that URLs are accessible and not blocking automated access"
                                )
                        except Exception as e:
                            st.error(f"❌ Screenshot error: {str(e)}")

        # Text Diff Tool
        with tool_col2:
            if st.button("📊 Text Diff Analysis", use_container_width=True, key="textdiff_btn"):
                with st.spinner("📊 Extracting and comparing text... This may take 10-30 seconds..."):
                    try:
                        text1 = extract_text_from_url(url1)
                        text2 = extract_text_from_url(url2)

                        # Check for errors with specific handling
                        has_error = False

                        if text1.startswith("RATE_LIMIT") or text2.startswith("RATE_LIMIT"):
                            st.error("⏱️ **Rate Limit Exceeded**")
                            st.warning(
                                "The archive service has rate limited your requests. This happens when:\n"
                                "- You make too many requests in a short time\n"
                                "- The archive service (archive.ph, archive.today, etc.) is protecting against automated access\n\n"
                                "**Solutions:**\n"
                                "1. ⏳ Wait 60-120 seconds before trying again\n"
                                "2. 📸 Use the Screenshot Comparison instead (doesn't trigger rate limits)\n"
                                "3. 👁️ Use the iframe preview above to view the archives visually\n"
                                "4. 🔗 Use the direct links below to open archives in your browser"
                            )
                            has_error = True
                        elif text1.startswith("ACCESS_DENIED") or text2.startswith("ACCESS_DENIED"):
                            st.error("🚫 **Access Denied (403 Forbidden)**")
                            st.info(
                                "The archive service blocked automated access. This may require:\n"
                                "- Opening the URL in a browser\n"
                                "- Solving a CAPTCHA\n"
                                "- Using a different archive service\n\n"
                                "💡 Try the Screenshot Comparison or direct links instead."
                            )
                            has_error = True
                        elif text1.startswith("NOT_FOUND") or text2.startswith("NOT_FOUND"):
                            st.error("❌ **Archive Not Found (404)**")
                            st.info("One or both URLs may not be archived. Check the direct links below.")
                            has_error = True
                        elif text1.startswith(("HTTP_ERROR", "TIMEOUT", "CONNECTION_ERROR", "SSL_ERROR", "Error")):
                            if text1.startswith(("HTTP_ERROR", "TIMEOUT", "CONNECTION_ERROR", "SSL_ERROR", "Error")):
                                st.error(f"❌ **Failed to extract text from Version 1:**\n{text1}")
                            if text2.startswith(("HTTP_ERROR", "TIMEOUT", "CONNECTION_ERROR", "SSL_ERROR", "Error")):
                                st.error(f"❌ **Failed to extract text from Version 2:**\n{text2}")
                            st.info("💡 Try using the iframe preview or Screenshot Comparison instead.")
                            has_error = True

                        if has_error:
                            pass  # Error already displayed above
                        elif not text1 or not text2:
                            st.error("❌ One or both URLs returned empty content.")
                        else:
                            # Generate diff
                            import difflib
                            lines1 = text1.splitlines()
                            lines2 = text2.splitlines()
                            diff = difflib.unified_diff(lines1, lines2, fromfile='Version 1', tofile='Version 2', lineterm='', n=3)
                            diff_text = '\n'.join(diff)

                            # Calculate real changed lines (excluding diff headers)
                            diff_lines = [line for line in diff_text.splitlines()
                                        if line.startswith(('+', '-'))
                                        and not line.startswith(('---', '+++'))]

                            st.markdown("### 📊 Text Difference Analysis Results")

                            # Statistics
                            metric_col1, metric_col2, metric_col3 = st.columns(3)
                            with metric_col1:
                                st.metric("Version 1 Length", f"{len(text1):,} chars")
                            with metric_col2:
                                st.metric("Version 2 Length", f"{len(text2):,} chars")
                            with metric_col3:
                                st.metric("Changed Lines", len(diff_lines))

                            # Show diff
                            st.markdown("#### Detailed Differences")

                            if diff_lines:
                                st.markdown(
                                    "**Legend:** Lines starting with `-` (red) were removed, "
                                    "lines starting with `+` (green) were added."
                                )
                                st.code(diff_text, language="diff")
                            else:
                                st.success("✅ No text differences detected! The content appears identical.")

                            # Side-by-side text preview
                            with st.expander("📄 View Full Text Content"):
                                text_col1, text_col2 = st.columns(2)
                                with text_col1:
                                    chars_shown = min(5000, len(text1))
                                    st.markdown(f"**Version 1 Text** ({len(text1):,} total chars, showing first {chars_shown:,})")
                                    display_text1 = text1[:5000] + ("\n\n... (truncated)" if len(text1) > 5000 else "")
                                    st.text_area("", display_text1, height=300, key="text_display_1")
                                with text_col2:
                                    chars_shown = min(5000, len(text2))
                                    st.markdown(f"**Version 2 Text** ({len(text2):,} total chars, showing first {chars_shown:,})")
                                    display_text2 = text2[:5000] + ("\n\n... (truncated)" if len(text2) > 5000 else "")
                                    st.text_area("", display_text2, height=300, key="text_display_2")

                    except requests.exceptions.Timeout:
                        st.error("⏱️ Request timed out. The URLs may be too slow to respond (>30s).")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Connection error. Please check your internet connection.")
                    except Exception as e:
                        st.error(f"❌ Unexpected error during text extraction: {str(e)}")

        # Direct links
        st.markdown("---")
        st.markdown("### 🔗 Direct Links")
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            st.markdown(f"**Version 1:** [{url1}]({url1})")
        with link_col2:
            st.markdown(f"**Version 2:** [{url2}]({url2})")

# Tab 4: WARC Management
with tab4:
    st.header("📦 WARC Management")
    
    # Check credentials
    access_key, secret_key = get_ia_credentials()
    if not access_key or not secret_key:
        st.warning("⚠️ Internet Archive sync is disabled. Configure credentials in Streamlit settings.")
    else:
        st.success("✅ Internet Archive credentials configured")

    st.write("Store and sync WARC files with Internet Archive")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Upload WARC File", type=["warc", "warc.gz"])
        if uploaded_file:
            if save_warc_file(uploaded_file):
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
                # Compress if needed
                file_path = WARC_DIR / uploaded_file.name
                compressed_path = compress_warc(file_path)
                if compressed_path != file_path:
                    st.info(f"File compressed: {compressed_path.name}")
    
    with col2:
        if st.button("🔄 Sync All to Internet Archive", use_container_width=True):
            with st.spinner("Syncing to Internet Archive..."):
                local_warcs = list_local_warcs()
                if not local_warcs:
                    st.warning("No WARC files found locally")
                else:
                    for warc in local_warcs:
                        result = sync_to_internet_archive(warc)
                        st.write(f"{warc.name}: {result}")

    # Display local WARC files
    st.subheader("📂 Local WARC Files")
    local_warcs = list_local_warcs()
    if not local_warcs:
        st.info("No WARC files stored locally")
    else:
        for warc in local_warcs:
            info = get_warc_info(warc)
            with st.expander(f"📄 {info['name']}", expanded=False):
                st.write(f"Size: {info['size']}")
                st.write(f"Last Modified: {info['modified']}")
                
                # Add View button
                if st.button(f"👀 View Content", key=f"view_{info['name']}"):
                    view_warc_content(warc)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🔄 Sync", key=f"sync_{info['name']}"):
                        result = sync_to_internet_archive(warc)
                        st.write(result)
                with col2:
                    if st.button(f"⬇️ Download", key=f"download_{info['name']}"):
                        with open(warc, "rb") as file:
                            st.download_button(
                                label="Download WARC",
                                data=file,
                                file_name=info['name'],
                                mime="application/warc"
                            )
                with col3:
                    if st.button(f"❌ Delete", key=f"delete_{info['name']}"):
                        try:
                            warc.unlink()
                            st.success("File deleted")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting file: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Made with ❤️ to preserve the web 🫡😼 |
    <a href="https://github.com/shadowdevnotreal/wwwscope" target="_blank">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
