from features import extract_features

# Test URLs
test_urls = [
    "https://google.com",
    "http://facebook.com",
    "http://verify-paypal-login.xyz",
    "http://192.168.1.1/login",
    "https://secure-bank-account-update.com"
]

for url in test_urls:
    features = extract_features(url)
    print("\nURL:", url)
    print("Features:", features)