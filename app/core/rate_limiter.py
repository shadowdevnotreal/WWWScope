"""
Advanced Rate Limiter for WWWScope
Fixes all rate limiting issues with token bucket algorithm
"""

import time
import threading
from collections import defaultdict
from typing import Dict, Optional
import requests
from functools import wraps
import streamlit as st


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter with per-service limits
    Prevents overwhelming archive services with requests
    """
    
    def __init__(self):
        self.buckets: Dict[str, Dict] = defaultdict(lambda: {
            'tokens': 0,
            'last_update': time.time(),
            'lock': threading.Lock()
        })
        
        # Service-specific rate limits (requests per second)
        self.rate_limits = {
            'wayback_machine': 0.2,    # 1 request per 5 seconds
            'archive_today': 0.1,       # 1 request per 10 seconds  
            'memento': 0.5,             # 1 request per 2 seconds
            'default': 0.33             # 1 request per 3 seconds
        }
        
        # Maximum burst size per service
        self.max_tokens = {
            'wayback_machine': 2,
            'archive_today': 1,
            'memento': 3,
            'default': 2
        }
    
    def _refill_tokens(self, service: str) -> None:
        """Refill tokens based on elapsed time"""
        bucket = self.buckets[service]
        now = time.time()
        elapsed = now - bucket['last_update']
        
        rate = self.rate_limits.get(service, self.rate_limits['default'])
        max_tokens = self.max_tokens.get(service, self.max_tokens['default'])
        
        # Add tokens based on time elapsed
        bucket['tokens'] = min(
            max_tokens,
            bucket['tokens'] + (elapsed * rate)
        )
        bucket['last_update'] = now
    
    def acquire(self, service: str, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens for a request
        
        Args:
            service: Service name for rate limiting
            tokens: Number of tokens to acquire (default 1)
            timeout: Maximum time to wait for tokens (None = wait forever)
            
        Returns:
            True if tokens acquired, False if timeout
        """
        bucket = self.buckets[service]
        start_time = time.time()
        
        with bucket['lock']:
            while True:
                self._refill_tokens(service)
                
                if bucket['tokens'] >= tokens:
                    bucket['tokens'] -= tokens
                    return True
                
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        return False
                
                # Calculate wait time for next token
                rate = self.rate_limits.get(service, self.rate_limits['default'])
                wait_time = min(1.0 / rate, 1.0)  # Max 1 second wait
                time.sleep(wait_time)
    
    def reset(self, service: str) -> None:
        """Reset rate limiter for a service"""
        if service in self.buckets:
            bucket = self.buckets[service]
            with bucket['lock']:
                bucket['tokens'] = self.max_tokens.get(
                    service, 
                    self.max_tokens['default']
                )
                bucket['last_update'] = time.time()


# Global rate limiter instance
rate_limiter = TokenBucketRateLimiter()


def rate_limited(service: str, tokens: int = 1, timeout: Optional[float] = 30.0):
    """
    Decorator for rate-limited functions
    
    Usage:
        @rate_limited('wayback_machine', tokens=1)
        def submit_to_wayback(url):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not rate_limiter.acquire(service, tokens=tokens, timeout=timeout):
                raise TimeoutError(f"Rate limit timeout for service: {service}")
            
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    # If we get rate limited, wait and retry once
                    st.warning(f"⏳ Rate limit hit for {service}, waiting 30 seconds...")
                    time.sleep(30)
                    
                    if rate_limiter.acquire(service, tokens=tokens, timeout=timeout):
                        return func(*args, **kwargs)
                    raise
                raise
        
        return wrapper
    return decorator


class RetryWithBackoff:
    """
    Exponential backoff retry mechanism
    """
    
    @staticmethod
    def retry(
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        exceptions: tuple = (requests.RequestException,)
    ):
        """
        Decorator for retry with exponential backoff
        
        Args:
            max_attempts: Maximum retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            exceptions: Tuple of exceptions to catch
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < max_attempts - 1:
                            # Calculate delay with exponential backoff
                            delay = min(
                                base_delay * (exponential_base ** attempt),
                                max_delay
                            )
                            
                            st.info(
                                f"⏳ Attempt {attempt + 1}/{max_attempts} failed. "
                                f"Retrying in {delay:.1f}s..."
                            )
                            time.sleep(delay)
                        else:
                            st.error(f"❌ All {max_attempts} attempts failed")
                
                raise last_exception
            
            return wrapper
        return decorator


def adaptive_timeout(url: str, base_timeout: float = 30.0) -> float:
    """
    Calculate adaptive timeout based on URL characteristics
    
    Args:
        url: Target URL
        base_timeout: Base timeout in seconds
        
    Returns:
        Adjusted timeout in seconds
    """
    # Longer timeout for archive.org (slower)
    if 'archive.org' in url or 'wayback' in url:
        return base_timeout * 2
    
    # Shorter timeout for fast services
    if 'archive.today' in url or 'archive.is' in url:
        return base_timeout * 0.8
    
    return base_timeout


# Improved rate_limited_request without cache
def smart_request(
    url: str,
    service: str = 'default',
    method: str = 'GET',
    timeout: Optional[float] = None,
    **kwargs
) -> requests.Response:
    """
    Make a rate-limited request with smart timeout and retry
    
    Args:
        url: Target URL
        service: Service name for rate limiting
        method: HTTP method
        timeout: Request timeout (None = adaptive)
        **kwargs: Additional arguments for requests
        
    Returns:
        Response object
    """
    # Calculate timeout if not provided
    if timeout is None:
        timeout = adaptive_timeout(url)
    
    # Set default headers
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    
    if 'User-Agent' not in kwargs['headers']:
        kwargs['headers']['User-Agent'] = 'WWWScope Archiver/2.0 (https://github.com/shadowdevnotreal/wwwscope)'
    
    # Acquire rate limit token
    if not rate_limiter.acquire(service, tokens=1, timeout=30.0):
        raise TimeoutError(f"Rate limit timeout for service: {service}")
    
    # Make request with retry
    @RetryWithBackoff.retry(
        max_attempts=3,
        base_delay=2.0,
        max_delay=30.0,
        exponential_base=2.0
    )
    def _make_request():
        response = requests.request(method, url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    
    return _make_request()


# Session manager for maintaining state across requests
class SessionManager:
    """Manage requests sessions with connection pooling"""
    
    def __init__(self):
        self.sessions: Dict[str, requests.Session] = {}
        self.lock = threading.Lock()
    
    def get_session(self, service: str) -> requests.Session:
        """Get or create a session for a service"""
        with self.lock:
            if service not in self.sessions:
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'WWWScope Archiver/2.0'
                })
                
                # Set up connection pooling
                adapter = requests.adapters.HTTPAdapter(
                    pool_connections=10,
                    pool_maxsize=20,
                    max_retries=0  # We handle retries ourselves
                )
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                
                self.sessions[service] = session
            
            return self.sessions[service]
    
    def close_all(self):
        """Close all sessions"""
        with self.lock:
            for session in self.sessions.values():
                session.close()
            self.sessions.clear()


# Global session manager
session_manager = SessionManager()
