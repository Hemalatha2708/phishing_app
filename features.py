import re
from urllib.parse import urlparse

def extract_features(url):
    features = []

    # Length
    features.append(len(url))

    # Subdomains
    features.append(url.count('.'))

    # Special characters
    features.append(len(re.findall(r'[@\-_=]', url)))

    # HTTPS
    features.append(1 if url.startswith("https") else 0)

    # IP address
    features.append(1 if re.search(r'\d+\.\d+\.\d+\.\d+', url) else 0)

    # Keywords
    keywords = ['login','verify','bank','secure','account']
    features.append(sum([1 for k in keywords if k in url.lower()]))

    return features