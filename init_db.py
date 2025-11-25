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
        print("Note: For production or historic schema management, use Flask-Migrate and run `flask db init/migrate/upgrade` instead of `create_all()`.")
        # Optionally ensure small development-only columns are present
        try:
            from bin.ensure_cover_column import ensure_cover_url
            ensure_cover_url()
        except Exception:
            # Skip if script can't run (e.g., example or packaging)
            pass


if __name__ == '__main__':
    create_schema()
