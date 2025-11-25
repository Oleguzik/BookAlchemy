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
### Book cover images

You can provide a direct URL for a book cover by setting the `Cover URL` field when adding or editing a book from the UI.
If a `cover_url` is present, the app will show that image. If `cover_url` is not provided, the app will fall back to the Open Library cover service based on the ISBN (if provided). If neither is available, no cover image will be displayed.

To add fund of example cover URLs for seeded books, `data/seed_books.py` includes a few open library links for demo purposes.
### Fixing the OperationalError: missing column (dev only)

If you see an error like:

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: book.cover_url
```

It means you've updated the model but your SQLite DB file has not been migrated. For development you have these options:

- Easiest (safe for local development): run the small helper that adds the column (only if missing):

```bash
source .venv/bin/activate  # or `venv/bin/activate`
python bin/ensure_cover_column.py
```

- Ideally: use Flask-Migrate (Alembic) to add migrations and apply them:

```bash
pip install Flask-Migrate
export FLASK_APP=app.py
flask db migrate -m "Add cover_url to Book"
flask db upgrade
```

- If you don't care about existing data during development: drop and re-create the DB file + re-seed

```bash
python reset_db.py --force-kill --yes
```

Choose the option that matches your use case; the first helper is a lightweight option if you want to avoid using migrations while still preserving data.



### Setup script

For convenience, there's a `bin/setup.sh` script that will create a virtualenv, install requirements, run `init_db.py`, and seed the database:

```bash
bash bin/setup.sh
```


Open http://127.0.0.1:5000/

