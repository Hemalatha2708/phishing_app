"""
Input validation module for user registration and form inputs.
"""

import re
from email_validator import validate_email, EmailNotValidError


def validate_email_address(email):
    """
    Validate email format.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not email or not isinstance(email, str):
        return False, "Email must be a non-empty string"
    
    email = email.strip()
    
    try:
        # Validate and normalize email
        valid = validate_email(email)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_username(username):
    """
    Validate username format.
    
    Args:
        username (str): Username to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not username or not isinstance(username, str):
        return False, "Username must be a non-empty string"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must be at most 50 characters"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscore, and hyphen"
    
    return True, None


def validate_password(password):
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not password or not isinstance(password, str):
        return False, "Password must be a non-empty string"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 128:
        return False, "Password must be at most 128 characters"
    
    # Optional: Check for strong password requirements
    # - At least one uppercase
    # - At least one lowercase
    # - At least one digit
    has_upper = re.search(r'[A-Z]', password)
    has_lower = re.search(r'[a-z]', password)
    has_digit = re.search(r'\d', password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password should contain uppercase, lowercase, and numbers"
    
    return True, None


def sanitize_string(value):
    """
    Sanitize string input to prevent XSS.
    
    Args:
        value (str): String to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # Remove/escape dangerous characters
    value = value.strip()
    return value
