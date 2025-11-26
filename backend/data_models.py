"""
Simple data models module for BookAlchemy demo.
This file defines the `db` object used by the Flask application.

Models like `Author` and `Book` will be implemented in later steps.
"""

from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy "db" object.
# This will be initialized by the Flask app using `db.init_app(app)`.
# Keep the models in this file when you're ready.

db = SQLAlchemy()


class Author(db.Model):
    """Simple Author model with basic metadata."""
    __tablename__ = 'author'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Author id={self.id} name={self.name!r}>"

    def __str__(self):
        # human-friendly display
        return f"{self.name} (id={self.id})"


class Book(db.Model):
    """Book model referencing an Author with a foreign key."""
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
# Optional direct link to a cover image (e.g., hosted image URL)
    cover_url = db.Column(db.String(512), nullable=True)
    # User rating for the book (1-10 scale, nullable if not rated)
    rating = db.Column(db.Integer, nullable=True)
    author_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'author.id',
            ondelete='CASCADE'),
        nullable=False)
    # Cached AI recommendation/metadata for this book
    ai_recommendation = db.Column(db.Text, nullable=True)

    # relationship to Author. backref creates .books on Author instances.
    # cascade='all, delete-orphan' ensures books are deleted when author is
    # deleted
    author = db.relationship('Author', backref=db.backref(
        'books', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Book id={self.id} title={self.title!r} isbn={self.isbn!r}>"

    def __str__(self):
        return f"{self.title} by {self.author.name if self.author else 'Unknown'}"


# Note for beginners: do NOT put `db.create_all()` here, because importing
# `app` from this file would cause a circular import (app imports data_models).
# Instead, run the following snippet once from a separate script (we already
# added `init_db.py` which wraps this code safely with `app.app_context()`):
#
# from app import app
# from data_models import db
#
# with app.app_context():
#     db.create_all()
#
# After running, you can comment out or remove the call; the database schema
# will already exist in `data/library.sqlite`.
