#!/usr/bin/env python3
"""
Safe database reset utility for BookAlchemy (development only)

Usage:
    python reset_db.py [--no-backup] [--remove-file] [--drop-tables] [--no-seed] [--force-kill] [--yes]

Default behavior:
 - Backs up data/library.sqlite to backups/
 - Drops tables and recreates schema (db.create_all())
 - Runs seed_authors.py and seed_books.py

Options:
 - --no-backup     : skip creating backup
 - --remove-file   : instead of drop/create tables, delete the sqlite file entirely before recreating
 - --drop-tables   : drop all tables then recreate
 - --no-seed       : skip running seed scripts
 - --force-kill    : kill running Flask/Python processes before proceeding
 - --yes           : do not prompt for confirmation

NOTE: This script is intended for local development convenience only.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
import signal
from datetime import datetime

# Helper: import app and db
try:
    from app import app
    from data_models import db
except Exception as e:
    print('Error: Could not import app or db from project. Ensure you run this script from the project root and use the venv.')
    print(e)
    sys.exit(1)


def is_port_in_use(port=5000):
    try:
        out = subprocess.run(["lsof", "-iTCP:%d" % port, "-sTCP:LISTEN", "-P", "-n"], capture_output=True, text=True)
        return out.stdout.strip()
    except FileNotFoundError:
        return ""


def find_app_pids(port=5000):
    # Returns PID list for python processes listening on the port
    text = is_port_in_use(port)
    pids = set()
    if not text:
        return []
    for line in text.splitlines()[1:]:  # skip header
        parts = line.split()
        if len(parts) >= 2:
            pid = parts[1]
            # Filter to python processes or app references
            name = parts[0].lower()
            if 'python' in name or 'python3' in name or 'controlcenter' in name:
                pids.add(int(pid))
    return list(pids)


def kill_pids(pids, sig=signal.SIGTERM, timeout=3):
    for pid in pids:
        try:
            os.kill(pid, sig)
        except Exception as e:
            print(f'Failed to kill {pid}: {e}')
    # wait
    t0 = time.time()
    while time.time() - t0 < timeout:
        alive = [p for p in pids if os.path.exists(f"/proc/{p}")] if sys.platform != 'darwin' else []
        if not alive:
            return True
        time.sleep(0.2)
    # If still alive, try SIGKILL
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except Exception:
            pass
    return True


def backup_db(db_path, backup_dir='backups'):
    os.makedirs(backup_dir, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d%H%M%S')
    bname = os.path.basename(db_path)
    dst = os.path.join(backup_dir, f"{bname}.{stamp}")
    shutil.copy2(db_path, dst)
    # Try to also create SQL dump if sqlite3 is available
    try:
        dumpfile = os.path.join(backup_dir, f"{bname}.{stamp}.sql")
        subprocess.run(['sqlite3', db_path, '.dump'], capture_output=True, text=True, check=True)
        with open(dumpfile, 'w') as f:
            r = subprocess.run(['sqlite3', db_path, '.dump'], capture_output=True, text=True, check=True)
            f.write(r.stdout)
    except Exception:
        # ignore if sqlite3 not available
        pass
    return dst


def recreate_schema(remove_file=False, drop_tables=True):
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if not db_uri or not db_uri.startswith('sqlite'):
        print('Warning: Non-sqlite DB or not configured; attempting to drop/recreate via SQLAlchemy')
    if remove_file:
        # Only delete the sqlite file if it's really a sqlite URI
        if db_uri and db_uri.startswith('sqlite:///'):
            path = db_uri.replace('sqlite:///', '')
            if os.path.exists(path):
                os.remove(path)
                print('Removed DB file:', path)
        # recreate with create_all
        with app.app_context():
            db.create_all()
        return

    with app.app_context():
        if drop_tables:
            db.drop_all()
            print('Dropped all tables')
        db.create_all()
        print('Created tables')


def run_seed_scripts():
    try:
        import seed_authors
        import seed_books
        with app.app_context():
            seed_authors.seed_authors()
            seed_books.seed_books()
    except Exception as e:
        print('Failed to run seed scripts:', e)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description='Reset development DB safely')
    parser.add_argument('--no-backup', action='store_true', help='Do not backup existing DB')
    parser.add_argument('--remove-file', action='store_true', help='Delete the DB file instead of dropping tables')
    parser.add_argument('--drop-tables', action='store_true', default=True, help='Drop tables (default)')
    parser.add_argument('--no-seed', action='store_true', help='Do not run seed scripts')
    parser.add_argument('--force-kill', action='store_true', help='Force-kill any Flask processes on port 5000')
    parser.add_argument('--yes', action='store_true', help='Do not prompt for confirmation')
    args = parser.parse_args()

    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if not db_uri or not db_uri.startswith('sqlite'):
        print('This script currently only supports sqlite databased via SQLALCHEMY_DATABASE_URI in app config.')
        sys.exit(1)
    db_path = db_uri.replace('sqlite:///', '')

    print('Database file:', db_path)
    if not os.path.exists(db_path):
        print('(note) DB file does not exist yet, will be created by init or create_all')

    pids = find_app_pids(5000)
    if pids:
        print('Found running processes on port 5000 (likely your app):', pids)
        if not args.force_kill:
            print('Please stop your app (or use --force-kill to terminate) and re-run this script')
            sys.exit(1)
        else:
            print('Killing pids:', pids)
            kill_pids(pids)
            time.sleep(0.5)

    if os.path.exists(db_path):
        if not args.no_backup:
            b = backup_db(db_path)
            print('Backup created at', b)
    else:
        print('No existing DB file found, proceeding to create one...')

    # Confirm
    print('\nActions to perform:')
    print('- Recreate DB schema (drop-tables=%s, remove-file=%s)' % (args.drop_tables, args.remove_file))
    print('- Run seeds: %s' % (not args.no_seed))
    if not args.yes:
        ok = input('Continue? [y/N] ').strip().lower()
        if ok not in ('y', 'yes'):
            print('Aborted')
            sys.exit(0)

    # Recreate schema
    recreate_schema(remove_file=args.remove_file, drop_tables=args.drop_tables)

    # Seed
    if not args.no_seed:
        print('Seeding authors and books...')
        ok = run_seed_scripts()
        if ok:
            print('Seeding completed')
        else:
            print('Seeding encountered issues')

    print('Done. DB is ready.')


if __name__ == '__main__':
    main()
