"""
FLYTAU Database Module
MySQL connection management using mysql-connector-python
"""
import mysql.connector
from mysql.connector import pooling
from flask import current_app, g


# Global connection pool (initialized once)
_connection_pool = None


def init_app(app):
    """
    Initialize the database connection pool with the Flask app.
    
    Args:
        app: Flask application instance
    """
    global _connection_pool
    
    pool_config = {
        'pool_name': app.config['DB_POOL_NAME'],
        'pool_size': app.config['DB_POOL_SIZE'],
        'host': app.config['DB_HOST'],
        'port': app.config['DB_PORT'],
        'user': app.config['DB_USER'],
        'password': app.config['DB_PASSWORD'],
        'database': app.config['DB_NAME'],
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'autocommit': False
    }
    
    try:
        _connection_pool = pooling.MySQLConnectionPool(**pool_config)
    except mysql.connector.Error as err:
        app.logger.error(f"Failed to create connection pool: {err}")
        raise
    
    # Register teardown function to close connections
    app.teardown_appcontext(close_db)


def get_db():
    """
    Get a database connection from the pool.
    Stores connection in Flask's g object for request-scoped reuse.
    
    Returns:
        MySQL connection object
    """
    if 'db' not in g:
        if _connection_pool is None:
            raise RuntimeError("Database not initialized. Call init_app first.")
        g.db = _connection_pool.get_connection()
    return g.db


def close_db(error=None):
    """
    Close the database connection at the end of the request.
    
    Args:
        error: Exception if one occurred during the request
    """
    db = g.pop('db', None)
    if db is not None:
        if error:
            db.rollback()
        db.close()


def execute_query(query, params=None, fetch_one=False, fetch_all=True, commit=False):
    """
    Execute a SQL query and return results.
    
    Args:
        query: SQL query string
        params: Tuple of parameters for the query
        fetch_one: If True, return only one row
        fetch_all: If True, return all rows (default)
        commit: If True, commit the transaction
    
    Returns:
        Query results as list of dicts, single dict, or None
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(query, params or ())
        
        if commit:
            conn.commit()
            # For INSERT, return the last inserted ID
            if cursor.lastrowid:
                return cursor.lastrowid
            return cursor.rowcount
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        
        return None
    except mysql.connector.Error as err:
        conn.rollback()
        raise
    finally:
        cursor.close()


def execute_many(query, data_list, commit=True):
    """
    Execute a query multiple times with different parameters.
    
    Args:
        query: SQL query string with placeholders
        data_list: List of tuples containing parameters
        commit: If True, commit the transaction
    
    Returns:
        Number of rows affected
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.executemany(query, data_list)
        if commit:
            conn.commit()
        return cursor.rowcount
    except mysql.connector.Error as err:
        conn.rollback()
        raise
    finally:
        cursor.close()


def commit():
    """Commit the current transaction."""
    conn = get_db()
    conn.commit()


def rollback():
    """Rollback the current transaction."""
    conn = get_db()
    conn.rollback()
