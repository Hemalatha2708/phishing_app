
"""
Phishing Detection Web Application
Main Flask application for URL classification using ML models
"""

import logging
import pickle
import os
from flask import Flask, render_template, request, redirect, session, url_for
from flask_wtf.csrf import CSRFProtect

from auth import register_user, login_user
from db import get_db, init_db_pool, close_pool
from features import extract_features, get_risk_reasons
from config import config
from validation import sanitize_string

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
csrf = CSRFProtect(app)

# Global model variables (lazy-loaded on first use)
_rf_model = None
_xgb_model = None


def load_models():
    """
    Load ML models lazily on first use instead of at startup.
    This improves app startup time significantly.
    
    Returns:
        tuple: (rf_model, xgb_model) or (None, None) if loading fails
    """
    global _rf_model, _xgb_model
    
    if _rf_model is not None and _xgb_model is not None:
        return _rf_model, _xgb_model
    
    try:
        if not os.path.exists(config.MODEL_PATH_RF):
            logger.error(f"Random Forest model not found at {config.MODEL_PATH_RF}")
            return None, None
        
        if not os.path.exists(config.MODEL_PATH_XGB):
            logger.error(f"XGBoost model not found at {config.MODEL_PATH_XGB}")
            return None, None
        
        _rf_model = pickle.load(open(config.MODEL_PATH_RF, "rb"))
        _xgb_model = pickle.load(open(config.MODEL_PATH_XGB, "rb"))
        logger.info("ML models loaded successfully on first use")
        return _rf_model, _xgb_model
    
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {str(e)}")
        return None, None
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        return None, None


# =========================
# ROUTES
# =========================

@app.route('/')
def index():
    """Redirect to home page"""
    return redirect(url_for('home'))


@app.route('/home')
def home():
    """Display home page"""
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    GET: Display login form
    POST: Authenticate user
    """
    if request.method == 'POST':
        try:
            username = sanitize_string(request.form.get('username', ''))
            password = request.form.get('password', '')
            
            if not username or not password:
                return render_template('login.html', error="Username and password required")
            
            user = login_user(username, password)
            
            if user:
                session['user_id'] = user['id']
                logger.info(f"User logged in: {username}")
                return redirect(url_for('predict_page'))
            else:
                logger.warning(f"Failed login attempt: {username}")
                return render_template('login.html', error="Invalid username or password")
        
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return render_template('login.html', error="Login failed. Please try again.")
    
    error = session.pop('error', None)
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    GET: Display registration form
    POST: Create new user account
    """
    if request.method == 'POST':
        try:
            username = sanitize_string(request.form.get('username', ''))
            email = sanitize_string(request.form.get('email', ''))
            password = request.form.get('password', '')
            
            result = register_user(username, email, password)
            
            if result['status'] == 'success':
                return render_template('register.html', success=True)
            elif result['status'] == 'exists':
                return render_template('register.html', error="Username or email already registered")
            else:
                return render_template('register.html', error=result['message'])
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return render_template('register.html', error="Registration failed. Please try again.")
    
    return render_template('register.html')




# ✅ PREDICT PAGE
@app.route('/predict')
def predict_page():
    """Display URL prediction form"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('predict.html')


@app.route('/result', methods=['POST'])
def result():
    """
    Process URL prediction and display results.
    Extracts features, runs both ML models, and logs to database.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        url = sanitize_string(request.form.get('url', '').strip())
        
        if not url:
            return render_template('result.html', error="Please enter a URL")
        
        # Load models lazily
        rf_model, xgb_model = load_models()
        
        if not rf_model or not xgb_model:
            logger.error("ML models not loaded")
            return render_template('result.html', error="ML models not available. Please contact support.")
        
        # Extract features
        try:
            features = extract_features(url)
        except ValueError as e:
            logger.warning(f"Feature extraction failed for URL: {url}, Error: {str(e)}")
            return render_template('result.html', error=str(e))
        
        # Get predictions from both models
        try:
            rf_score = rf_model.predict_proba([features])[0][1]
            xgb_score = xgb_model.predict_proba([features])[0][1]
        except Exception as e:
            logger.error(f"Model prediction failed: {str(e)}")
            return render_template('result.html', error="Prediction failed. Please try again.")
        
        # Calculate final score
        final_score = (rf_score + xgb_score) / 2 * 100
        final_score = round(final_score, 2)
        
        # Classify result
        if final_score < 50:
            classification = "Safe"
        elif final_score < 75:
            classification = "Suspicious"
        else:
            classification = "Dangerous"
        
        # Get risk reasons
        reasons = get_risk_reasons(url)
        if classification == "Safe":
            reasons = ["No major risks detected"]
        elif not reasons:
            reasons = ["Potential risks detected"]
        
        # Log to database
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute(
                "INSERT INTO history (user_id, url, score, status) VALUES (%s, %s, %s, %s)",
                (session['user_id'], url, final_score, classification)
            )
            
            db.commit()
            cursor.close()
            db.close()
            
            logger.info(f"Prediction logged for user {session['user_id']}: URL={url}, Score={final_score}, Status={classification}")
        
        except Exception as e:
            logger.error(f"Database error while logging prediction: {str(e)}")
            # Continue anyway - don't fail the prediction if logging fails
        
        return render_template(
            'result.html',
            url=url,
            result=classification,
            score=final_score,
            reasons=reasons
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return render_template('result.html', error="An unexpected error occurred. Please try again.")


@app.route('/history')
def history():
    """Display user's prediction history"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "SELECT url, score, status, created_at FROM history WHERE user_id=%s ORDER BY created_at DESC",
            (session['user_id'],)
        )
        
        history_data = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return render_template('history.html', history=history_data)
    
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        return render_template('history.html', error="Failed to retrieve history", history=[])


@app.route('/logout')
def logout():
    """Log out user and clear session"""
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
    return redirect(url_for('home'))


# =========================
# ERROR HANDLERS
# =========================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500


# =========================
# APP LIFECYCLE HANDLERS
# =========================

@app.before_request
def before_request():
    """Initialize database pool before first request"""
    try:
        init_db_pool()
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {str(e)}")


@app.teardown_appcontext
def teardown_app(exception):
    """Close database pool on app shutdown"""
    if exception:
        logger.error(f"App context teardown due to exception: {str(exception)}")
    close_pool()


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    try:
        # Initialize database pool
        init_db_pool()
        app.run(debug=config.DEBUG, host='127.0.0.1', port=5000)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    finally:
        # Cleanup
        close_pool()