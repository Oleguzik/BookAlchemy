"""Utility script to create the database schema (run once).

Usage:
    source venv/bin/activate
    python init_db.py
"""
from app import app
from data_models import db


def create_schema():
    with app.app_context():
        db.create_all()
        print("Database schema created (tables should now exist).")


if __name__ == '__main__':
    create_schema()
