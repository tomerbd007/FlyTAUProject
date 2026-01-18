"""MySQL connection pool and query execution."""
import mysql.connector
from mysql.connector import pooling
from flask import current_app, g


_connection_pool = None
_db_available = False


def init_app(app):
    """Initialize connection pool with Flask app config."""
    global _connection_pool, _db_available
    
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
        _db_available = True
        app.logger.info("Database connection pool created successfully")
    except mysql.connector.Error as err:
        _db_available = False
        app.logger.warning(f"Database not available at startup: {err}")
        app.logger.warning("App will start but DB operations will fail until DB is available")
        # Don't raise - let the app start without DB
    
    app.teardown_appcontext(close_db)


def is_db_available():
    """Check if database connection is available."""
    return _db_available

def get_db():
    """Get connection from pool (reused per request)."""
    if 'db' not in g:
        if _connection_pool is None:
            raise RuntimeError("Database not initialized. Call init_app first.")
        g.db = _connection_pool.get_connection()
    return g.db


def close_db(error=None):
    """Return connection to pool at end of request."""
    db = g.pop('db', None)
    if db is not None:
        if error:
            db.rollback()
        db.close()


def execute_query(query, params=None, fetch_one=False, fetch_all=True, commit=False):
    """Execute SQL and return results as dicts. Use commit=True for INSERT/UPDATE/DELETE."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(query, params or ())
        
        if commit:
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        
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
    """Execute same query with multiple parameter sets."""
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
    get_db().commit()


def rollback():
    get_db().rollback()
