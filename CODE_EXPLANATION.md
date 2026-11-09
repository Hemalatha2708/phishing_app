# Phishing Detection Web Application - Complete Code Explanation

## 📋 Project Overview

This is a **Flask-based web application** that uses machine learning to detect phishing URLs. Users can register, log in, and input URLs to receive a risk assessment (Safe/Suspicious/Dangerous) based on two trained ML models: Random Forest and XGBoost.

---

## 🏗️ Architecture & Data Flow

```
User Browser
    ↓
Flask Web App (app.py)
    ├── Authentication (auth.py) → User Registration/Login
    ├── Database (db.py) → MySQL Connection
    ├── Feature Extraction (extract_features function)
    └── ML Models (rf_model.pkl, xgb_model.json)
         ├── Random Forest Classifier
         └── XGBoost Classifier
    ↓
Database (MySQL)
    ├── profiles table (user credentials)
    └── history table (prediction records)
```

---

## 📁 File-by-File Breakdown

### 1. **app.py** - Main Flask Application
**Purpose:** Core web server and routing logic

#### Key Components:

**Model Loading (Lines 9-13)**
```python
rf_model = pickle.load(open("rf_model.pkl", "rb"))
xgb_model = xgb.Booster()
xgb_model.load_model("xgb_model.json")
```
- Loads pre-trained Random Forest and XGBoost models at startup
- **⚠️ ISSUE:** Models loaded synchronously, blocks server startup

**Feature Extraction Function (Lines 18-60)**
- Extracts 19 features from each URL:
  - **Basic stats:** URL length, dot count, slash count
  - **Suspicious symbols:** @ signs, dashes, = signs (common in phishing)
  - **Domain analysis:** Domain length, subdomain count
  - **Security indicators:** IP address detection, HTTPS check
  - **Keyword detection:** "login", "verify", "account", "bank", etc.
  - **URL shorteners:** Detects bit.ly, tinyurl (suspicious)
  - **Suspicious TLDs:** .tk, .ml, .ga (free/anonymous domains)

- **⚠️ CRITICAL ISSUE:** This function is **duplicated** in both `app.py` and `train_model.py` (DRY violation)

**Routes (Endpoints):**

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Redirect to home |
| `/home` | GET | Landing page |
| `/login` | GET/POST | User authentication |
| `/register` | GET/POST | New user registration |
| `/predict` | GET | Prediction form page (requires login) |
| `/result` | POST | Process URL and return prediction |

**Login Flow (Lines 77-96)**
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = login_user(username, password)  # auth.py
        if user:
            session['user_id'] = user['id']  # Create session
            return redirect(url_for('predict_page'))
```
- Validates credentials via `auth.py`
- Sets session cookie with user ID
- **⚠️ NO CSRF PROTECTION** - forms vulnerable to cross-site attacks

**Registration Flow (Lines 100-148)**
- Validates username (6-15 alphanumeric chars)
- Validates email (whitelist: gmail, outlook, yahoo, hotmail)
- Validates password (min 8 chars)
- Checks for duplicate username/email
- **⚠️ ISSUE:** Hardcoded email domains (inflexible)

**Prediction Flow (Lines 167-220)**
```python
if url:
    features = extract_features(url)  # Extract 19 features
    rf_score = rf_model.predict_proba([features])[0][1]  # Random Forest
    xgb_score = xgb_model.predict(dmatrix)[0]  # XGBoost
    score = (rf_score + xgb_score) / 2 * 100  # Average scores
```
- Extracts features from user's URL
- Runs both models (ensemble approach)
- Averages predictions for final risk score
- Classifies: Safe (<50%), Suspicious (50-75%), Dangerous (>75%)
- Saves to database history table

**⚠️ SECURITY ISSUES:**
1. **Line 65:** `app.secret_key = "secret123"` - Hardcoded, weak secret key
2. **No input validation** - URLs not validated before feature extraction
3. **No error handling** - Model failures crash the app
4. **No CSRF tokens** - All forms vulnerable

---

### 2. **db.py** - Database Connection
**Purpose:** Provides MySQL connection pooling (currently just a simple connection)

```python
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="hemalatha2000",  # ⚠️ HARDCODED PASSWORD
        database="phishing"
    )
```

**⚠️ CRITICAL ISSUES:**
1. **Hardcoded credentials** exposed in source code
2. **No connection pooling** - Creates new connection for each request
3. **No error handling** - Connection failures crash app
4. **No timeout settings** - Connections can hang indefinitely

---

### 3. **auth.py** - User Authentication
**Purpose:** Handles user registration and login logic

#### `register_user(username, email, password)`
```python
def register_user(username, email, password):
    cursor.execute("SELECT * FROM profiles WHERE username=%s", (username,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        return "exists"
    
    hashed_password = generate_password_hash(password)  # Werkzeug (safe)
    cursor.execute(
        "INSERT INTO profiles (username, email, password_hash) VALUES (%s,%s,%s)",
        (username, email, hashed_password)
    )
```
✅ **Good:** Uses `werkzeug.security` to hash passwords
- Prevents rainbow table attacks
- Passwords never stored in plain text

**Issue:** Returns inconsistent status codes ("exists" vs "username_exists" in app.py)

#### `login_user(username, password)`
```python
def login_user(username, password):
    cursor.execute("SELECT * FROM profiles WHERE username=%s", (username,))
    user = cursor.fetchone()
    
    if user and check_password_hash(user['password_hash'], password):
        return user  # Returns user dict with id, username, email
```
✅ **Good:** Uses password hashing verification
⚠️ **Issue:** Returns full user object (exposes email to session)

---

### 4. **train_model.py** - ML Model Training
**Purpose:** Trains Random Forest and XGBoost models on phishing dataset

#### Workflow:
1. **Data Loading** - Loads Test.csv with phishing URLs and labels
2. **Data Cleaning**
   ```python
   df = df.dropna()  # Remove missing values
   df = df.drop_duplicates()  # Remove duplicates
   ```
3. **Feature Extraction** - ⚠️ **DUPLICATED CODE** from app.py
4. **Train-Test Split** - 80-20 split with stratification
5. **Random Forest Training**
   ```python
   rf_model = RandomForestClassifier(
       n_estimators=150,      # 150 decision trees
       random_state=42,       # Reproducible results
       n_jobs=-1              # Use all CPU cores
   )
   ```
6. **XGBoost Training**
   ```python
   xgb_model = XGBClassifier(
       n_estimators=150,
       learning_rate=0.1,
       max_depth=6,
       eval_metric='logloss'
   )
   ```
7. **Model Comparison** - Selects best-performing model
8. **Model Persistence**
   ```python
   pickle.dump(rf_model, open("rf_model.pkl", "wb"))
   xgb_model.save_model("xgb_model.json")
   ```

**⚠️ ISSUES:**
1. **Duplicated feature extraction** - Same logic in app.py
2. **No cross-validation** - Only single train-test split
3. **No hyperparameter tuning** - Hardcoded parameters
4. **No model evaluation metrics** - Only accuracy reported

---

### 5. **create_db_schema.py** - Database Schema
**Purpose:** Creates MySQL database and tables

**Database Structure:**
```sql
CREATE TABLE profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    url TEXT NOT NULL,
    score FLOAT NOT NULL,
    status VARCHAR(50) NOT NULL,  -- Safe, Suspicious, Dangerous
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES profiles(id)
);
```

**⚠️ ISSUE:** Contains same hardcoded credentials as db.py

---

### 6. **test_features.py** - Feature Testing
**Purpose:** Unit tests for feature extraction

```python
from features import extract_features  # ⚠️ IMPORTS NON-EXISTENT MODULE
```

**⚠️ CRITICAL ISSUE:** Tries to import from `features` module that doesn't exist yet
- This file will crash on execution
- Feature extraction function is in app.py and train_model.py
- Should be in separate `features.py` module

---

### 7. **Static Files**

#### **style.css** - Styling
- Provides CSS for responsive design
- Formats forms, buttons, results display

#### **images/** - Asset Directory
- Stores application images/logos

---

### 8. **Templates** - HTML Pages (Flask Jinja2 Templates)

| File | Purpose |
|------|---------|
| `home.html` | Landing page with app description |
| `login.html` | Login form (username/password) |
| `register.html` | Registration form with validation feedback |
| `predict.html` | URL input form for phishing detection |
| `result.html` | Displays prediction results (Safe/Suspicious/Dangerous) |
| `history.html` | User's prediction history |

**⚠️ ISSUE:** All templates missing CSRF tokens - vulnerable to cross-site attacks

---

## 🔍 How Phishing Detection Works

### Feature Engineering (19 features extracted per URL):

| Category | Features | Why It Matters |
|----------|----------|----------------|
| **URL Structure** | length, dots, slashes, @, dashes, =, ? | Phishing URLs often have suspicious structure |
| **Character Analysis** | digit count, special char count | Obfuscation indicator |
| **Domain** | domain length, subdomain count | Phishing uses complex subdomains |
| **Security** | IP address detection, HTTPS | Legitimate sites rarely use IP addresses |
| **Keywords** | "login", "verify", "account", "bank" | Phishing often targets account/bank access |
| **URL Shorteners** | bit.ly, tinyurl detection | Shorteners hide true destination |
| **Suspicious TLDs** | .tk, .ml, .ga, .cf | Free domains associated with phishing |

### Classification Logic:
```
Risk Score = (RandomForest_score + XGBoost_score) / 2 * 100

If score < 50%    → SAFE (likely legitimate)
If 50% ≤ score < 75% → SUSPICIOUS (review carefully)
If score ≥ 75%    → DANGEROUS (likely phishing)
```

---

## 🚨 Critical Security Issues Summary

| Severity | Issue | Location | Impact |
|----------|-------|----------|--------|
| 🔴 CRITICAL | Hardcoded DB password | db.py, create_db_schema.py | Database compromise |
| 🔴 CRITICAL | Hardcoded secret key | app.py (line 65) | Session hijacking |
| 🔴 CRITICAL | Missing CSRF protection | All forms | XSS/CSRF attacks |
| 🔴 CRITICAL | No input validation | app.py (URL processing) | Invalid/malicious inputs crash system |
| 🔴 CRITICAL | Non-existent module import | test_features.py | Tests fail |
| 🟠 HIGH | Duplicated extract_features() | app.py + train_model.py | DRY violation, maintenance nightmare |
| 🟠 HIGH | No error handling | Throughout | App crashes on errors |
| 🟠 HIGH | No logging | Throughout | Can't track security events |
| 🟡 MEDIUM | Synchronous model loading | app.py startup | Blocks server initialization |
| 🟡 MEDIUM | Regex recompiled each request | extract_features | Performance degradation |
| 🟡 MEDIUM | No database pooling | db.py | Resource exhaustion |

---

## 📊 Dependencies

**From requrminets.txt** (note: typo in filename):
- Flask - Web framework
- mysql-connector-python - MySQL driver
- scikit-learn - ML library (Random Forest)
- xgboost - ML library
- pandas - Data manipulation
- werkzeug - Security utilities (password hashing)
- numpy - Numerical computing

---

## ✅ Verification Checklist

- [ ] No hardcoded credentials remain
- [ ] All functions have docstrings
- [ ] Feature extraction logic exists only in features.py
- [ ] Prediction workflow works end-to-end
- [ ] test_features.py runs without import errors
- [ ] All inputs validated before processing
- [ ] CSRF tokens in all forms
- [ ] Error handling throughout
- [ ] Logging for security events

---

## 🔧 Next Steps (From Implementation Roadmap)

**Phase 1: Security Hardening** (BLOCKS rest)
1. Create config.py with environment variables
2. Extract extract_features() to features.py
3. Add URL input validation
4. Add Flask-WTF CSRF protection
5. Replace hardcoded values with config

**Phase 2: Code Quality**
1. Add error handling
2. Set up logging
3. Add docstrings
4. Create requirements.txt
5. Create validation module

**Phase 3: Performance**
1. Compile regex patterns once
2. Add database connection pooling
3. Lazy-load ML models
4. Add caching

**Phase 4: Testing**
1. Fix test_features.py
2. Create integration tests
3. Security testing
