"""Seed script to add sample books linked to existing authors.

This script is safe to run multiple times: it checks for existing ISBN/title before creating.
"""
import sys, os
# add project root to path so `from app import app` works when run via module or direct script
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)
from app import app
from data_models import db, Author, Book

SAMPLE_BOOKS = [
    ("Jane Austen", "9780141439518", "Pride and Prejudice", 1813, "https://covers.openlibrary.org/b/isbn/9780141439518-M.jpg"),
    ("Charles Dickens", "9780141439563", "Great Expectations", 1861, "https://covers.openlibrary.org/b/isbn/9780141439563-M.jpg"),
    ("Mark Twain", "9780141439648", "Adventures of Huckleberry Finn", 1884, "https://covers.openlibrary.org/b/isbn/9780141439648-M.jpg"),
    ("Virginia Woolf", "9780156907392", "Mrs Dalloway", 1925, "https://covers.openlibrary.org/b/isbn/9780156907392-M.jpg"),
    ("George Orwell", "9780451524935", "1984", 1949, "https://covers.openlibrary.org/b/isbn/9780451524935-M.jpg"),
    ("Harper Lee", "9780061120084", "To Kill a Mockingbird", 1960, "https://covers.openlibrary.org/b/isbn/9780061120084-M.jpg"),
    ("J.K. Rowling", "9780747532743", "Harry Potter and the Philosopher's Stone", 1997, "https://covers.openlibrary.org/b/isbn/9780747532743-M.jpg"),
    ("Toni Morrison", "9780307277671", "Beloved", 1987, "https://covers.openlibrary.org/b/isbn/9780307277671-M.jpg"),
    ("Gabriel Garcia Marquez", "9780307389732", "One Hundred Years of Solitude", 1967, "https://covers.openlibrary.org/b/isbn/9780307389732-M.jpg"),
    ("Fyodor Dostoevsky", "9780140449136", "Crime and Punishment", 1866, "https://covers.openlibrary.org/b/isbn/9780140449136-M.jpg"),
]


def seed_books():
    with app.app_context():
        for item in SAMPLE_BOOKS:
            # support both 4-tuple and 5-tuple entries (with optional cover_url)
            if len(item) == 5:
                author_name, isbn, title, year, cover_url = item
            else:
                author_name, isbn, title, year = item
                cover_url = None
            # find author by name
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                print(f"Skipping book for missing author: {author_name}")
                continue
            # check if book exists by isbn
            existing = Book.query.filter_by(isbn=isbn).first()
            if existing:
                # update if cover_url is missing
                if not existing.cover_url and cover_url:
                    existing.cover_url = cover_url
                    print(f"Updated cover for existing book: {title}")
                else:
                    print(f"Skipping existing book: {title} (isbn {isbn})")
                continue
            b = Book(isbn=isbn, title=title, publication_year=year, author_id=author.id, cover_url=cover_url)
            db.session.add(b)
        db.session.commit()
        print("Book seeding completed.")


if __name__ == '__main__':
    seed_books()
