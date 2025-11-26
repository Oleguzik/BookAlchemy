"""
Main entry point for BookAlchemy application.

This file imports the Flask app from the backend package and runs it.
Use this file to start the development server.

Usage:
    python run.py
"""

from backend.app import app

if __name__ == '__main__':
    app.run(port=5002, debug=True)
