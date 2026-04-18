"""
Configuration module for phishing detection app.
Uses environment variables with sensible defaults for development.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'phishing')
    
    # Model settings
    MODEL_PATH_RF = os.getenv('MODEL_PATH_RF', 'rf_model.pkl')
    MODEL_PATH_XGB = os.getenv('MODEL_PATH_XGB', 'xgb_model.pkl')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'phishing_app.log')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # In production, SECRET_KEY MUST be set in environment
    if not os.getenv('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DB_NAME = 'phishing_test'


# Select config based on environment
ENV = os.getenv('FLASK_ENV', 'development')

if ENV == 'production':
    config = ProductionConfig()
elif ENV == 'testing':
    config = TestingConfig()
else:
    config = DevelopmentConfig()
