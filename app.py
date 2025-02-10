import os
import streamlit as st
import requests
import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import internetarchive

@dataclass
class ArchiveResult:
    status: str
    message: str
    details: Optional[str] = None

class ArchiveStatus(Enum):
    SUCCESS = "✅"
    FAILURE = "❌"
    PENDING = "⏳"

class SeleniumConfig:
    def __init__(self):
        self.is_cloud = self._detect_environment()
        
    def _detect_environment(self) -> bool:
        """Detect if running in Streamlit Cloud"""
        return 'STREAMLIT_CLOUD' in os.environ
    
    def get_chrome_options(self) -> Options:
        """Get Chrome options based on environment"""
        options = Options()
        if self.is_cloud:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
        return options
    
    def get_driver(self) -> webdriver.Chrome:
        """Initialize Chrome driver based on environment"""
        options = self.get_chrome_options()
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

class WebArchiver:
    def __init__(self):
        self.config = SeleniumConfig()
        self.driver = None
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
        
    def initialize_driver(self):
        """Initialize Selenium driver"""
        try:
            self.driver = self.config.get_driver()
            return True
        except Exception as e:
            st.error(f"Failed to initialize Selenium: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up Selenium resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def archive_url(self, url: str, service: str) -> ArchiveResult:
        """Archive a URL using the specified service"""
        try:
            if service == "Wayback Machine":
                return self._wayback_archive(url)
            elif service == "Archive.today":
                return self._archive_today(url)
            elif service == "Memento":
                return self._memento_archive(url)
        except Exception as e:
            return ArchiveResult(
                status=ArchiveStatus.FAILURE.value,
                message=f"Error archiving: {str(e)}"
            )
    
    def _wayback_archive(self, url: str) -> ArchiveResult:
        """Handle Wayback Machine archiving"""
        try:
            response = requests.post(
                self.services["archive"]["Wayback Machine"],
                data={"url": url},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=30
            )
            
            if response.ok:
                time.sleep(5)  # Wait for processing
                archive_url = f"https://web.archive.org/web/*/{url}"
                verify_response = requests.get(
                    archive_url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=30
                )
                
                if verify_response.ok and "Sorry" not in verify_response.text:
                    return ArchiveResult(
                        status=ArchiveStatus.SUCCESS.value,
                        message=f"Archived Successfully: {archive_url}"
                    )
            return ArchiveResult(
                status=ArchiveStatus.FAILURE.value,
                message="Archive.org failed to archive"
            )
        except Exception as e:
            return ArchiveResult(
                status=ArchiveStatus.FAILURE.value,
                message=f"Error: {str(e)}"
            )
    
    def _archive_today(self, url: str) -> ArchiveResult:
        """Handle Archive.today archiving"""
        if not self.services["archive"]["Archive.today"]:
            return ArchiveResult(
                status=ArchiveStatus.FAILURE.value,
                message="No available Archive.today mirrors"
            )
        
        if self.driver:
            try:
                options = self.config.get_chrome_options()
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options
                )
                
                for mirror in self.services["archive"]["Archive.today"]:
                    try:
                        driver.get(mirror)
                        time.sleep(3)
                        
                        input_box = driver.find_element("name", "url")
                        input_box.send_keys(url)
                        input_box.submit()
                        time.sleep(10)  # Allow processing
                        
                        archived_url = driver.current_url
                        driver.quit()
                        return ArchiveResult(
                            status=ArchiveStatus.SUCCESS.value,
                            message=f"Archived Successfully: {archived_url}"
                        )
                    except Exception:
                        continue  # Try next mirror
                driver.quit()
            except Exception as e:
                st.warning(f"Selenium failed: {e}")
        
        # Fallback to Requests if Selenium fails
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": self.services["archive"]["Archive.today"][0]
        }
        
        for mirror in self.services["archive"]["Archive.today"]:
            try:
                response = requests.post(
                    f"{mirror}/submit/",
                    data={"url": url},
                    headers=headers,
                    timeout=40
                )
                if response.ok:
                    return ArchiveResult(
                        status=ArchiveStatus.SUCCESS.value,
                        message=f"Archived Successfully at {mirror}"
                    )
            except Exception:
                continue  # Try next mirror
        
        return ArchiveResult(
            status=ArchiveStatus.FAILURE.value,
            message="Archive.today failed on all mirrors"
        )
    
    def _memento_archive(self, url: str) -> ArchiveResult:
        """Handle Memento archiving"""
        try:
            response = requests.get(
                self.services["archive"]["Memento"],
                params={"url": url},
                timeout=10
            )
            if response.ok:
                return ArchiveResult(
                    status=ArchiveStatus.SUCCESS.value,
                    message="Archived Successfully",
                    details=response.json()
                )
            return ArchiveResult(
                status=ArchiveStatus.FAILURE.value,
                message="Memento archiving failed"
            )
        except Exception as e:
            return ArchiveResult(
                status=ArchiveStatus.FAILURE.value,
                message=f"Error: {str(e)}"
            )

class WARCManager:
    def __init__(self):
        self.upload_folder = "local_archives"
        os.makedirs(self.upload_folder, exist_ok=True)
        
    def upload_warc(self, file: st.uploaded_file_manager.UploadedFile) -> ArchiveResult:
        """Upload a WARC file to local storage"""
        try:
            file_path = os.path.join(self.upload_folder, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            return ArchiveResult(
                status=ArchiveStatus.SUCCESS.value,
                message=f"File uploaded to {file_path}"
            )
        except Exception as e:
            return ArchiveResult(
                status=ArchiveStatus.FAILURE.value,
                message=f"Error uploading: {str(e)}"
            )
    
    def sync_to_internet_archive(self, file_name: str) -> ArchiveResult:
        """Sync a local WARC file to Internet Archive"""
        try:
            file_path = os.path.join(self.upload_folder, file_name)
            item = internetarchive.upload(
                file_name,
                files=[file_path],
                metadata={"title": file_name}
            )
            return ArchiveResult(
                status=ArchiveStatus.SUCCESS.value,
                message=f"Uploaded to Internet Archive: {item.identifier}"
            )
        except Exception as e:
            return ArchiveResult(
                status=ArchiveStatus.FAILURE.value,
                message=f"Error uploading: {str(e)}"
            )

def main():
    st.title("🌍 WWWScope – Web Archiving & Retrieval")
    
    # Initialize components
    archiver = WebArchiver()
    warc_manager = WARCManager()
    
    try:
        if not archiver.initialize_driver():
            return
        
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
                results = {}
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_to_service = {
                        executor.submit(archiver.archive_url, url, service): service
                        for service in services
                    }
                    
                    for future in concurrent.futures.as_completed(future_to_service):
                        service = future_to_service[future]
                        try:
                            results[service] = future.result()
                        except Exception as e:
                            results[service] = ArchiveResult(
                                status=ArchiveStatus.FAILURE.value,
                                message=f"Error: {str(e)}"
                            )
                
                for service, result in results.items():
                    st.write(f"{service}: {result.message}")
                    if result.details:
                        st.code(result.details)
        
        # Retrieve Section
        elif mode == "Retrieve Archives":
            url = st.text_input("Enter URL to retrieve archives for:")
            services = st.multiselect(
                "Select Services:",
                ["Memento", "Internet Archive"],
                default=["Memento"]
            )
            
            if st.button("Retrieve"):
                results = {}
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_to_service = {
                        executor.submit(archiver.retrieve_archives, url, service): service
                        for service in services
                    }
                    
                    for future in concurrent.futures.as_completed(future_to_service):
                        service = future_to_service[future]
                        try:
                            results[service] = future.result()
                        except Exception as e:
                            results[service] = ArchiveResult(
                                status=ArchiveStatus.FAILURE.value,
                                message=f"Error: {str(e)}"
                            )
                
                for service, result in results.items():
                    st.write(f"{service}: {result.message}")
                    if result.details:
                        st.code(result.details)
        
        # WARC File Management Section
        st.header("📂 WARC File Management")
        
        # Upload WARC files
        uploaded_file = st.file_uploader("Upload WARC File", type=["warc", "warc.gz"])
        if uploaded_file:
            result = warc_manager.upload_warc(uploaded_file)
            st.write(result.message)
        
        # Sync WARC files to Internet Archive
        if st.button("🔄 Sync Local Archives to Internet Archive"):
            local_files = os.listdir(warc_manager.upload_folder)
            if not local_files:
                st.warning("No local archives found.")
            else:
                results = {}
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_to_file = {
                        executor.submit(warc_manager.sync_to_internet_archive, f): f
                        for f in local_files
                    }
                    
                    for future in concurrent.futures.as_completed(future_to_file):
                        file_name = future_to_file[future]
                        try:
                            results[file_name] = future.result()
                        except Exception as e:
                            results[file_name] = ArchiveResult(
                                status=ArchiveStatus.FAILURE.value,
                                message=f"Error: {str(e)}"
                            )
                
                for file_name, result in results.items():
                    st.write(f"{file_name}: {result.message}")
    
    finally:
        archiver.cleanup()

if __name__ == "__main__":
    main()
