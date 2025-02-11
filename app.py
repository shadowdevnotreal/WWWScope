import time
import streamlit as st
import requests
import concurrent.futures
import random
import contextlib
from functools import lru_cache
from typing import Dict, Any

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

# Constants
ARCHIVE_TODAY_MIRRORS = [
    "https://archive.today",
    "https://archive.ph",
    "https://archive.is",
    "https://archive.fo"
]

ARCHIVE_SITES = {
    "Wayback Machine": "https://web.archive.org/save/",
    "Archive.today": "https://archive.today/submit/",
    "Memento": "http://timetravel.mementoweb.org/api/json/"
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
    """Submit URL to Archive.today with CAPTCHA warning."""
    result = "⚠️ Note: Archive.today may require CAPTCHA. If archiving fails, please:\n"
    result += "1. Visit archive.today manually\n"
    result += "2. Complete the CAPTCHA\n"
    result += "3. Try archiving again\n\n"
    
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
                        return result + f"✅ Archived Successfully: {archived_url}"
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
                return result + f"✅ Archived Successfully at {mirror}"
        except requests.exceptions.RequestException:
            continue

    return result + "❌ Archive.today failed on all mirrors."

def retrieve_memento_links(url: str) -> Dict[str, Any]:
    """Retrieve archived versions from Memento Web."""
    try:
        response = rate_limited_request(f"{ARCHIVE_SITES['Memento']}?url={url}")
        if response.ok:
            return response.json()
        return "No archived versions found."
    except Exception as e:
        return f"Error: {str(e)}"

def process_service(service: str, url: str, mode: str) -> str:
    """Process a single archive service request."""
    try:
        if mode == "Archive URL":
            if service == "Wayback Machine":
                return submit_to_wayback(url)
            elif service == "Archive.today":
                return submit_to_archive_today(url)
        else:
            if service == "Memento":
                return retrieve_memento_links(url)
            elif service == "Wayback Machine":
                return f"Check archived versions at: https://web.archive.org/web/*/{url}"
            elif service == "Archive.today":
                return f"Visit Archive.today homepage to search: https://archive.today"
    except Exception as e:
        return f"Error processing {service}: {str(e)}"

# Streamlit UI
st.title("🌍 WWWScope – Web Archiving & Retrieval")
st.write("Archive and retrieve web pages from multiple services.")

# URL input with better validation
url = st.text_input("Enter the URL to archive or retrieve:", 
                    placeholder="https://example.com")

# Create tabs for different modes
tab1, tab2 = st.tabs(["📥 Archive URL", "🔍 Retrieve Archives"])

with tab1:
    st.header("Archive URL")
    
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
            # Add http:// if missing
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
                        with ignore_thread_context_warning():
                            with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected_services)) as executor:
                                future_to_service = {
                                    executor.submit(process_service, service, url, "Archive URL"): service 
                                    for service in selected_services
                                }
                                
                                for idx, future in enumerate(concurrent.futures.as_completed(future_to_service)):
                                    service = future_to_service[future]
                                    status_text.text(f"Processing {service}...")
                                    progress_bar.progress((idx + 1) / len(selected_services))
                                    
                                    try:
                                        results[service] = future.result()
                                    except Exception as e:
                                        results[service] = f"Failed: {str(e)}"

                    status_text.empty()
                    progress_bar.empty()
                    
                    # Display results in a more attractive way
                    for service, result in results.items():
                        with st.expander(f"{service} Result", expanded=True):
                            if "✅" in str(result):
                                st.success(result)
                            elif "❌" in str(result):
                                st.error(result)
                            else:
                                st.info(result)

with tab2:
    st.header("Retrieve Archives")
    
    retrieve_service = st.radio(
        "Choose archive service to search:",
        ["All Services", "Wayback Machine Only", "Archive.today Only", "Memento Only"],
        horizontal=True
    )
    
    if st.button("🔍 Search Archives", use_container_width=True):
        if not url:
            st.error("Please enter a URL")
        else:
            url = clean_url(url)
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Direct links to archive services
            wayback_link = f"https://web.archive.org/web/*/{url}"
            archive_today_link = "https://archive.today"
            
            with st.expander("Quick Archive Links", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.link_button("Open Wayback Machine", wayback_link)
                with col2:
                    st.link_button("Open Archive.today", archive_today_link)

            services_to_check = []
            if retrieve_service == "All Services":
                services_to_check = ["Wayback Machine", "Archive.today", "Memento"]
            elif retrieve_service == "Wayback Machine Only":
                services_to_check = ["Wayback Machine"]
            elif retrieve_service == "Archive.today Only":
                services_to_check = ["Archive.today"]
            elif retrieve_service == "Memento Only":
                services_to_check = ["Memento"]

            results = {}
            with st.spinner("Searching archives..."):
                for service in services_to_check:
                    results[service] = process_service(service, url, "Retrieve Archived Versions")

            # Display results in a more attractive way
            for service, result in results.items():
                with st.expander(f"{service} Archives", expanded=True):
                    if isinstance(result, dict):
                        st.json(result)
                    else:
                        st.write(result)
                        if "web.archive.org" in str(result):
                            st.link_button("Open in Wayback Machine", str(result))
                        elif "archive.today" in str(result):
                            st.link_button("Open in Archive.today", str(result))

# Add footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Made with ❤️ to preserve the web 🫡😼 |
    <a href="https://github.com/shadowdevnotreal/wwwscope" target="_blank">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
