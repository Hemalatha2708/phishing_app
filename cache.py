"""
Simple in-memory caching for predictions.
Optional optimization to cache identical URL predictions.
"""

import hashlib
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Simple in-memory cache
_prediction_cache = {}

# Cache TTL in seconds
CACHE_TTL_SECONDS = 300  # 5 minutes


class CachedPrediction:
    """Represents a cached prediction with timestamp"""
    
    def __init__(self, score, classification, reasons):
        self.score = score
        self.classification = classification
        self.reasons = reasons
        self.created_at = datetime.now()
    
    def is_expired(self, ttl_seconds=CACHE_TTL_SECONDS):
        """Check if cache entry has expired"""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > ttl_seconds


def get_url_hash(url):
    """Generate hash for URL for caching"""
    return hashlib.md5(url.encode()).hexdigest()


def get_cached_prediction(url):
    """
    Retrieve cached prediction for URL if available and not expired.
    
    Args:
        url (str): URL to look up in cache
        
    Returns:
        dict or None: {'score', 'classification', 'reasons'} if found and valid, None otherwise
    """
    url_hash = get_url_hash(url)
    
    if url_hash not in _prediction_cache:
        return None
    
    cached = _prediction_cache[url_hash]
    
    if cached.is_expired():
        del _prediction_cache[url_hash]
        return None
    
    logger.debug(f"Cache hit for URL: {url}")
    return {
        'score': cached.score,
        'classification': cached.classification,
        'reasons': cached.reasons
    }


def cache_prediction(url, score, classification, reasons):
    """
    Cache a prediction result.
    
    Args:
        url (str): URL that was predicted
        score (float): Prediction score
        classification (str): Safe/Suspicious/Dangerous
        reasons (list): Risk reasons
    """
    url_hash = get_url_hash(url)
    _prediction_cache[url_hash] = CachedPrediction(score, classification, reasons)
    logger.debug(f"Cached prediction for URL: {url}")


def clear_cache():
    """Clear all cached predictions"""
    global _prediction_cache
    _prediction_cache.clear()
    logger.info("Prediction cache cleared")


def cleanup_expired_cache():
    """Remove all expired cache entries"""
    expired_keys = [
        key for key, cached in _prediction_cache.items()
        if cached.is_expired()
    ]
    
    for key in expired_keys:
        del _prediction_cache[key]
    
    if expired_keys:
        logger.debug(f"Removed {len(expired_keys)} expired cache entries")
