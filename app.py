import time
import streamlit as st
import requests
import concurrent.futures
import random

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

# Archive.today Mirrors
ARCHIVE_TODAY_MIRRORS = [
    "https://archive.today",
    "https://archive.ph",
    "https://archive.is",
    "https://archive.fo"
]

# Archive & Retrieve Endpoints
ARCHIVE_SITES = {
    "Wayback Machine": "https://web.archive.org/save/",
    "Archive.today": "https://archive.today/submit/",
    "Memento": "http://timetravel.mementoweb.org/api/json/"
}


def submit_to_wayback(url):
    try:
        # Send request to archive the URL
        response = requests.post(
            "https://web.archive.org/save/",
            data={"url": url},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30,
        )

        # Check if the archive request was successful
        if response.ok:
            # Extract the archive URL
            archive_url = f"https://web.archive.org/web/*/{url}"

            # Wait a few seconds before checking if it exists
            time.sleep(5)
            verify_response = requests.get(archive_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)

            # Check if the archive exists
            if verify_response.ok:
                return f"✅ Archived Successfully: {archive_url}"
            else:
                return "❌ Archive.org claimed success but the archive is missing."
        else:
            return "❌ Archive.org failed to archive the URL."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error: {e}"

# Ensure the mirrors list is not empty
if not ARCHIVE_TODAY_MIRRORS:
    raise ValueError("Error: Archive.today mirrors list is empty!")

# Function to submit URL to Archive.today
def submit_to_archive_today(url):
    
    # If Selenium is available, use it
    if SELENIUM_AVAILABLE:
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            for mirror in ARCHIVE_TODAY_MIRRORS:
                try:
                    driver.get(mirror)
                    time.sleep(3)

                    input_box = driver.find_element(By.NAME, "url")
                    input_box.send_keys(url)
                    input_box.submit()

                    time.sleep(10)  # Allow time for processing

                    archived_url = driver.current_url
                    driver.quit()
                    return f"✅ Archived Successfully: {archived_url}"
                except Exception:
                    continue  # Try next mirror

            driver.quit()
        except Exception as e:
            st.warning(f"Selenium failed: {e}")

    # If Selenium is not available, use Requests instead
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": random.choice(ARCHIVE_TODAY_MIRRORS)
    }

    for mirror in ARCHIVE_TODAY_MIRRORS:
        try:
            response = requests.post(
                f"{mirror}/submit/",
                data={"url": url},
                headers=headers,
                timeout=40  # Increased timeout
            )
            if response.ok:
                return f"✅ Archived Successfully at {mirror}"
        except requests.exceptions.RequestException:
            continue  # Try next mirror

    return "❌ Archive.today failed on all mirrors."


# Retrieve from Memento Web
def retrieve_memento_links(url):
    try:
        params = {"url": url}
        response = requests.get(ARCHIVE_SITES["Memento"], params=params, timeout=10)
        if response.ok:
            return response.json()
        else:
            return "No archived versions found."
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.title("🌍 WWWScope – Web Archiving & Retrieval")
st.write("Archive and retrieve web pages from multiple services.")

# 📌 **Add User Input for URL**
url = st.text_input("Enter the URL to archive or retrieve:")

# Choose mode
mode = st.radio("Choose Mode:", ["Archive URL", "Retrieve Archived Versions"])

# Select Services
services = st.multiselect(
    "Select Services:",
    ["Wayback Machine", "Archive.today", "Memento"],
    default=["Wayback Machine"]
)

# Button to Archive or Retrieve
if st.button("Submit"):
    if not url:
        st.error("Please enter a valid URL.")
    else:
        results = {}

        def process_service(service):
            if mode == "Archive URL":
                if service == "Wayback Machine":
                    return submit_to_wayback(url)
                elif service == "Archive.today":
                    return submit_to_archive_today(url)
            elif mode == "Retrieve Archived Versions":
                if service == "Wayback Machine":
                    return f"Check archived versions at: https://web.archive.org/web/*/{url}"
                elif service == "Archive.today":
                    return f"Search manually at: https://archive.today/{url}"
                elif service == "Memento":
                    return retrieve_memento_links(url)

        # Run services in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_service = {executor.submit(process_service, s): s for s in services}
            for future in concurrent.futures.as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    results[service] = future.result()
                except Exception as e:
                    results[service] = f"Error: {e}"

        # Display results
        st.json(results)
        
# Existing imports and configurations
import streamlit as st
import requests
import concurrent.futures

# 📌 **Add URL Input for Archiving & Retrieval**
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
        results = {}

        def process_service(service):
            if mode == "Archive URL":
                return requests.get(f"https://web.archive.org/save/{url}").url if service == "Wayback Machine" else f"https://archive.today/{url}"
            elif mode == "Retrieve Archived Versions":
                return f"Check archive at: https://web.archive.org/web/*/{url}" if service == "Wayback Machine" else f"Search manually at: https://archive.today/{url}"

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_service = {executor.submit(process_service, s): s for s in services}
            for future in concurrent.futures.as_completed(future_to_service):
                service = future_to_service[future]
                results[service] = future.result()

        st.json(results)

# 📌 **Existing WARC Upload Code Below**
st.header("📂 Upload & Sync WARC Files")
uploaded_file = st.file_uploader("Upload WARC File", type=["warc", "warc.gz"])
if uploaded_file:
    st.success(f"File uploaded: {uploaded_file.name}")

if st.button("🔄 Sync Local Archives"):
    st.write("Syncing WARC files to public storage...")
