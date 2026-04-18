# Phishing Detection Web Application

A machine learning-powered web application for detecting phishing URLs using Random Forest and XGBoost models.

## 🔒 Security Features

- **Secure Authentication**: Password hashing with werkzeug
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **Configuration Management**: Environment-based configuration (no hardcoded secrets)
- **Input Validation**: Email, username, password, and URL validation
- **Error Handling**: Comprehensive error handling with logging
- **Connection Pooling**: Database connection pooling for better resource management

## 🚀 Performance Features

- **Lazy Model Loading**: ML models loaded on first use, not at startup
- **Database Connection Pooling**: Reusable connection pool instead of creating new connections
- **Prediction Caching**: Optional in-memory caching for identical URLs
- **Optimized Feature Extraction**: Pre-compiled regex patterns
- **Structured Logging**: Detailed logging for debugging and monitoring

## 📋 Prerequisites

- Python 3.8+
- MySQL Server 5.7+
- pip (Python package manager)

## 🔧 Installation

### 1. Clone and setup environment

```bash
git clone <repository-url>
cd phishing_app
```

### 2. Create Python virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure database

```bash
# Create database and tables
mysql -u root -p < schema.sql
```

### 5. Setup environment variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your configuration
```

**.env file template:**
```env
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-database-password
DB_NAME=phishing
```

### 6. Train the models

```bash
python train_model.py
```

This will create `rf_model.pkl` and `xgb_model.pkl` in the project directory.

### 7. Run the application

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

## 📊 Model Training

The application uses two ML models for ensemble prediction:

- **Random Forest**: 150 estimators, fast and reliable
- **XGBoost**: 150 estimators, max depth 6, excellent accuracy

Both models are trained on the dataset in `Test.csv` using an 80/20 train-test split with stratification.

**Feature Engineering:**
- URL length, dot count, slash count
- Suspicious symbols (@, -, =, ?)
- Digit and special character counts
- Domain analysis (length, dots)
- IP address detection
- HTTPS check
- Suspicious keyword matching (9 keywords)
- URL shortener detection
- Suspicious TLD detection

Total: **16 engineered features** per URL

## 🏗️ Project Structure

```
phishing_app/
├── app.py                 # Main Flask application
├── auth.py               # User registration and login
├── db.py                 # Database connection (backward compatible)
├── db_utils.py           # Database connection pooling
├── features.py           # Feature extraction and URL validation
├── validation.py         # Input validation functions
├── cache.py              # Prediction caching utility
├── config.py             # Configuration management
├── train_model.py        # Model training script
├── test_features.py      # Unit tests for feature extraction
├── requirements.txt      # Python dependencies
├── schema.sql            # Database schema
├── .env.example          # Environment configuration template
├── static/
│   ├── style.css         # Application styling
│   └── images/           # Static images
└── templates/
    ├── home.html         # Home page
    ├── login.html        # Login form
    ├── register.html     # Registration form
    ├── predict.html      # URL prediction form
    ├── result.html       # Prediction results
    ├── history.html      # Prediction history
    ├── 404.html          # 404 error page
    └── 500.html          # 500 error page
```

## 🔐 Security Considerations

### Production Deployment

⚠️ **Important**: These settings are for development only. For production:

1. **Change SECRET_KEY**: Set a strong, unique secret key
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Set FLASK_ENV=production**: Disables debug mode

3. **Use HTTPS**: Deploy behind a reverse proxy with SSL/TLS

4. **Database Security**:
   - Use strong passwords
   - Restrict database access
   - Enable database backups
   - Consider managed database services

5. **CSRF Tokens**: Already implemented, tokens automatically included in all forms

6. **Input Validation**: All user inputs validated before processing

## 📊 Database Schema

### profiles table
- `id`: Primary key
- `username`: Unique username (VARCHAR 50)
- `email`: Unique email (VARCHAR 100)
- `password_hash`: Hashed password (VARCHAR 255)
- `created_at`: Registration timestamp

### history table
- `id`: Primary key
- `user_id`: Foreign key to profiles
- `url`: Analyzed URL (TEXT)
- `score`: Risk score 0-100 (DECIMAL 5,2)
- `status`: Safe/Suspicious/Dangerous (ENUM)
- `created_at`: Prediction timestamp

## 🧪 Testing

Run the test suite:

```bash
python -m pytest test_features.py -v
```

Or run tests with unittest:

```bash
python test_features.py
```

## 📋 API Usage

### Prediction Scoring

- **Score 0-50**: Safe ✅
- **Score 50-75**: Suspicious ⚠️
- **Score 75-100**: Dangerous ❌

## 🛠️ Troubleshooting

### "Cannot connect to database"

- Ensure MySQL server is running: `net start MySQL80` (Windows) or `brew services start mysql` (macOS)
- Check database credentials in `.env`
- Verify database exists: `mysql -u root -p -e "SHOW DATABASES;"`

### "ML models not available"

- Ensure models are trained: `python train_model.py`
- Check that `.pkl` files exist in project directory
- Check MODEL_PATH_RF and MODEL_PATH_XGB in `.env`

### "CSRF token missing"

- Ensure all forms include `{{ csrf_token() }}`
- Clear browser cookies and refresh page
- Check Flask-WTF is installed: `pip list | grep Flask-WTF`

## 📝 Logging

Logs are written to `phishing_app.log` by default. Configure logging level in `.env`:

```env
LOG_LEVEL=DEBUG    # For development
LOG_LEVEL=INFO     # For production
```

## 🚀 Performance Optimization

The application includes several optimizations:

1. **Connection Pooling**: 5 persistent database connections
2. **Lazy Model Loading**: Models loaded only when first needed
3. **Prediction Caching**: Caches predictions for 5 minutes
4. **Regex Pre-compilation**: URL features use pre-compiled patterns
5. **Request Compression**: Automatic gzip compression

## 📚 Code Review Fixes (review_fix branch)

This branch includes comprehensive improvements:

### Security Hardening
- ✅ Removed hardcoded database credentials
- ✅ Removed hardcoded Flask secret key
- ✅ Added CSRF protection to all forms
- ✅ Added input validation
- ✅ Added error handling and logging

### Code Quality
- ✅ Eliminated DRY violation (centralized feature extraction)
- ✅ Added comprehensive docstrings
- ✅ Added type hints and error handling
- ✅ Improved error messages
- ✅ Added structured logging

### Performance
- ✅ Connection pooling
- ✅ Lazy model loading
- ✅ Optimized regex patterns
- ✅ Optional prediction caching
- ✅ Database connection cleanup

## 📞 Support

For issues and questions:
1. Check the Troubleshooting section
2. Review application logs in `phishing_app.log`
3. Ensure all dependencies are installed: `pip install -r requirements.txt`

## 📄 License

This project is provided as-is for educational and research purposes.

## 🙏 Acknowledgments

- Developed using Flask, scikit-learn, and XGBoost
- URL features based on common phishing indicators
- Database design optimized for user history tracking
