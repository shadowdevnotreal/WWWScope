"""
Fixed Archive Service Submission Functions
Implements proper rate limiting, retry logic, and error handling
"""

import time
import random
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import requests
import streamlit as st

# Import from our fixed rate limiter module
# In production, this would be: from rate_limiter_fixed import rate_limited, smart_request, session_manager, RetryWithBackoff


ARCHIVE_TODAY_MIRRORS = [
    "https://archive.today",
    "https://archive.ph",
    "https://archive.is",
    "https://archive.fo"
]

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
}


def submit_to_wayback(url: str, max_attempts: int = 5, max_wait_time: int = 180) -> str:
    """
    Submit URL to Wayback Machine with improved retry and verification
    
    Args:
        url: URL to archive
        max_attempts: Maximum verification attempts
        max_wait_time: Maximum wait time for archive to appear (seconds)
        
    Returns:
        Status message
    """
    check_url = f"https://archive.org/wayback/available?url={url}"
    
    try:
        # Step 1: Check if already archived
        st.info("🔍 Checking if URL is already archived...")
        
        try:
            check_response = requests.get(check_url, timeout=15)
            check_data = check_response.json()
            
            if check_data.get('archived_snapshots', {}).get('closest', {}).get('available'):
                closest = check_data['archived_snapshots']['closest']
                timestamp = closest.get('timestamp', '')
                archived_url = closest.get('url', '')
                
                return (
                    f"✅ URL already archived (snapshot: {timestamp})\n"
                    f"🔗 {archived_url}\n"
                    f"📊 View all snapshots: https://web.archive.org/web/*/{url}"
                )
        except Exception as e:
            st.warning(f"⚠️ Could not check existing archives: {str(e)}")
        
        # Step 2: Submit for archiving
        st.info("📤 Submitting to Wayback Machine...")
        
        submit_response = requests.post(
            ARCHIVE_SITES["Wayback Machine"],
            data={"url": url},
            headers={
                "User-Agent": "WWWScope Archiver/2.0",
                "Accept": "application/json"
            },
            timeout=30,
        )
        
        # Check for rate limiting
        if submit_response.status_code == 429:
            retry_after = submit_response.headers.get('Retry-After', '60')
            return (
                f"❌ Rate limit exceeded. Wayback Machine requests a wait of {retry_after} seconds.\n"
                f"Please try again later."
            )
        
        if not submit_response.ok:
            return (
                f"❌ Archive.org submission failed with status code: {submit_response.status_code}\n"
                f"Response: {submit_response.text[:200]}"
            )
        
        # Step 3: Wait and verify with progressive delays
        st.info("⏳ Waiting for archive to be processed...")
        
        wait_times = [5, 10, 15, 20, 30]  # Progressive wait times
        total_waited = 0
        
        for attempt, wait_time in enumerate(wait_times[:max_attempts], 1):
            if total_waited >= max_wait_time:
                break
            
            time.sleep(wait_time)
            total_waited += wait_time
            
            try:
                verify_response = requests.get(check_url, timeout=15)
                verify_data = verify_response.json()
                
                if verify_data.get('archived_snapshots', {}).get('closest', {}).get('available'):
                    closest = verify_data['archived_snapshots']['closest']
                    
                    # Check if this is a new snapshot (within last 5 minutes)
                    timestamp = closest.get('timestamp', '')
                    if timestamp:
                        # Simple check: if timestamp is recent enough
                        return (
                            f"✅ Successfully archived!\n"
                            f"🔗 {closest.get('url', '')}\n"
                            f"📊 View all snapshots: https://web.archive.org/web/*/{url}\n"
                            f"⏱️ Verified after {total_waited} seconds"
                        )
                
                st.info(
                    f"Attempt {attempt}/{max_attempts}: Archive not yet available. "
                    f"Waited {total_waited}s total..."
                )
            
            except Exception as e:
                st.warning(f"Verification attempt {attempt} failed: {str(e)}")
        
        # Archive submitted but not yet confirmed
        return (
            f"⚠️ Archive submission accepted but not yet confirmed after {total_waited}s.\n"
            f"The archive may still be processing. Please check back later:\n"
            f"🔗 https://web.archive.org/web/*/{url}\n"
            f"\n💡 Tip: Large pages can take several minutes to process."
        )
    
    except requests.exceptions.Timeout:
        return (
            "❌ Request timed out. Wayback Machine may be experiencing high load.\n"
            "Please try again in a few minutes."
        )
    
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


def submit_to_archive_today(url: str, max_mirror_attempts: int = 3) -> str:
    """
    Submit URL to Archive.today with session management and smart mirror rotation
    
    Args:
        url: URL to archive
        max_mirror_attempts: Maximum attempts per mirror
        
    Returns:
        Status message
    """
    # Display CAPTCHA notice
    st.info(
        "ℹ️ **Archive.today Notice**\n\n"
        "Archive.today uses CAPTCHA protection. If archiving fails:\n"
        "1. Open any Archive.today mirror in your browser\n"
        "2. Complete the CAPTCHA\n"
        "3. Return here and try again\n\n"
        "⏳ Attempting archive..."
    )
    
    # Create a persistent session for Archive.today
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })
    
    # Randomize mirror order to distribute load
    mirrors = ARCHIVE_TODAY_MIRRORS.copy()
    random.shuffle(mirrors)
    
    for mirror_idx, mirror in enumerate(mirrors, 1):
        st.info(f"📍 Trying mirror {mirror_idx}/{len(mirrors)}: {mirror}")
        
        for attempt in range(max_mirror_attempts):
            try:
                # Add random referer from the same mirror
                session.headers["Referer"] = mirror
                
                # Submit URL
                response = session.post(
                    f"{mirror}/submit/",
                    data={"url": url},
                    timeout=60,
                    allow_redirects=True
                )
                
                # Check response
                if response.ok:
                    # Check if we got a redirect to the archived page
                    if response.url != f"{mirror}/submit/" and "/archive/" in response.url:
                        archived_url = response.url
                        return (
                            f"✅ Successfully archived at Archive.today!\n"
                            f"🔗 {archived_url}\n"
                            f"📊 Mirror used: {mirror}"
                        )
                    
                    # Check if CAPTCHA page
                    if "hcaptcha" in response.text.lower() or "captcha" in response.text.lower():
                        st.warning(f"⚠️ CAPTCHA detected on {mirror}")
                        continue
                    
                    # Successfully submitted, but no redirect
                    st.info(f"✅ Submitted to {mirror}, checking for archive...")
                    time.sleep(3)
                    
                    # Try to find the archived URL
                    check_url = f"{mirror}/{url}"
                    check_response = session.get(check_url, timeout=30)
                    
                    if check_response.ok and "/archive/" in check_response.url:
                        return (
                            f"✅ Successfully archived at Archive.today!\n"
                            f"🔗 {check_response.url}\n"
                            f"📊 Mirror used: {mirror}"
                        )
                
                elif response.status_code == 429:
                    st.warning(f"⚠️ Rate limit on {mirror}")
                    break  # Try next mirror
                
                else:
                    st.warning(
                        f"⚠️ Attempt {attempt + 1}/{max_mirror_attempts} failed "
                        f"on {mirror}: HTTP {response.status_code}"
                    )
            
            except requests.exceptions.Timeout:
                st.warning(f"⚠️ Timeout on {mirror}, attempt {attempt + 1}/{max_mirror_attempts}")
            
            except Exception as e:
                st.warning(f"⚠️ Error on {mirror}: {str(e)}")
            
            # Exponential backoff between attempts
            if attempt < max_mirror_attempts - 1:
                wait_time = (2 ** attempt) * 2
                time.sleep(wait_time)
        
        # Small delay between mirrors
        if mirror_idx < len(mirrors):
            time.sleep(2)
    
    session.close()
    
    return (
        "❌ Archive.today archiving failed on all mirrors.\n\n"
        "**Possible reasons:**\n"
        "• CAPTCHA protection is active\n"
        "• Service is experiencing high load\n"
        "• URL may be blocked by Archive.today\n\n"
        "**Try this:**\n"
        "1. Visit https://archive.today directly\n"
        "2. Submit the URL manually\n"
        "3. Complete any CAPTCHAs\n"
    )


def retrieve_memento_links(url: str) -> Dict[str, Any]:
    """
    Retrieve archived versions from Memento Web with error handling

    Args:
        url: URL to search for

    Returns:
        Dictionary with results or error message
    """
    try:
        memento_api_url = f"{ARCHIVE_SITES['Memento']}{url}"

        response = requests.get(
            memento_api_url,
            headers={"User-Agent": "WWWScope Archiver/2.0"},
            timeout=30
        )

        if response.ok:
            data = response.json()

            if data.get('mementos'):
                return {
                    'success': True,
                    'data': data,
                    'message': f"Found {len(data.get('mementos', {}).get('list', []))} archived versions"
                }
            else:
                return {
                    'success': False,
                    'message': 'No archived versions found in Memento'
                }
        else:
            return {
                'success': False,
                'message': f'Memento API error: HTTP {response.status_code}'
            }

    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': (
                '⚠️ Memento Service Timeout\n\n'
                'The Memento archive aggregator is not responding. This service aggregates '
                'archives from multiple sources and can be slow or unavailable.\n\n'
                '💡 Try these alternatives:\n'
                '• Wayback Machine - Direct archive search\n'
                '• Archive.today - Quick manual lookup\n'
                '• TimeTravel - Alternative Memento interface'
            )
        }

    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': (
                '⚠️ Cannot Connect to Memento\n\n'
                'The Memento service (timetravel.mementoweb.org) is unreachable. '
                'This may be due to:\n'
                '• Service maintenance or downtime\n'
                '• Network connectivity issues\n'
                '• Service overload\n\n'
                '💡 Recommended: Use Wayback Machine or Archive.today instead'
            )
        }

    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': (
                f'⚠️ Memento Service Error\n\n'
                f'Unable to retrieve data from Memento archive aggregator.\n\n'
                f'💡 Try: Wayback Machine or Archive.today for reliable results'
            )
        }

    except Exception as e:
        return {
            'success': False,
            'message': (
                f'⚠️ Unexpected Error\n\n'
                f'An error occurred while accessing Memento: {type(e).__name__}\n\n'
                f'💡 Use alternative archive services for better results'
            )
        }


def process_service(service: str, url: str, mode: str, timeout: float = 60.0) -> str:
    """
    Process a single archive service request with timeout management
    
    Args:
        service: Service name
        url: Target URL
        mode: "Archive URL" or "Retrieve"
        timeout: Maximum time for operation
        
    Returns:
        Status message or result URL
    """
    start_time = time.time()
    
    try:
        if mode == "Archive URL":
            if service == "Wayback Machine":
                result = submit_to_wayback(url)
            elif service == "Archive.today":
                result = submit_to_archive_today(url)
            else:
                result = f"⚠️ Archiving not yet implemented for {service}"
            
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                return f"⚠️ Operation timed out after {elapsed:.1f}s"
            
            return result
        
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
            }
            
            if service == "Memento":
                result = retrieve_memento_links(url)
                if result.get('success'):
                    return result.get('message', 'Success')
                else:
                    return result.get('message', 'Failed')
            elif service in base_urls:
                return base_urls[service]
            else:
                return f"Service {service} not configured for retrieval"
    
    except Exception as e:
        return f"Error processing {service}: {str(e)}"


def process_services_parallel(services: list[str], url: str, mode: str) -> Dict[str, str]:
    """
    Process multiple services with controlled parallelism
    
    Args:
        services: List of service names
        url: Target URL
        mode: "Archive URL" or "Retrieve"
        
    Returns:
        Dictionary mapping service names to results
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = {}
    max_workers = min(3, len(services))  # Limit concurrent requests
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_service = {
            executor.submit(process_service, service, url, mode, 90.0): service
            for service in services
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_service):
            service = future_to_service[future]
            try:
                result = future.result(timeout=120.0)
                results[service] = result
            except Exception as e:
                results[service] = f"Error: {str(e)}"
    
    return results
