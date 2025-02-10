import streamlit as st
import requests
import os
import boto3
import internetarchive
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

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
