import time
import streamlit as st
import requests
import concurrent.futures
import random
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
@lru_cache(maxsize=100)
def rate_limited_request(url: str) -> requests.Response:
    """Make a rate-limited request to avoid overwhelming servers."""
    time.sleep(1)  # Basic rate limiting
    return requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)

def validate_url(url: str) -> bool:
    """Validate if the URL is accessible and properly formatted."""
    if not url.startswith(('http://', 'https://')):
        return False
    try:
        response = requests.head(url, timeout=5)
        return response.ok
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
    """Submit URL to Wayback Machine."""
    try:
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
            
        archive_url = f"https://web.archive.org/web/*/{url}"
        time.sleep(5)
        
        try:
            verify_response = rate_limited_request(archive_url)
            return f"✅ Archived Successfully: {archive_url}" if verify_response.ok else "❌ Archive verification failed"
        except requests.exceptions.Timeout:
            return "⚠️ Archive verification timed out, but submission may have succeeded"
            
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def submit_to_archive_today(url: str) -> str:
    """Submit URL to Archive.today using either Selenium or requests."""
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
                return f"Search manually at: https://archive.today/{url}"
    except Exception as e:
        return f"Error processing {service}: {str(e)}"

# Streamlit UI
st.title("🌍 WWWScope – Web Archiving & Retrieval")
st.write("Archive and retrieve web pages from multiple services.")

url = st.text_input("Enter the URL to archive or retrieve:")
mode = st.radio("Choose Mode:", ["Archive URL", "Retrieve Archived Versions"])

services = st.multiselect(
    "Select Services:",
    ["Wayback Machine", "Archive.today", "Memento"],
    default=["Wayback Machine"]
)

if st.button("Submit"):
    if not url:
        st.error("Please enter a valid URL.")
    else:
        if not validate_url(url):
            st.error("Please enter a valid URL starting with http:// or https://")
        else:
            results = {}
            progress_bar = st.progress(0)
            status_text = st.empty()

            with st.spinner("Processing requests..."):
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(services)) as executor:
                    future_to_service = {
                        executor.submit(process_service, service, url, mode): service 
                        for service in services
                    }
                    
                    for idx, future in enumerate(concurrent.futures.as_completed(future_to_service)):
                        service = future_to_service[future]
                        status_text.text(f"Processing {service}...")
                        progress_bar.progress((idx + 1) / len(services))
                        
                        try:
                            results[service] = future.result()
                        except Exception as e:
                            results[service] = f"Failed: {str(e)}"

            status_text.empty()
            progress_bar.empty()
            st.json(results)
