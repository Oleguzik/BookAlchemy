"""Seed script to add example authors to the BookAlchemy database.

This script is safe to run multiple times: it checks for the author's
name before adding a new record so duplicates are not created.
"""
from app import app
from data_models import db, Author
from datetime import datetime

AUTHORS = [
    ("Jane Austen", "1775-12-16", "1817-07-18"),
    ("Charles Dickens", "1812-02-07", "1870-06-09"),
    ("Mark Twain", "1835-11-30", "1910-04-21"),
    ("Virginia Woolf", "1882-01-25", "1941-03-28"),
    ("George Orwell", "1903-06-25", "1950-01-21"),
    ("Harper Lee", "1926-04-28", "2016-02-19"),
    ("J.K. Rowling", "1965-07-31", None),
    ("Toni Morrison", "1931-02-18", "2019-08-05"),
    ("Gabriel Garcia Marquez", "1927-03-06", "2014-04-17"),
    ("Fyodor Dostoevsky", "1821-11-11", "1881-02-09"),
]


def parse_date(s):
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%d").date()


def seed_authors():
    with app.app_context():
        for name, b, d in AUTHORS:
            # skip if already exists by name to avoid duplicates
            existing = Author.query.filter_by(name=name).first()
            if existing:
                print(f"Skipping existing author: {name}")
                continue
            a = Author(name=name, birth_date=parse_date(b), date_of_death=parse_date(d))
            db.session.add(a)
        db.session.commit()
        print("Seeding completed.")


if __name__ == "__main__":
    seed_authors()
