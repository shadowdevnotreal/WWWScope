<p align="center">
  <img width="357"src="https://github.com/user-attachments/assets/c340b398-eadc-4f6e-92ee-2e2e716727be">
</p>

# WWWScope
WWWScope 🌍🔍 – Archive, compare, and sync web history with ease. Capture snapshots, track changes, and store archives effortlessly. 🚀

## 🌍 Multi-Site Archiver & Sync Tool

This tool allows you to archive web pages, compare archived versions, and sync WARC files between your local system, Amazon S3, and Internet Archive.

✅ Archive URLs to multiple services
 (Wayback Machine, Archive.today, ReplayWeb, Memento)
 
✅ Compare archived versions visually

✅ Upload & sync WARC files to S3 & Internet Archive

✅ Run locally OR deploy on Streamlit Cloud


---

## 📌 Features
### 🔹 Archiving

- Save web pages to multiple archive sites simultaneously.
- Retrieve past versions from archives.


### 🔹 Archive Comparison

- Compare two versions of archived content visually.


### 🔹 Sync WARC Files

- Store WARC files locally.
- Sync to public cloud storage (Amazon S3, Internet Archive).
- One-click "Sync" button to upload all local archives.


---

## 🚀 Running the App Locally

### 1️⃣ Install Dependencies

- Ensure Python 3.8+ is installed, then run:

```
pip install streamlit selenium requests webdriver-manager boto3 internetarchive difflib
```

### 2️⃣ Run the App

```
streamlit run app.py
```

📌 Open browser:

```
http://localhost:8501/ 
```

---

## 🌍 Deploying via GitHub & Streamlit Cloud

### 1️⃣ Push Your Code to GitHub

```git init
git add app.py requirements.txt
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```
### 2️⃣ Deploy on Streamlit Cloud

1. Go to Streamlit Cloud.
2. Click New App.
3. Select your GitHub repo.
- Branch: main
- Main file path: app.py

1 Click Deploy 🚀.

---

## 📂 Uploading & Syncing WARC Files

1. Upload a WARC file via the UI.
2. Click "Sync Local Archives to S3 & Internet Archive".
3. WARC files are uploaded to:

- Amazon S3 (public URL provided)
- Internet Archive (archive.org link generated)

---

## 🔧 Configuration

- Secrets (For Cloud Deployment)

- Store credentials securely using Streamlit Secrets:

1. In Streamlit Cloud, go to Secrets Manager.
2. Add:
```
S3_ACCESS_KEY = "your-access-key"
S3_SECRET_KEY = "your-secret-key"
```
3. Modify the script to use:
```
S3_ACCESS_KEY = st.secrets["S3_ACCESS_KEY"]
S3_SECRET_KEY = st.secrets["S3_SECRET_KEY"]
```
---
