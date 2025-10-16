"""
Fixed Internet Archive Upload Module
Fixes all upload errors with proper retry, validation, and progress tracking
"""

import os
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import streamlit as st
import internetarchive
from internetarchive import get_item


class InternetArchiveUploader:
    """
    Robust Internet Archive uploader with retry logic and validation
    """
    
    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize uploader with credentials
        
        Args:
            access_key: IA S3 access key
            secret_key: IA S3 secret key
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.config = self._get_config()
    
    def _get_config(self) -> Optional[Dict[str, Any]]:
        """Get IA configuration"""
        if not self.access_key or not self.secret_key:
            return None
        
        return {
            's3': {
                'access': self.access_key,
                'secret': self.secret_key
            }
        }
    
    def _create_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Create comprehensive metadata for Internet Archive item
        
        Args:
            file_path: Path to WARC file
            
        Returns:
            Metadata dictionary
        """
        file_stats = file_path.stat()
        
        return {
            'title': f'WWWScope Archive - {file_path.stem}',
            'mediatype': 'web',
            'collection': 'opensource',
            'description': (
                f'Web archive created by WWWScope archiver. '
                f'Original file: {file_path.name}'
            ),
            'creator': 'WWWScope Archiver',
            'subject': ['web archiving', 'WARC', 'preservation'],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'language': 'eng',
            'source': 'WWWScope (https://github.com/shadowdevnotreal/wwwscope)',
            
            # Technical metadata
            'warc_file_name': file_path.name,
            'warc_file_size': file_stats.st_size,
            'warc_created_date': datetime.fromtimestamp(
                file_stats.st_ctime
            ).strftime('%Y-%m-%d %H:%M:%S'),
            'warc_modified_date': datetime.fromtimestamp(
                file_stats.st_mtime
            ).strftime('%Y-%m-%d %H:%M:%S'),
            
            # Checksums for verification
            'md5_checksum': self._calculate_md5(file_path),
            'sha256_checksum': self._calculate_sha256(file_path),
            
            # License
            'licenseurl': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'rights': 'This archive is released under CC0 1.0 Universal (Public Domain)'
        }
    
    @staticmethod
    def _calculate_md5(file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate MD5 checksum of file"""
        md5_hash = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                md5_hash.update(chunk)
        
        return md5_hash.hexdigest()
    
    @staticmethod
    def _calculate_sha256(file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def _generate_identifier(self, file_path: Path) -> str:
        """
        Generate unique identifier for Internet Archive item
        
        Args:
            file_path: Path to WARC file
            
        Returns:
            Unique identifier string
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_hash = self._calculate_md5(file_path)[:8]
        
        return f"wwwscope_{timestamp}_{file_hash}"
    
    def _verify_upload(self, identifier: str, file_path: Path) -> bool:
        """
        Verify that upload was successful
        
        Args:
            identifier: IA item identifier
            file_path: Original file path
            
        Returns:
            True if upload verified successfully
        """
        try:
            # Get the item from Internet Archive
            item = get_item(identifier)
            
            # Check if item exists
            if not item.exists:
                return False
            
            # Check if file is in the item
            file_name = file_path.name
            if file_name not in [f['name'] for f in item.files]:
                return False
            
            # Verify file size matches
            remote_file = next(f for f in item.files if f['name'] == file_name)
            local_size = file_path.stat().st_size
            
            if remote_file.get('size') != str(local_size):
                st.warning(f"⚠️ Size mismatch: local={local_size}, remote={remote_file.get('size')}")
                return False
            
            return True
        
        except Exception as e:
            st.error(f"Verification failed: {str(e)}")
            return False
    
    def upload_with_retry(
        self,
        file_path: Path,
        max_attempts: int = 3,
        chunk_size: int = 10 * 1024 * 1024  # 10MB chunks
    ) -> Dict[str, Any]:
        """
        Upload WARC file to Internet Archive with retry logic
        
        Args:
            file_path: Path to WARC file
            max_attempts: Maximum upload attempts
            chunk_size: Size of upload chunks in bytes
            
        Returns:
            Dictionary with upload results
        """
        if not self.config:
            return {
                'success': False,
                'message': '❌ Internet Archive credentials not configured',
                'identifier': None,
                'url': None
            }
        
        if not file_path.exists():
            return {
                'success': False,
                'message': f'❌ File not found: {file_path}',
                'identifier': None,
                'url': None
            }
        
        # Generate identifier
        identifier = self._generate_identifier(file_path)
        
        # Create metadata
        metadata = self._create_metadata(file_path)
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                status_text.text(f"📤 Upload attempt {attempt + 1}/{max_attempts}...")
                progress_bar.progress((attempt + 1) / (max_attempts + 1))
                
                # Perform upload
                response = internetarchive.upload(
                    identifier,
                    files=[str(file_path)],
                    metadata=metadata,
                    config=self.config,
                    queue_derive=True,
                    verify=True,
                    checksum=True,
                    delete=False  # Don't delete local file
                )
                
                # Wait for upload to complete
                status_text.text("⏳ Verifying upload...")
                time.sleep(5)  # Give IA time to process
                
                # Verify upload
                if self._verify_upload(identifier, file_path):
                    progress_bar.progress(1.0)
                    status_text.empty()
                    progress_bar.empty()
                    
                    return {
                        'success': True,
                        'message': '✅ Successfully uploaded to Internet Archive',
                        'identifier': identifier,
                        'url': f'https://archive.org/details/{identifier}',
                        'metadata': metadata
                    }
                else:
                    raise Exception("Upload verification failed")
            
            except Exception as e:
                last_exception = e
                
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt) * 5  # Exponential backoff: 5s, 10s, 20s
                    status_text.text(
                        f"⚠️ Upload failed: {str(e)}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    status_text.empty()
                    progress_bar.empty()
        
        # All attempts failed
        return {
            'success': False,
            'message': f'❌ Upload failed after {max_attempts} attempts: {str(last_exception)}',
            'identifier': identifier,
            'url': None,
            'error': str(last_exception)
        }
    
    def bulk_upload(
        self,
        file_paths: list[Path],
        delay_between_uploads: float = 5.0
    ) -> list[Dict[str, Any]]:
        """
        Upload multiple WARC files with rate limiting
        
        Args:
            file_paths: List of file paths to upload
            delay_between_uploads: Delay between uploads in seconds
            
        Returns:
            List of upload results
        """
        results = []
        
        for i, file_path in enumerate(file_paths):
            st.info(f"📦 Uploading {i + 1}/{len(file_paths)}: {file_path.name}")
            
            result = self.upload_with_retry(file_path)
            results.append(result)
            
            if i < len(file_paths) - 1:
                st.info(f"⏳ Waiting {delay_between_uploads}s before next upload...")
                time.sleep(delay_between_uploads)
        
        return results


def get_ia_credentials() -> tuple[Optional[str], Optional[str]]:
    """
    Safely get Internet Archive credentials from Streamlit secrets
    
    Returns:
        Tuple of (access_key, secret_key) or (None, None)
    """
    try:
        access_key = st.secrets.get("ia_access_key")
        secret_key = st.secrets.get("ia_secret_key")
        
        if access_key and secret_key:
            return access_key, secret_key
        
        return None, None
    
    except Exception:
        return None, None


def upload_to_internet_archive(file_path: Path) -> str:
    """
    Upload WARC file to Internet Archive (Fixed version)
    
    Args:
        file_path: Path to WARC file
        
    Returns:
        Status message string
    """
    access_key, secret_key = get_ia_credentials()
    
    if not access_key or not secret_key:
        return "❌ Internet Archive credentials not configured"
    
    try:
        uploader = InternetArchiveUploader(access_key, secret_key)
        result = uploader.upload_with_retry(file_path)
        
        if result['success']:
            return f"{result['message']}\n🔗 {result['url']}"
        else:
            return result['message']
    
    except Exception as e:
        return f"❌ Upload failed: {str(e)}"


def sync_to_internet_archive(file_path: Path) -> str:
    """
    Sync WARC file to Internet Archive (wrapper for compatibility)
    
    Args:
        file_path: Path to WARC file
        
    Returns:
        Status message string
    """
    return upload_to_internet_archive(file_path)


def batch_sync_to_internet_archive(file_paths: list[Path]) -> list[str]:
    """
    Sync multiple WARC files to Internet Archive
    
    Args:
        file_paths: List of file paths
        
    Returns:
        List of status messages
    """
    access_key, secret_key = get_ia_credentials()
    
    if not access_key or not secret_key:
        return ["❌ Internet Archive credentials not configured"] * len(file_paths)
    
    try:
        uploader = InternetArchiveUploader(access_key, secret_key)
        results = uploader.bulk_upload(file_paths, delay_between_uploads=10.0)
        
        messages = []
        for result in results:
            if result['success']:
                messages.append(f"{result['message']}\n🔗 {result['url']}")
            else:
                messages.append(result['message'])
        
        return messages
    
    except Exception as e:
        return [f"❌ Batch upload failed: {str(e)}"] * len(file_paths)
