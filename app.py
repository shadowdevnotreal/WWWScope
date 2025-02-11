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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api import app as api_app
import threading

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

# Add CORS middleware to API
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_api():
    """Run the FastAPI server"""
    uvicorn.run(api_app, host="0.0.0.0", port=8000)

def main():
    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()


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
    """Display WARC file content in a viewer"""
    st.markdown("### 📄 WARC Content Viewer")
    
    try:
        with open(warc_file, 'rb') as stream:
            for record in ArchiveIterator(stream):
                if record.rec_type == 'response':
                    # Get content
                    content = record.content_stream().read().decode('utf-8', errors='ignore')
                    headers = record.http_headers
                    url = record.rec_headers.get_header('WARC-Target-URI')
                    
                    # Display in expandable section
                    with st.expander(f"🔗 {url}", expanded=False):
                        st.markdown("#### Headers:")
                        st.code(str(headers))
                        st.markdown("#### Content:")
                        # Create iframe for HTML content
                        components.html(content, height=600, scrolling=True)
                        
                        # Add download button for this page
                        st.download_button(
                            "💾 Download Page Content",
                            content,
                            file_name=f"page_{url.split('/')[-1]}.html",
                            mime="text/html"
                        )
    except Exception as e:
        st.error(f"Error reading WARC file: {str(e)}")

# Constants
ARCHIVE_TODAY_MIRRORS = [
    "https://archive.today",
    "https://archive.ph",
    "https://archive.is",
    "https://archive.fo"
]

# Add to your ARCHIVE_SITES constant
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
    "WebCite": "http://www.webcitation.org/"
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
        
        def get_enhanced_metadata(file_path: Path, url: str = None) -> dict:
    """Get enhanced metadata for Internet Archive upload"""
    return {
        "title": f"WWWScope Web Archive: {file_path.name}",
        "mediatype": "web",
        "collection": "opensource",
        "creator": "WWWScope Web Archiving Tool",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "subject": ["web archive", "digital preservation", "wwwscope"],
        "description": f"""Web archive created using WWWScope.
        File: {file_path.name}
        URL: {url if url else 'Not specified'}
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Tool: WWWScope + ReplayWeb
        """,
        "notes": "Created with WWWScope - Open Source Web Archiving Tool",
        "license": "http://creativecommons.org/publicdomain/zero/1.0/"
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

@lru_cache(maxsize=100)
def rate_limited_request(url: str) -> requests.Response:    
    """Make a rate-limited request to avoid overwhelming servers."""
    time.sleep(1)  # Basic rate limiting
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
                st.info("Screenshot comparison feature coming soon!")
                # You can add screenshot comparison logic here
        
        with col2:
            if st.button("📊 Text Diff"):
                st.info("Text difference analysis coming soon!")
                # You can add text difference logic here
        
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
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        st.error(f"Failed to initialize Chrome driver: {e}")
        return None

def submit_to_wayback(url: str) -> str:
    """Submit URL to Wayback Machine with improved verification."""
    try:
        # First check if URL already exists
        check_url = f"https://archive.org/wayback/available?url={url}"
        check_response = requests.get(check_url, timeout=30)
        check_data = check_response.json()
        
        if check_data.get('archived_snapshots', {}).get('closest', {}).get('available'):
            return f"✅ URL already archived: https://web.archive.org/web/*/{url}"
        
        # If not archived, submit for archiving
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
            
        # Wait and verify
        time.sleep(5)
        verify_url = f"https://archive.org/wayback/available?url={url}"
        verify_response = requests.get(verify_url, timeout=30)
        verify_data = verify_response.json()
        
        if verify_data.get('archived_snapshots', {}).get('closest', {}).get('available'):
            return f"✅ Successfully archived: https://web.archive.org/web/*/{url}"
        else:
            return "⚠️ Archive submission accepted but not yet available"
            
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
        

def submit_to_archive_today(url: str) -> str:
    """Submit URL to Archive.today with improved CAPTCHA handling."""
    message = """
    ⚠️ Archive.today CAPTCHA Notice:
    
    If archiving fails due to CAPTCHA:
    1. Open Archive.today in a new tab
    2. Solve the CAPTCHA once
    3. Return here and try again
    
    Status: Attempting archive...
    """
    st.info(message)
    
    if SELENIUM_AVAILABLE:
        driver = get_selenium_driver()
        if driver:
            try:
                for mirror in ARCHIVE_TODAY_MIRRORS:
                    try:
                        driver.get(mirror)
                        time.sleep(3)

                        input_box = driver.find_element(By.NAME, "url")
                        input_box.send_keys(url)
                        input_box.submit()

                        time.sleep(10)
                        archived_url = driver.current_url
                        driver.quit()
                        return f"✅ Archived Successfully: {archived_url}"
                    except Exception:
                        continue
                driver.quit()
            except Exception as e:
                st.warning(f"Selenium failed: {e}")

    # Fallback to requests if Selenium fails or is not available
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
                timeout=40
            )
            if response.ok:
                return f"✅ Archived Successfully at {mirror}"
        except requests.exceptions.RequestException:
            continue

    return "❌ Archive.today failed on all mirrors."
    

def retrieve_memento_links(url: str) -> Dict[str, Any]:
    """Retrieve archived versions from Memento Web."""
    try:
        response = rate_limited_request(f"{ARCHIVE_SITES['Memento']}?url={url}")
        if response.ok:
            return response.json()
        return "No archived versions found."
    except Exception as e:
        return f"Error: {str(e)}"

# Update process_service function
def process_service(service: str, url: str, mode: str) -> str:
    """Process a single archive service request."""
    try:
        if mode == "Archive URL":
            if service == "Wayback Machine":
                return submit_to_wayback(url)
            elif service == "Archive.today":
                return submit_to_archive_today(url)
            # Add other services as needed
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

# In Tab 2 (Retrieve Archives), replace the existing results display with this:
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

            # Results display
            with st.expander("🔍 Search Results", expanded=True):
                st.info("Searching archives...")
                results = {}
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, service in enumerate(services_to_check):
                    status_text.text(f"🔍 Checking {service}...")
                    progress_bar.progress((idx + 1) / len(services_to_check))
                    
                    result = process_service(service, url, "Retrieve")
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
            for service, result in results.items():
                with st.expander(f"{service} Results", expanded=True):
                    if isinstance(result, dict):
                        st.json(result)
                    else:
                        st.write(result)
                    
                    # Add timestamp
                    st.caption(f"Search completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Tab 3: Compare Archives
with tab3:
    st.header("🔄 Archive Comparison")
    st.write("Compare two versions of archived content visually.")
    
    url1 = st.text_input("First Archive URL:")
    url2 = st.text_input("Second Archive URL:")
    
    if st.button("Compare Archives", use_container_width=True):
        if url1 and url2:
            compare_archives(url1, url2)
        else:
            st.warning("Please enter both archive URLs to compare")

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
            # In Tab 4, after displaying file info
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

if __name__ == "__main__":
    main()
