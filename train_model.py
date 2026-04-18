import pandas as pd
import re
import pickle
from urllib.parse import urlparse

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

# ==============================
# 1. Load Dataset
# ==============================
df = pd.read_csv("Test.csv")

# Clean data
df = df.dropna()
df = df.drop_duplicates()

print("Dataset Loaded:", df.shape)

# ==============================
# 2. Feature Extraction
# ==============================
def extract_features(url):
    features = []
    from urllib.parse import urlparse
    import re

    domain = urlparse(url).netloc

    # Basic
    features.append(len(url))
    features.append(url.count('.'))
    features.append(url.count('/'))

    # Suspicious symbols
    features.append(url.count('@'))
    features.append(url.count('-'))
    features.append(url.count('='))
    features.append(url.count('?'))

    # Digits & special chars
    features.append(sum(c.isdigit() for c in url))
    features.append(sum(not c.isalnum() for c in url))

    # Domain features
    features.append(len(domain))
    features.append(domain.count('.'))

    # IP address
    features.append(1 if re.search(r'(\d{1,3}\.){3}\d{1,3}', url) else 0)

    # HTTPS
    features.append(1 if url.startswith("https") else 0)

    # Keywords (STRONG SIGNAL)
    keywords = ['login','secure','verify','account','update','bank','signin','confirm','password']
    features.append(sum(word in url.lower() for word in keywords))

    # Shorteners
    shorteners = ['bit.ly','tinyurl','goo.gl','t.co','rb.gy']
    features.append(1 if any(s in url for s in shorteners) else 0)

    # Suspicious TLDs (NEW 🔥)
    tlds = ['.tk','.ml','.ga','.cf','.gq']
    features.append(1 if any(t in url for t in tlds) else 0)

    return features

# Apply features
X = df['URL'].apply(extract_features).tolist()
y = df['Label']

print("Feature extraction completed!")

# ==============================
# 3. Train-Test Split
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ==============================
# 4. Random Forest Model
# ==============================
rf_model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)

rf_acc = accuracy_score(y_test, rf_pred)
print("\n🌲 Random Forest Accuracy:", rf_acc)

# ==============================
# 5. XGBoost Model
# ==============================
xgb_model = XGBClassifier(
    n_estimators=150,
    learning_rate=0.1,
    max_depth=6,
    eval_metric='logloss'
)

xgb_model.fit(X_train, y_train)
xgb_pred = xgb_model.predict(X_test)

xgb_acc = accuracy_score(y_test, xgb_pred)
print("\n⚡ XGBoost Accuracy:", xgb_acc)

# ==============================
# 6. Compare Models
# ==============================
if xgb_acc > rf_acc:
    print("\n🏆 Best Model: XGBoost")
else:
    print("\n🏆 Best Model: Random Forest")

# ==============================
# 7. Save Models
# ==============================
pickle.dump(rf_model, open("rf_model.pkl", "wb"))
pickle.dump(xgb_model, open("xgb_model.pkl", "wb"))

print("\n✅ Both models saved successfully!")