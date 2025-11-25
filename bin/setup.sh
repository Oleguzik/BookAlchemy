#!/usr/bin/env bash
set -euo pipefail

echo "Setting up BookAlchemy dev environment..."

PYTHON=${PYTHON:-python3}
VENV_DIR=venv

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
python data/seed_authors.py
python data/seed_books.py

echo "Setup complete. To use the app:"
echo "  source $VENV_DIR/bin/activate"
echo "  flask run --reload"
echo "To use Flask-Migrate for schema changes, run:"
echo "  export FLASK_APP=app.py"
echo "  flask db init # first time only"
echo "  flask db migrate -m 'initial'"
echo "  flask db upgrade"
