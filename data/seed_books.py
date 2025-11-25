"""Seed script to add sample books linked to existing authors.

This script is safe to run multiple times: it checks for existing ISBN/title before creating.
"""
from app import app
from data_models import db, Author, Book

SAMPLE_BOOKS = [
    ("Jane Austen", "9780141439518", "Pride and Prejudice", 1813),
    ("Charles Dickens", "9780141439563", "Great Expectations", 1861),
    ("Mark Twain", "9780141439648", "Adventures of Huckleberry Finn", 1884),
    ("Virginia Woolf", "9780156907392", "Mrs Dalloway", 1925),
    ("George Orwell", "9780451524935", "1984", 1949),
    ("Harper Lee", "9780061120084", "To Kill a Mockingbird", 1960),
    ("J.K. Rowling", "9780747532743", "Harry Potter and the Philosopher's Stone", 1997),
    ("Toni Morrison", "9780307277671", "Beloved", 1987),
    ("Gabriel Garcia Marquez", "9780307389732", "One Hundred Years of Solitude", 1967),
    ("Fyodor Dostoevsky", "9780140449136", "Crime and Punishment", 1866),
]


def seed_books():
    with app.app_context():
        for author_name, isbn, title, year in SAMPLE_BOOKS:
            # find author by name
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                print(f"Skipping book for missing author: {author_name}")
                continue
            # skip if isbn already exists
            existing = Book.query.filter_by(isbn=isbn).first()
            if existing:
                print(f"Skipping existing book: {title} (isbn {isbn})")
                continue
            b = Book(isbn=isbn, title=title, publication_year=year, author_id=author.id)
            db.session.add(b)
        db.session.commit()
        print("Book seeding completed.")


if __name__ == '__main__':
    seed_books()
