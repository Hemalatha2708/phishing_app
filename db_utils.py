"""
Database utilities module with connection pooling for performance.
Replaces simple get_db() with pooled connections for better throughput.
"""

import mysql.connector
from mysql.connector import pooling
import logging
from config import config

logger = logging.getLogger(__name__)

# Create connection pool
_db_pool = None


def init_db_pool():
    """
    Initialize database connection pool.
    Call this once at application startup.
    """
    global _db_pool
    
    try:
        _db_pool = pooling.MySQLConnectionPool(
            pool_name="phishing_pool",
            pool_size=5,  # Number of connections to maintain
            pool_reset_session=True,
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            autocommit=False
        )
        logger.info("Database connection pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {str(e)}")
        raise


def get_db():
    """
    Get a connection from the pool.
    
    Returns:
        mysql.connector.connection: Database connection from pool
        
    Raises:
        ConnectionError: If pool is not initialized or connection fails
    """
    global _db_pool
    
    if _db_pool is None:
        init_db_pool()
    
    try:
        connection = _db_pool.get_connection()
        return connection
    except mysql.connector.Error as e:
        if e.errno == 2003:
            raise ConnectionError("Cannot connect to database. Ensure MySQL server is running.")
        elif e.errno == 1045:
            raise PermissionError("Invalid database credentials")
        elif e.errno == 1049:
            raise ValueError(f"Database '{config.DB_NAME}' does not exist")
        else:
            logger.error(f"Database connection error: {str(e)}")
            raise


def close_pool():
    """
    Close all connections in the pool.
    Call this at application shutdown.
    """
    global _db_pool
    
    if _db_pool:
        try:
            # Close all connections in the pool
            while True:
                try:
                    conn = _db_pool.get_connection()
                    try:
                        conn.close()
                    except Exception as e:
                        # Log but don't crash on individual connection close errors
                        # (e.g., KeyboardInterrupt during shutdown)
                        logger.debug(f"Error closing individual connection: {str(e)}")
                except pooling.PoolError:
                    break
            logger.info("Database connection pool closed")
        except Exception as e:
            logger.error(f"Error closing connection pool: {str(e)}")
        finally:
            _db_pool = None
