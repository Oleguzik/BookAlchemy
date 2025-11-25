#!/usr/bin/env bash
set -euo pipefail

echo "Setting up BookAlchemy dev environment..."

# Ensure we run from project root regardless of where bin/setup.sh is invoked
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_ROOT"

PYTHON=${PYTHON:-python3}
# use .venv by default if present; otherwise `venv`
VENV_DIR=${VENV_DIR:-.venv}
if [ ! -d "$VENV_DIR" ]; then
  # fallback to venv directory
  VENV_DIR=venv
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv at $VENV_DIR"
  $PYTHON -m venv $VENV_DIR
fi

echo "Activating venv and installing requirements..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Initializing database..."
python init_db.py

echo "Seeding data..."
# Run seeders as modules so Python's import path includes project root
python -m data.seed_authors
python -m data.seed_books

echo "Setup complete. To use the app:"
echo "  source $VENV_DIR/bin/activate"
echo "  flask run --reload"
echo "To use Flask-Migrate for schema changes, run:"
echo "  export FLASK_APP=app.py"
echo "  flask db init # first time only"
echo "  flask db migrate -m 'initial'"
echo "  flask db upgrade"
