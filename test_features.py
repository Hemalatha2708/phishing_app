"""
Unit tests for feature extraction module.
Tests URL feature extraction and validation functions.
"""

import unittest
from features import extract_features, validate_url, get_risk_reasons


class TestFeatureExtraction(unittest.TestCase):
    """Test cases for feature extraction functions"""
    
    def test_valid_url_extraction(self):
        """Test feature extraction on valid URLs"""
        url = "https://www.google.com"
        features = extract_features(url)
        
        # Should return 16 features
        self.assertEqual(len(features), 16)
        # All features should be integers
        self.assertTrue(all(isinstance(f, int) for f in features))
    
    def test_suspicious_url_extraction(self):
        """Test feature extraction on suspicious URL"""
        url = "https://verify-account-login.bit.ly"
        features = extract_features(url)
        
        self.assertEqual(len(features), 16)
        # Should detect keywords (14th feature)
        self.assertGreater(features[13], 0)
        # Should detect URL shortener (15th feature)
        self.assertEqual(features[14], 1)
    
    def test_ip_address_detection(self):
        """Test IP address detection in URL"""
        url = "http://192.168.1.1/login"
        features = extract_features(url)
        
        # 12th feature should be 1 for IP address
        self.assertEqual(features[11], 1)
    
    def test_https_check(self):
        """Test HTTPS detection"""
        https_url = "https://example.com"
        http_url = "http://example.com"
        
        https_features = extract_features(https_url)
        http_features = extract_features(http_url)
        
        # 13th feature: HTTPS check
        self.assertEqual(https_features[12], 1)
        self.assertEqual(http_features[12], 0)
    
    def test_invalid_url_validation(self):
        """Test validation of invalid URLs"""
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://example.com",
            "h" * 3000,  # Too long
        ]
        
        for url in invalid_urls:
            is_valid, error = validate_url(url)
            self.assertFalse(is_valid)
            self.assertIsNotNone(error)
    
    def test_valid_url_validation(self):
        """Test validation of valid URLs"""
        valid_urls = [
            "https://www.google.com",
            "http://example.com/path",
            "https://subdomain.example.co.uk/page",
        ]
        
        for url in valid_urls:
            is_valid, error = validate_url(url)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
    
    def test_risk_reasons_generation(self):
        """Test risk reason generation"""
        url = "http://login-verify-account.bit.ly"
        reasons = get_risk_reasons(url)
        
        # Should return up to 3 reasons
        self.assertLessEqual(len(reasons), 3)
        # Should be a list of strings
        self.assertTrue(all(isinstance(r, str) for r in reasons))
        # Should contain some risk indicators
        self.assertGreater(len(reasons), 0)
    
    def test_safe_url_reasons(self):
        """Test reason generation for safe URLs"""
        url = "https://www.google.com"
        reasons = get_risk_reasons(url)
        
        # Safe URLs should have at most 1 reason or be empty
        self.assertLessEqual(len(reasons), 1)


if __name__ == '__main__':
    unittest.main()
