#!/usr/bin/env python3
"""
FLYTAU Application Entry Point for AWS Elastic Beanstalk

This file is named 'application.py' and the Flask instance is named 'application'
to match AWS Elastic Beanstalk's default WSGI expectations.

Run locally with:
    python application.py

Or for production with gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5001 "application:application"
"""

import os
from datetime import timedelta
from flask import Flask
from flask_session import Session

from app.config import Config
from app import db
from app.routes import register_routes
from app import register_error_handlers


# ---------------------------------------------------------------------------
# Flask-Session filesystem directory setup
# ---------------------------------------------------------------------------
session_dir = os.path.join(os.getcwd(), "flask_session_data")
if not os.path.exists(session_dir):
    os.makedirs(session_dir)


# ---------------------------------------------------------------------------
# Create and configure the Flask application
# ---------------------------------------------------------------------------
application = Flask(__name__, 
                    template_folder='app/templates',
                    static_folder='app/static')
application.config.from_object(Config)

# Flask-Session filesystem backend configuration
application.config.update(
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR=session_dir,
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_REFRESH_EACH_REQUEST=True,
    SESSION_COOKIE_SECURE=False  # Set to True if using HTTPS
)

# Initialize Flask-Session
Session(application)

# Initialize database connection pool
db.init_app(application)

# Register all routes
register_routes(application)

# Register error handlers
register_error_handlers(application)


# ---------------------------------------------------------------------------
# TEMPORARY: Database setup route for AWS EB deployment
# Remove or disable this route after initial database setup!
# ---------------------------------------------------------------------------
@application.route("/setup_db")
def setup_db():
    """
    Initialize database tables from SQL schema file.
    
    WARNING: This is a TEMPORARY route for initial deployment.
    Remove or protect this route after database setup is complete!
    
    Usage: Visit https://<your-domain>/setup_db after deployment
    """
    try:
        # Try multiple possible schema file locations
        schema_files = [
            "flytau_schema.sql",  # Project root (preferred for EB)
            "sql/00_schema.sql",  # Original location
        ]
        
        sql_script = None
        used_file = None
        
        for schema_file in schema_files:
            if os.path.exists(schema_file):
                with open(schema_file, "r") as f:
                    sql_script = f.read()
                used_file = schema_file
                break
        
        if sql_script is None:
            return "Error: No schema file found. Checked: " + ", ".join(schema_files), 404
        
        # Execute the SQL script
        conn = db.get_db()
        cursor = conn.cursor()
        
        try:
            # Execute multi-statement SQL
            for result in cursor.execute(sql_script, multi=True):
                pass  # Consume all results
            conn.commit()
        finally:
            cursor.close()
        
        return f"Success! Tables created from {used_file}."
    except Exception as e:
        return f"Error running SQL file: {str(e)}", 500


@application.route("/setup_db_seed")
def setup_db_seed():
    """
    Load seed data into the database.
    
    WARNING: This is a TEMPORARY route for initial deployment.
    Remove or protect this route after seeding is complete!
    
    Usage: Visit https://<your-domain>/setup_db_seed after /setup_db
    """
    try:
        seed_files = [
            "flytau_seed.sql",  # Project root (preferred for EB)
            "sql/01_seed_fixed.sql",  # Original location
        ]
        
        sql_script = None
        used_file = None
        
        for seed_file in seed_files:
            if os.path.exists(seed_file):
                with open(seed_file, "r") as f:
                    sql_script = f.read()
                used_file = seed_file
                break
        
        if sql_script is None:
            return "Error: No seed file found. Checked: " + ", ".join(seed_files), 404
        
        conn = db.get_db()
        cursor = conn.cursor()
        
        try:
            for result in cursor.execute(sql_script, multi=True):
                pass
            conn.commit()
        finally:
            cursor.close()
        
        return f"Success! Seed data loaded from {used_file}."
    except Exception as e:
        return f"Error running seed file: {str(e)}", 500


# ---------------------------------------------------------------------------
# Local development server
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    application.run(
        host='127.0.0.1',
        port=5001,  # Changed from 5000 - macOS uses 5000 for AirPlay
        debug=False,  # Disabled to avoid conda/venv ctypes conflict
        use_reloader=False
    )
