# Quick Reference: Code Components & Issues

## 🔍 File-by-File Summary

### 1. **app.py** (Main Flask Application)
**Lines:** ~220 total | **Language:** Python

**What It Does:**
- Runs the web server
- Handles user navigation (routes/URLs)
- Manages login/registration
- Processes phishing detection requests
- Serves HTML templates to users

**Key Functions:**
```python
extract_features(url)          # Extracts 19 features from URL
def home()                     # Homepage
def login()                    # Login page
def register()                 # Registration page
def predict_page()             # URL input form
def result()                   # Process & predict phishing
```

**Critical Issues:**
| Line | Issue | Severity |
|------|-------|----------|
| 65 | `app.secret_key = "secret123"` | 🔴 CRITICAL |
| 18-60 | `extract_features()` function duplicated | 🟠 HIGH |
| All forms | No CSRF tokens | 🔴 CRITICAL |
| result() | No URL validation | 🔴 CRITICAL |
| 9-13 | Models loaded at startup | 🟡 MEDIUM |

**How to Fix:**
- [ ] Move secret key to environment variable in config.py
- [ ] Move extract_features() to features.py
- [ ] Add CSRF tokens to login.html, register.html, predict.html
- [ ] Add URL validation before feature extraction
- [ ] Lazy-load models on first prediction

---

### 2. **db.py** (Database Connection)
**Lines:** 8 total | **Language:** Python

**What It Does:**
- Creates connection to MySQL database
- Used by auth.py and app.py to store/retrieve data

**Code:**
```python
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="hemalatha2000",
        database="phishing"
    )
```

**Critical Issues:**
| Issue | Severity | Impact |
|-------|----------|--------|
| Hardcoded password | 🔴 CRITICAL | DB compromise |
| Hardcoded username | 🔴 CRITICAL | DB compromise |
| No pooling | 🟡 MEDIUM | Resource exhaustion |
| No error handling | 🟠 HIGH | Crashes on connection error |
| No timeouts | 🟠 HIGH | Connections hang |

**How to Fix:**
- [ ] Move credentials to environment variables
- [ ] Use config.py for host/database name
- [ ] Add try-except error handling
- [ ] Add connection timeout

**Example Fix:**
```python
import os
from config import DB_CONFIG

def get_db():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=DB_CONFIG['database'],
            connection_timeout=5
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
```

---

### 3. **auth.py** (User Authentication)
**Lines:** 39 total | **Language:** Python

**What It Does:**
- Handles user registration (creates new account)
- Handles user login (verifies credentials)
- Manages password hashing

**Key Functions:**
```python
def register_user(username, email, password)
    # Returns: "exists", "email_exists", or "success"
    # Does: Creates new user with hashed password

def login_user(username, password)
    # Returns: user dict or None
    # Does: Verifies password and returns user info
```

**Good Practices:**
✅ Uses `werkzeug.security` for password hashing
✅ Uses parameterized SQL queries (prevents SQL injection)
✅ Checks for duplicate users before inserting

**Issues:**
| Issue | Severity | Impact |
|-------|----------|--------|
| Inconsistent return codes | 🟠 HIGH | Confusing to app.py |
| Returns full user object | 🟠 HIGH | Exposes unnecessary data |
| No email validation | 🟠 HIGH | Invalid emails accepted |
| No rate limiting | 🟠 HIGH | Vulnerable to brute force |
| No logging | 🟡 MEDIUM | Can't track attacks |

**How to Fix:**
- [ ] Use consistent return codes: {"success": True/False, "reason": "..."}
- [ ] Return only {id, username} - hide email
- [ ] Add email format validation
- [ ] Add rate limiting for failed logins
- [ ] Log authentication attempts

---

### 4. **train_model.py** (ML Model Training)
**Lines:** 96 total | **Language:** Python

**What It Does:**
- Loads phishing URL dataset from Test.csv
- Extracts features from each URL
- Trains 2 machine learning models
- Tests accuracy on test set
- Saves trained models to disk

**Key Steps:**
```python
1. df = pd.read_csv("Test.csv")
2. X = df['URL'].apply(extract_features).tolist()
3. X_train, X_test, y_train, y_test = train_test_split()
4. rf_model = RandomForestClassifier(n_estimators=150)
5. xgb_model = XGBClassifier(n_estimators=150)
6. pickle.dump(rf_model, open("rf_model.pkl", "wb"))
7. xgb_model.save_model("xgb_model.json")
```

**Models:**
- **Random Forest:** 150 decision trees (good baseline)
- **XGBoost:** 150 boosted trees (usually better accuracy)

**Issues:**
| Issue | Severity | Impact |
|-------|----------|--------|
| Duplicates extract_features() | 🟠 HIGH | DRY violation |
| No cross-validation | 🟠 HIGH | Unreliable accuracy estimate |
| No hyperparameter tuning | 🟡 MEDIUM | Suboptimal models |
| Only accuracy metric | 🟡 MEDIUM | Missing precision/recall |
| No feature scaling | 🟡 MEDIUM | Potential accuracy loss |
| No data validation | 🟠 HIGH | Bad data = bad model |

**How to Fix:**
- [ ] Import extract_features from features.py (don't duplicate)
- [ ] Use cross-validation for reliability
- [ ] Add precision, recall, F1-score reporting
- [ ] Save feature scaling info if used
- [ ] Log training results

---

### 5. **create_db_schema.py** (Database Setup)
**Lines:** ~60+ total | **Language:** Python

**What It Does:**
- Creates MySQL database (if not exists)
- Creates 2 tables: profiles and history
- Defines column structures and constraints

**Tables Created:**
```sql
1. profiles
   - id (auto-increment)
   - username (unique)
   - email (unique)
   - password_hash
   - created_at

2. history
   - id (auto-increment)
   - user_id (foreign key → profiles.id)
   - url (text)
   - score (float)
   - status (varchar: Safe/Suspicious/Dangerous)
   - checked_at
```

**Issues:**
| Issue | Severity | Impact |
|-------|----------|--------|
| Hardcoded credentials | 🔴 CRITICAL | DB compromise |
| No error handling | 🟠 HIGH | Crashes silently |
| No indexes | 🟡 MEDIUM | Slow queries |
| Credentials in source | 🔴 CRITICAL | Version control leak |

**How to Fix:**
- [ ] Use environment variables for credentials
- [ ] Add try-except-finally blocks
- [ ] Add indexes on frequently queried columns
- [ ] Add unique constraint on (user_id, url, checked_at)

---

### 6. **test_features.py** (Unit Tests)
**Lines:** 12 total | **Language:** Python

**What It Does:**
- Tests the feature extraction function
- Verifies it works on sample URLs

**Current Code:**
```python
from features import extract_features  # ❌ PROBLEM: Module doesn't exist!

test_urls = [
    "https://google.com",
    "http://facebook.com",
    "http://verify-paypal-login.xyz",
    ...
]

for url in test_urls:
    features = extract_features(url)
    print("URL:", url)
    print("Features:", features)
```

**Issues:**
| Issue | Severity | Impact |
|-------|----------|--------|
| Imports non-existent module | 🔴 CRITICAL | File crashes immediately |
| No assertions | 🟠 HIGH | Tests don't verify anything |
| No error handling | 🟠 HIGH | Crashes on invalid URLs |
| No logging | 🟡 MEDIUM | Hard to debug |
| Hardcoded test data | 🟡 MEDIUM | Not maintainable |

**How to Fix:**
- [ ] Create features.py module with extract_features()
- [ ] Add assertions to verify output
- [ ] Test edge cases (very long URLs, special chars)
- [ ] Test invalid inputs (non-URLs, empty strings)
- [ ] Use proper unittest framework

**Example Fix:**
```python
from features import extract_features
import unittest

class TestFeatureExtraction(unittest.TestCase):
    def test_basic_url(self):
        features = extract_features("https://google.com")
        self.assertEqual(len(features), 19)
        self.assertIsInstance(features, list)
    
    def test_phishing_indicators(self):
        phish_url = "http://verify-paypal-login.tk"
        features = extract_features(phish_url)
        # Should have high keyword count (verify, login, paypal)
        # Should have suspicious TLD (.tk)
        self.assertGreater(features[13], 0)  # keywords
        self.assertEqual(features[15], 1)     # susp_TLD
    
    def test_empty_url(self):
        with self.assertRaises(Exception):
            extract_features("")

if __name__ == '__main__':
    unittest.main()
```

---

### 7. **Templates** (HTML Files)
**Language:** Jinja2 (Python templating language)

#### **home.html** (Homepage)
- Displays app description
- Shows login/register buttons
- Marketing/informational content

#### **login.html** (Login Form)
**Issues:**
- ❌ No CSRF token
- ❌ No input validation feedback
- ❌ No remember-me option

**Should Include:**
```html
<form method="POST">
    {{ csrf_token() }}  ← MISSING!
    <input type="text" name="username" required>
    <input type="password" name="password" required>
    <button type="submit">Login</button>
</form>
```

#### **register.html** (Registration Form)
**Issues:**
- ❌ No CSRF token
- ❌ No real-time password strength meter
- ❌ Display errors but no styling

#### **predict.html** (URL Input Form)
**Issues:**
- ❌ No CSRF token
- ❌ No input sanitization
- ❌ No URL format validation
- ❌ No helpful examples

#### **result.html** (Results Page)
**What It Shows:**
- Risk percentage (0-100%)
- Classification (Safe/Suspicious/Dangerous)
- Color coding (🟢 green/🟡 yellow/🔴 red)
- Link to history

#### **history.html** (Prediction History)
**Shows:** Previous predictions by user

---

### 8. **Static Files**

#### **style.css**
- Provides styling for all HTML pages
- Makes app look professional
- Responsive design (works on mobile)

#### **images/**
- Stores logos/icons
- Assets for UI

---

## 🚨 Critical Issues Checklist

### Security (Block Everything Else)
- [ ] `"secret123"` hardcoded in app.py → Use environment variable
- [ ] `"hemalatha2000"` hardcoded in db.py → Use environment variable
- [ ] Root username hardcoded in db.py → Use environment variable
- [ ] No CSRF tokens in any forms → Add Flask-WTF
- [ ] No URL validation before processing → Add validation.py
- [ ] test_features.py imports non-existent module → Create features.py

### Code Quality
- [ ] extract_features() duplicated 2x → Extract to single features.py
- [ ] No docstrings anywhere → Add for all functions
- [ ] No error handling → Wrap critical sections in try-except
- [ ] No logging → Add security event logging
- [ ] No input validation → Create validation.py module

### Performance
- [ ] ML models load at startup → Lazy-load on first use
- [ ] No database connection pooling → Use pooling library
- [ ] Regex recompiled each request → Compile once in features.py
- [ ] No caching → Add Redis or simple in-memory cache

---

## 📝 Variable Naming Reference

| Variable | Meaning | Type |
|----------|---------|------|
| `user_id` | Unique user identifier | Integer |
| `session['user_id']` | Currently logged-in user | Integer |
| `features` | 19 extracted URL features | List[Float] |
| `score` | Risk score 0-100% | Float |
| `result` | Classification | String (Safe/Susp./Dangerous) |
| `rf_score` | Random Forest prediction | Float (0-1) |
| `xgb_score` | XGBoost prediction | Float (0-1) |
| `db` | MySQL connection object | mysql.connector.MySQLConnection |
| `cursor` | Database query executor | mysql.connector.MySQLCursor |

---

## 📋 Implementation Priority

### MUST FIX FIRST (Blocks deployment):
1. Remove hardcoded credentials → Use config.py
2. Create features.py and fix imports
3. Add CSRF protection to all forms
4. Add URL input validation
5. Fix test_features.py imports

### SHOULD FIX SOON (High impact):
6. Add error handling throughout
7. Add logging for security events
8. Add docstrings to all functions
9. Create validation.py module
10. Create requirements.txt

### NICE TO HAVE (Performance):
11. Add database connection pooling
12. Lazy-load ML models
13. Compile regex patterns once
14. Add result caching
15. Add authentication rate limiting
