"""
Database connection module.
Uses configuration from config.py instead of hardcoded credentials.
"""

import mysql.connector
from config import config


def get_db():
    """
    Create and return a database connection.
    
    Returns:
        mysql.connector.connection: Database connection
        
    Raises:
        mysql.connector.Error: If connection fails
    """
    try:
        connection = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        return connection
    except mysql.connector.Error as e:
        if e.errno == 2003:
            raise ConnectionError("Cannot connect to database. Ensure MySQL server is running.")
        elif e.errno == 1045:
            raise PermissionError("Invalid database credentials")
        elif e.errno == 1049:
            raise ValueError(f"Database '{config.DB_NAME}' does not exist")
        else:
            raise