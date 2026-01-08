#!/usr/bin/env python3
"""
FLYTAU Application Entry Point

Run with:
    python run.py

Or for production with gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5001 "app:create_app()"
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5001,  # Changed from 5000 - macOS uses 5000 for AirPlay
        debug=False,  # Disabled to avoid conda/venv ctypes conflict
        use_reloader=False
    )
