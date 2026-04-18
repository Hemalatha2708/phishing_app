"""
Feature extraction module for phishing detection.
Single source of truth for URL feature extraction logic.
"""

import re
from urllib.parse import urlparse


# Compile regex patterns once at module load for performance
IP_PATTERN = re.compile(r'(\d{1,3}\.){3}\d{1,3}')

# Constants
SUSPICIOUS_KEYWORDS = ['login', 'secure', 'verify', 'account', 'update', 'bank', 'signin', 'confirm', 'password']
URL_SHORTENERS = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'rb.gy']
SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq']


def validate_url(url):
    """
    Validate URL format before feature extraction.
    
    Args:
        url (str): URL to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"
    
    url = url.strip()
    
    if len(url) < 5:
        return False, "URL is too short"
    
    if len(url) > 2048:
        return False, "URL is too long"
    
    if not (url.startswith('http://') or url.startswith('https://')):
        return False, "URL must start with http:// or https://"
    
    try:
        result = urlparse(url)
        if not result.netloc:
            return False, "URL must have a valid domain"
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"
    
    return True, None


def extract_features(url):
    """
    Extract 16 features from a URL for ML prediction.
    
    Args:
        url (str): URL to extract features from
        
    Returns:
        list: 16 features for model prediction
        
    Raises:
        ValueError: If URL is invalid or feature extraction fails
    """
    # Validate URL first
    is_valid, error_msg = validate_url(url)
    if not is_valid:
        raise ValueError(error_msg)
    
    url = url.strip()
    
    try:
        domain = urlparse(url).netloc
        features = []
        
        # 1. URL length
        features.append(len(url))
        
        # 2. Dot count
        features.append(url.count('.'))
        
        # 3. Slash count
        features.append(url.count('/'))
        
        # 4-7. Suspicious symbols
        features.append(url.count('@'))
        features.append(url.count('-'))
        features.append(url.count('='))
        features.append(url.count('?'))
        
        # 8. Digit count
        features.append(sum(c.isdigit() for c in url))
        
        # 9. Special character count
        features.append(sum(not c.isalnum() for c in url))
        
        # 10. Domain length
        features.append(len(domain))
        
        # 11. Domain dot count
        features.append(domain.count('.'))
        
        # 12. IP address detection
        features.append(1 if IP_PATTERN.search(url) else 0)
        
        # 13. HTTPS check
        features.append(1 if url.startswith("https") else 0)
        
        # 14. Suspicious keywords count
        features.append(sum(word in url.lower() for word in SUSPICIOUS_KEYWORDS))
        
        # 15. URL shortener detection
        features.append(1 if any(s in url for s in URL_SHORTENERS) else 0)
        
        # 16. Suspicious TLD detection
        features.append(1 if any(t in url for t in SUSPICIOUS_TLDS) else 0)
        
        return features
    
    except Exception as e:
        raise ValueError(f"Error extracting features from URL: {str(e)}")


def get_risk_reasons(url):
    """
    Generate human-readable risk reasons for a given URL.
    
    Args:
        url (str): URL to analyze
        
    Returns:
        list: List of risk reason strings (max 3)
    """
    reasons = []
    url_lower = url.lower()
    
    # Check for suspicious keywords
    for word in ['login', 'verify', 'account', 'update', 'bank', 'signin']:
        if word in url_lower:
            reasons.append(f"Contains suspicious keyword: '{word}'")
            break  # Only add one keyword reason
    
    # Check for URL shorteners
    if any(s in url_lower for s in URL_SHORTENERS):
        reasons.append("Uses URL shortener")
    
    # Check for IP address
    if IP_PATTERN.search(url):
        reasons.append("Contains IP address")
    
    # Check for too many subdomains
    if url.count('.') > 3:
        reasons.append("Too many subdomains")
    
    # Check for URL length
    if len(url) > 75:
        reasons.append("URL is too long")
    
    # Check for @ symbol
    if '@' in url:
        reasons.append("Contains '@' symbol")
    
    # Check for - in domain
    if '-' in url:
        reasons.append("Contains '-' in domain")
    
    # Check for HTTP (not HTTPS)
    if url.startswith("http://"):
        reasons.append("Not using HTTPS")
    
    # Check for too many digits
    if sum(c.isdigit() for c in url) > 5:
        reasons.append("Too many numbers in URL")
    
    # Check for suspicious TLDs
    if any(t in url_lower for t in SUSPICIOUS_TLDS):
        reasons.append("Suspicious domain extension")
    
    # Return top 3 reasons
    return reasons[:3]
