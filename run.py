"""
Main entry point for BookAlchemy application.

This file imports the Flask app from the backend package and runs it.
Use this file to start the development server.

Usage:
    python run.py
"""

from backend.app import app

if __name__ == '__main__':
    # Bind to 0.0.0.0 for Codio deployment (makes app accessible externally)
    app.run(host='0.0.0.0', port=5002, debug=True)
