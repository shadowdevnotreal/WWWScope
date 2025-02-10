import time
import streamlit as st
import requests
import os
import boto3
import internetarchive
import concurrent.futures

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

# Archive & Retrieve Endpoints
ARCHIVE_SITES = {
    "Wayback Machine": "https://web.archive.org/save/",
    "Archive.today": "https://archive.today/submit/",
    "Memento": "http://timetravel.mementoweb.org/api/json/"
}

# Submit URL to Wayback Machine
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

# S3 & Internet Archive Configuration (Add to Streamlit Secrets for Security)
# S3_BUCKET = "your-public-s3-bucket"
# S3_ACCESS_KEY = st.secrets["S3_ACCESS_KEY"]
# S3_SECRET_KEY = st.secrets["S3_SECRET_KEY"]

## To run public bucket 
# import boto3
# import botocore
# s3 = boto3.client("s3", config=boto3.session.Config(signature_version=botocore.UNSIGNED))
# bucket_name = "your-public-bucket-name"

# Example: List public files in the S3 bucket
# response = s3.list_objects_v2(Bucket=bucket_name)
# files = [obj["Key"] for obj in response.get("Contents", [])]
# st.write("Public files in S3 bucket:", files)

# Ensure Upload Directory Exists
UPLOAD_FOLDER = "local_archives"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Selenium WebDriver
def get_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# Securely Upload WARC to S3
def upload_warc_to_s3(file_path, file_name):
    s3 = boto3.client("s3", aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_KEY)
    try:
        s3.upload_file(file_path, S3_BUCKET, file_name, ExtraArgs={'ACL': 'public-read'})
        return f"https://{S3_BUCKET}.s3.amazonaws.com/{file_name}"
    except Exception as e:
        return f"Error uploading to S3: {e}"

# Upload WARC to Internet Archive
def upload_warc_to_internet_archive(file_path, file_name):
    try:
        item = internetarchive.upload(file_name, files=[file_path], metadata={'title': file_name})
        return f"https://archive.org/details/{file_name}"
    except Exception as e:
        return f"Error uploading to Internet Archive: {e}"

# Streamlit UI
st.title("🌍 Archive Sync & Management")
st.write("Sync your local WARC archives to public cloud storage.")

# File Upload Section
uploaded_file = st.file_uploader("Upload WARC File", type=["warc", "warc.gz"])
if uploaded_file:
    file_name = uploaded_file.name
    file_path = os.path.join(UPLOAD_FOLDER, file_name)

    # Save file locally
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File uploaded and stored at: {file_path}")

# Sync Button to Upload Local Archives to Cloud
if st.button("🔄 Sync Local Archives to S3 & Internet Archive"):
    local_files = os.listdir(UPLOAD_FOLDER)
    
    if not local_files:
        st.warning("No local archives found.")
    else:
        results = {}

        def sync_file(file_name):
            file_path = os.path.join(UPLOAD_FOLDER, file_name)
            s3_url = upload_warc_to_s3(file_path, file_name)
            ia_url = upload_warc_to_internet_archive(file_path, file_name)
            return {"s3_url": s3_url, "internet_archive_url": ia_url}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(sync_file, f): f for f in local_files}
            for future in concurrent.futures.as_completed(future_to_file):
                file_name = future_to_file[future]
                try:
                    results[file_name] = future.result()
                except Exception as e:
                    results[file_name] = f"Error: {e}"

        st.json(results)
