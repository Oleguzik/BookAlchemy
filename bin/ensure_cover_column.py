#!/usr/bin/env python3
"""
Ensure `cover_url` column exists in the `book` table.

This is a small helper for development when running without Flask-Migrate.
It checks the `book` table's columns and performs a simple ALTER TABLE to add
the `cover_url` column when missing. This is only intended for local development
and small schema changes; in production use Flask-Migrate/Alembic.
"""
import sys
import os
from sqlalchemy import inspect, text

# Ensure project root is on sys.path when executed from bin/
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

try:
    from app import app
    from data_models import db
except Exception as exc:
    # We will still attempt to patch the local sqlite file directly.
    app = None
    db = None
    fallback_msg = f"Cannot import app/db ({exc}). Falling back to raw sqlite access if possible."
    print(fallback_msg)


def ensure_cover_url():
    if app and db:
        with app.app_context():
            inspector = inspect(db.engine)
            if 'book' not in inspector.get_table_names():
                print('Table `book` does not exist; nothing to do.')
                return
            cols = [c['name'] for c in inspector.get_columns('book')]
            if 'cover_url' in cols:
                print('`cover_url` already exists on book table.')
                return
            print('Adding `cover_url` column to `book` table via SQLAlchemy engine...')
            try:
                db.session.execute(text('ALTER TABLE book ADD COLUMN cover_url VARCHAR(512)'))
                db.session.commit()
                print('Done. Column added.')
                return
            except Exception as exc:
                print('Failed to add column via SQLAlchemy:', exc)
                print('Falling back to raw sqlite alter...')

    # Fallback: try sqlite3 direct ALTER TABLE (works for local sqlite files)
    # Try to find DB file; prefer SQLAlchemy config if available
    if db and app:
        try:
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if db_uri and db_uri.startswith('sqlite:///'):
                db_file = db_uri.replace('sqlite:///', '')
            else:
                db_file = 'data/library.sqlite'
        except Exception:
            db_file = 'data/library.sqlite'
    else:
        db_file = 'data/library.sqlite'

    import sqlite3
    if not os.path.exists(db_file):
        print('DB file does not exist:', db_file)
        return
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info('book')")
        cols = [r[1] for r in cur.fetchall()]
        if 'cover_url' in cols:
            print('`cover_url` already exists on book table (sqlite).')
            return
        print('Adding `cover_url` column to `book` table via sqlite3...')
        cur.execute('ALTER TABLE book ADD COLUMN cover_url VARCHAR(512)')
        conn.commit()
        print('Done. Column added.')
    except Exception as exc:
        print('Failed to add column via sqlite3:', exc)
    finally:
        conn.close()


if __name__ == '__main__':
    ensure_cover_url()
