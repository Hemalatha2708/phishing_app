"""
Authentication module for user registration and login.
"""

import logging
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from validation import validate_email_address, validate_username, validate_password

logger = logging.getLogger(__name__)


def register_user(username, email, password):
    """
    Register a new user with validation and error handling.
    
    Args:
        username (str): User's username
        email (str): User's email address
        password (str): User's password
        
    Returns:
        dict: {'status': 'success'|'exists'|'error', 'message': str}
    """
    # Validate inputs
    is_valid, error_msg = validate_username(username)
    if not is_valid:
        return {'status': 'error', 'message': error_msg}
    
    is_valid, error_msg = validate_email_address(email)
    if not is_valid:
        return {'status': 'error', 'message': error_msg}
    
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return {'status': 'error', 'message': error_msg}
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Check if user already exists
        cursor.execute("SELECT * FROM profiles WHERE username=%s OR email=%s", (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            db.close()
            return {'status': 'exists', 'message': 'Username or email already registered'}
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert new user
        cursor.execute(
            "INSERT INTO profiles (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        db.commit()
        
        cursor.close()
        db.close()
        
        logger.info(f"User registered successfully: {username}")
        return {'status': 'success', 'message': 'Registration successful'}
    
    except Exception as e:
        logger.error(f"Registration error for {username}: {str(e)}")
        return {'status': 'error', 'message': 'Registration failed. Please try again.'}


def login_user(username, password):
    """
    Authenticate user credentials.
    
    Args:
        username (str): User's username
        password (str): User's password
        
    Returns:
        dict: User record if authenticated, None otherwise
    """
    if not username or not password:
        return None
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM profiles WHERE username=%s", (username,))
        user = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        if user and check_password_hash(user['password_hash'], password):
            logger.info(f"User logged in: {username}")
            return user
        else:
            logger.warning(f"Failed login attempt for: {username}")
            return None
    
    except Exception as e:
        logger.error(f"Login error for {username}: {str(e)}")
        return None
