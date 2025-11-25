# BookAlchemy

Minimal Flask app demonstrating SQLAlchemy models, routes for adding authors and books, and template examples.

## Quick start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py      # creates data/library.sqlite and tables
python app.py
```
### Optional: Using migrations with Flask-Migrate

If you plan to change the database schema, it's better to use Flask-Migrate (Alembic) instead of calling `db.create_all()`.

After activating the virtual environment and installing requirements, initialize migrations and apply the first migration:

```bash
export FLASK_APP=app.py
flask db init          # only first time
flask db migrate -m "initial"
flask db upgrade
```

This ensures schema changes are tracked and applied reliably.

### Setup script

For convenience, there's a `bin/setup.sh` script that will create a virtualenv, install requirements, run `init_db.py`, and seed the database:

```bash
bash bin/setup.sh
```


Open http://127.0.0.1:5000/

