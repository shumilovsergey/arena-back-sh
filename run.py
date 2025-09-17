#!/usr/bin/env python3
"""
Main application entry point
"""

from app import create_app
from app.constants import FLASK_HOST, FLASK_PORT, FLASK_DEBUG

app = create_app()

if __name__ == '__main__':
    print(f"Starting Flask app on {FLASK_HOST}:{FLASK_PORT}")
    print(f"Debug mode: {FLASK_DEBUG}")

    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )