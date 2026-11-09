# Phishing Detection App - Architecture & Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    WEB BROWSER (User)                            │
│  - Register Form                                                 │
│  - Login Form                                                    │
│  - URL Prediction Form                                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP Requests
                           ↓
        ┌──────────────────────────────────────────┐
        │      FLASK WEB APPLICATION (app.py)      │
        ├──────────────────────────────────────────┤
        │ Routes:                                   │
        │  • /home - Homepage                       │
        │  • /login - User authentication           │
        │  • /register - Account creation           │
        │  • /predict - Phishing check form         │
        │  • /result - Process & display results    │
        └──────────────┬───────────────────────────┘
                       │
         ┌─────────────┼─────────────┬────────────────┐
         ↓             ↓             ↓                ↓
    ┌────────┐   ┌────────┐   ┌──────────┐   ┌─────────────┐
    │ auth.py│   │ db.py  │   │Features  │   │ML Models    │
    │        │   │        │   │Extraction│   │             │
    │Register│   │MySQL   │   │(19 feat.)│   │Random Forest│
    │Login   │   │Connect │   │URL       │   │XGBoost      │
    └────────┘   └───┬────┘   │Analysis  │   │             │
                     │        └──────────┘   └─────────────┘
                     │
        ┌────────────┴─────────────┐
        ↓                          ↓
    ┌─────────────┐        ┌─────────────┐
    │ profiles    │        │  history    │
    │ table       │        │  table      │
    ├─────────────┤        ├─────────────┤
    │• id         │        │• id         │
    │• username   │        │• user_id    │
    │• email      │        │• url        │
    │• pwd_hash   │        │• score      │
    │• created_at │        │• status     │
    └─────────────┘        │• checked_at │
                           └─────────────┘
                     (MySQL Database)
```

## Request Flow: User Predicts Phishing URL

```
1. User enters URL
        ↓
2. POST /result with URL
        ↓
3. Check session (is user logged in?)
        ↓ Yes → Continue
        ↓ No → Redirect to /login
        ↓
4. Extract 19 Features from URL
        ├─ URL length, dots, slashes
        ├─ Suspicious symbols (@, -, =)
        ├─ Domain analysis
        ├─ IP/HTTPS detection
        ├─ Keyword detection (login, verify, bank)
        ├─ URL shortener detection
        └─ Suspicious TLD detection
        ↓
5. Get Predictions
        ├─ Random Forest Model → Score (0-1)
        ├─ XGBoost Model → Score (0-1)
        └─ Average Scores
        ↓
6. Calculate Risk Score
        score = (rf_score + xgb_score) / 2 * 100
        ↓
7. Classify Result
        ├─ < 50% → SAFE
        ├─ 50-75% → SUSPICIOUS
        └─ > 75% → DANGEROUS
        ↓
8. Store in Database
        INSERT INTO history (user_id, url, score, status)
        ↓
9. Display Result to User
        ├─ Risk percentage
        ├─ Classification (Safe/Suspicious/Dangerous)
        ├─ Recommendations
        └─ History link
```

## Registration/Login Flow

```
REGISTRATION:
1. User fills register.html form
2. POST /register with (username, email, password)
3. Validate:
   ├─ Username: 6-15 alphanumeric chars
   ├─ Email: Whitelist (gmail, outlook, yahoo)
   └─ Password: Min 8 chars
4. Check duplicates (username, email)
5. Hash password with werkzeug
6. INSERT into profiles table
7. Show success message

LOGIN:
1. User fills login.html form
2. POST /login with (username, password)
3. Query profiles table for username
4. Check password hash
5. If valid:
   ├─ Create session['user_id']
   └─ Redirect to /predict
6. If invalid:
   ├─ Set error message
   └─ Redirect back to /login
```

## 19 Feature Extraction Details

```
URL Feature Analysis:
┌────────────────────────────────────────────────────┐
│ INPUT: "http://verify-paypal-secure.xyz:8080/..."  │
├────────────────────────────────────────────────────┤
│ BASIC METRICS                                       │
│  1. URL length                                      │
│  2. Dot count (.)                                   │
│  3. Slash count (/)                                 │
│                                                     │
│ SUSPICIOUS SYMBOLS                                  │
│  4. @ count (email obfuscation)                     │
│  5. - count (domain confusion)                      │
│  6. = count (parameter obfuscation)                 │
│  7. ? count (query params)                          │
│                                                     │
│ CHARACTER ANALYSIS                                  │
│  8. Digit count                                     │
│  9. Special char count                              │
│                                                     │
│ DOMAIN FEATURES                                     │
│  10. Domain length                                  │
│  11. Subdomain count (.)                            │
│                                                     │
│ SECURITY INDICATORS                                 │
│  12. IP address detected (1/0)                      │
│  13. HTTPS protocol (1/0)                           │
│                                                     │
│ KEYWORD MATCHING (STRONG SIGNAL)                    │
│  14. Count of keywords:                             │
│      [login, secure, verify, account, update,       │
│       bank, signin, confirm, password]              │
│                                                     │
│ SHORTENER DETECTION                                 │
│  15. Contains shortener? (bit.ly, tinyurl, etc) 1/0 │
│                                                     │
│ SUSPICIOUS TLD                                      │
│  16. Suspicious TLD? (.tk, .ml, .ga, .cf) 1/0       │
│                                                     │
│ RESERVED FOR FUTURE                                 │
│  17-19. Placeholder for additional features         │
└────────────────────────────────────────────────────┘

EXAMPLE OUTPUT:
URL: https://verify-paypal-account-update.tk
Features: [41, 4, 2, 0, 2, 0, 0, 0, 8, 20, 4, 0, 1, 4, 0, 1]
          ↑   ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑  ↑  ↑ ↑ ↑ ↑ ↑ ↑
   len   . / @ - = ? digits special len_dom subdomain
   IP  HTTPS  keywords  shortener  susp_TLD
```

## Model Ensemble Approach

```
Input URL
    ↓
Extract Features (19)
    ↓
    ├─────────────────────────────────────┐
    ↓                                     ↓
Random Forest Model              XGBoost Model
(150 Decision Trees)             (150 Trees + Boosting)
    ↓                                     ↓
Score: 0.73                         Score: 0.78
(73% phishing probability)          (78% phishing probability)
    ↓                                     ↓
    └─────────────────────────────────────┘
              ↓
    Average Predictions
    (73 + 78) / 2 = 75.5%
              ↓
    Classification Logic:
    ├─ 0-50%     → SAFE ✅
    ├─ 50-75%    → SUSPICIOUS ⚠️
    └─ 75-100%   → DANGEROUS 🚫
              ↓
    Result: DANGEROUS (75.5%)
              ↓
    Store in Database & Display
```

## Database Schema Relationships

```
┌──────────────────────────┐
│       profiles           │
├──────────────────────────┤
│ id (PK) ◄──┐             │
│ username   │ UNIQUE      │
│ email      │ UNIQUE      │
│ password_hash            │
│ created_at               │
└──────────────────────────┘
              │
              │ 1-to-Many
              │
┌─────────────▼──────────────────┐
│       history                   │
├─────────────────────────────────┤
│ id (PK)                         │
│ user_id (FK) ──→ profiles.id    │
│ url                             │
│ score (0.0-100.0)               │
│ status (Safe/Susp./Dangerous)   │
│ checked_at                      │
└─────────────────────────────────┘

One user can have many predictions in history.
```

## Code Organization Issues

```
CURRENT STATE (PROBLEMATIC):
├── app.py
│   └── extract_features() ← DUPLICATED
├── train_model.py
│   └── extract_features() ← DUPLICATED
└── test_features.py
    └── imports from "features" ← NON-EXISTENT!

DESIRED STATE (AFTER REFACTORING):
├── config.py ← Environment configuration
├── features.py ← SINGLE SOURCE OF TRUTH
│   └── extract_features()
├── validation.py ← Input validation
├── app.py ← Web app (clean imports)
├── auth.py ← Auth functions
├── db.py ← Database functions
├── train_model.py ← Model training (imports from features.py)
└── test_features.py ← Tests (imports from features.py)
```
