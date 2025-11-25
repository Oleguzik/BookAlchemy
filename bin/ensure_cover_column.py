#!/usr/bin/env python3
"""
Ensure `cover_url` column exists in the `book` table.

This is a small helper for development when running without Flask-Migrate.
It checks the `book` table's columns and performs a simple ALTER TABLE to add
the `cover_url` column when missing. This is only intended for local development
and small schema changes; in production use Flask-Migrate/Alembic.
"""
import sys
from sqlalchemy import inspect, text

try:
    from app import app
    from data_models import db
except Exception as exc:
    print('Error: cannot import app or db. Run from project root with the venv active.')
    print(exc)
    sys.exit(2)


def ensure_cover_url():
    with app.app_context():
        inspector = inspect(db.engine)
        if 'book' not in inspector.get_table_names():
            print('Table `book` does not exist; nothing to do.')
            return
        cols = [c['name'] for c in inspector.get_columns('book')]
        if 'cover_url' in cols:
            print('`cover_url` already exists on book table.')
            return
        print('Adding `cover_url` column to `book` table...')
        # Use a lenient column definition compatible with sqlite and other DBs.
        try:
            db.session.execute(text('ALTER TABLE book ADD COLUMN cover_url VARCHAR(512)'))
            db.session.commit()
            print('Done. Column added.')
        except Exception as exc:
            print('Failed to add column:', exc)
            print('If you use Flask-Migrate, consider running alembic migrations instead.')


if __name__ == '__main__':
    ensure_cover_url()
