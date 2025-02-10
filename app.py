import streamlit as st
import os
import internetarchive
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from enum import Enum

@dataclass
class ArchiveResult:
    status: str
    message: str
    details: Optional[str] = None

class ArchiveStatus(Enum):
    SUCCESS = "✅"
    FAILURE = "❌"
    PENDING = "⏳"

class WebArchiver:
    def __init__(self):
        self.services = {
            "archive": {
                "Wayback Machine": "https://web.archive.org/save/",
                "Archive.today": ["https://archive.today", "https://archive.ph"],
                "Memento": "http://timetravel.mementoweb.org/api/json/"
            },
            "retrieve": {
                "Memento": "http://timetravel.mementoweb.org/api/json/",
                "Internet Archive": "https://archive.org"
            }
        }
        
    def archive_url(self, url: str, service: str) -> dict:
        """Archive a URL using the specified service"""
        try:
            if service == "Wayback Machine":
                return self._wayback_archive(url)
            elif service == "Archive.today":
                return self._archive_today(url)
            elif service == "Memento":
                return self._memento_archive(url)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def retrieve_archives(self, url: str, service: str) -> dict:
        """Retrieve archived versions of a URL"""
        try:
            if service == "Memento":
                return self._retrieve_memento(url)
            elif service == "Internet Archive":
                return self._retrieve_internet_archive(url)
        except Exception as e:
            return {"status": "error", "message": str(e)}

class WARCManager:
    def __init__(self):
        self.upload_folder = Path("local_archives")
        self.upload_folder.mkdir(exist_ok=True, parents=True)
        
    def upload_warc(self, file: st.uploaded_file_manager.UploadedFile) -> ArchiveResult:
        """Upload a WARC file to local storage"""
        try:
            # Get file properties
            file_name = file.name
            
            # Validate file type
            if not file_name.lower().endswith(('.warc', '.warc.gz')):
                return ArchiveResult(
                    status=ArchiveStatus.FAILURE.value,
                    message="Invalid file type. Only .warc and .warc.gz files are allowed"
                )
            
            # Write file to disk
            file_path = self.upload_folder / file_name
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            
            return ArchiveResult(
                status=ArchiveStatus.SUCCESS.value,
                message=f"File uploaded successfully: {file_name}"
            )
        except Exception as e:
            return ArchiveResult(
                status=ArchiveStatus.FAILURE.value,
                message=f"Error uploading file: {str(e)}"
            )

def main():
    st.title("WARC File Uploader")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a WARC file", type=["warc", "warc.gz"])
    
    if uploaded_file is not None:
        warc_manager = WARCManager()
        result = warc_manager.upload_warc(uploaded_file)
        st.write(result.message)

if __name__ == "__main__":
    main()
        
            
def main():
    st.title("🌍 WWWScope – Web Archiving & Retrieval")
    
    # Archive & Retrieve Section
    mode = st.radio("Choose Mode:", ["Archive URL", "Retrieve Archives"])
    
    if mode == "Archive URL":
        url = st.text_input("Enter URL to archive:")
        services = st.multiselect(
            "Select Services:",
            ["Wayback Machine", "Archive.today", "Memento"],
            default=["Wayback Machine"]
        )
        
        if st.button("Archive"):
            archiver = WebArchiver()
            results = {}
            
            with ThreadPoolExecutor() as executor:
                future_to_service = {
                    executor.submit(archiver.archive_url, url, service): service
                    for service in services
                }
                
                for future in future_to_service:
                    service = future_to_service[future]
                    try:
                        results[service] = future.result()
                    except Exception as e:
                        results[service] = {"status": "error", "message": str(e)}
            
            for service, result in results.items():
                st.write(f"{service}: {result['message']}")
    
    # Retrieve Section
    elif mode == "Retrieve Archives":
        url = st.text_input("Enter URL to retrieve archives for:")
        services = st.multiselect(
            "Select Services:",
            ["Memento", "Internet Archive"],
            default=["Memento"]
        )
        
        if st.button("Retrieve"):
            archiver = WebArchiver()
            results = {}
            
            with ThreadPoolExecutor() as executor:
                future_to_service = {
                    executor.submit(archiver.retrieve_archives, url, service): service
                    for service in services
                }
                
                for future in future_to_service:
                    service = future_to_service[future]
                    try:
                        results[service] = future.result()
                    except Exception as e:
                        results[service] = {"status": "error", "message": str(e)}
            
            for service, result in results.items():
                st.write(f"{service}: {result['message']}")
    
    # WARC File Management Section
    st.header("📂 WARC File Management")
    warc_manager = WARCManager()
    
    # Upload WARC files
    uploaded_file = st.file_uploader("Upload WARC File", type=["warc", "warc.gz"])
    if uploaded_file:
        result = warc_manager.upload_warc(uploaded_file)
        st.write(result["message"])
    
    # Sync WARC files to Internet Archive
    if st.button("🔄 Sync Local Archives to Internet Archive"):
        local_files = os.listdir(warc_manager.upload_folder)
        if not local_files:
            st.warning("No local archives found.")
        else:
            results = {}
            
            with ThreadPoolExecutor() as executor:
                future_to_file = {
                    executor.submit(warc_manager.sync_to_internet_archive, f): f
                    for f in local_files
                }
                
                for future in future_to_file:
                    file_name = future_to_file[future]
                    try:
                        results[file_name] = future.result()
                    except Exception as e:
                        results[file_name] = {
                            "status": "error",
                            "message": str(e)
                        }
            
            for file_name, result in results.items():
                st.write(f"{file_name}: {result['message']}")

if __name__ == "__main__":
    main()
