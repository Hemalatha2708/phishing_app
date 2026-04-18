"""
Database connection module.
Provides pooled database connections using configuration from config.py.
Backward compatible with existing code.
"""

from db_utils import get_db, init_db_pool, close_pool

__all__ = ['get_db', 'init_db_pool', 'close_pool']
