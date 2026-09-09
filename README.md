# BookAlchemy 📚

Personal library manager built with Flask — CRUD for books and authors, a 1–10 rating system, and an AI-powered review feature.

## What it does

- Full book/author management: add, browse, search, sort, delete — including cascade handling when deleting an author's last book (keep the author record, or remove both)
- 1–10 star rating system with live UI feedback
- AI-generated book reviews via an external LLM API (RapidAPI/Llama), cached in the database and editable by hand
- Environment-based configuration; secrets are never committed

## Tech stack

Flask · SQLAlchemy ORM · SQLite · Jinja2 · pytest (isolated test databases) · Flask-Migrate

## A few design decisions

- **Backend/frontend split even in a single-process app** — routes and models live separately from templates and static assets, so the project reads like a scaled-down version of a real service boundary
- **AI reviews are cached data, not a live dependency** — generated once per book, stored in the database, and only re-fetched on explicit refresh, so the app works offline and doesn't burn API quota on every page load
- **Cascade deletion is a first-class case, not an afterthought** — deleting an author's last book explicitly asks whether to keep or remove the author, and the behavior has dedicated tests

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m backend.init_db
python run.py                    # http://127.0.0.1:5000
```

Or run `bash bin/setup.sh` to do all of the above in one step.

Look for details in rubook.md

## Tests

```bash
pytest tests/ -v
```

Covers CRUD, cascade deletion, search, and the rating flow.

## Project structure

```
BookAlchemy/
├── run.py            # Entry point
├── backend/          # Flask app, SQLAlchemy models, DB init
├── frontend/         # Jinja2 templates + static assets
├── data/             # SQLite DB + seed scripts
└── tests/            # pytest suite
```

## License

MIT (educational project)
