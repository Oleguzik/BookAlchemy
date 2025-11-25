import sys
import os
import pytest
# Add project root to sys.path so `app` is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from data_models import db, Author, Book


@pytest.fixture
def client():
    # Use an in-memory SQLite DB to avoid touching the project DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_admin_page_lists_authors_and_books(client):
    with app.app_context():
        a = Author(name='Alice')
        db.session.add(a)
        db.session.commit()
        b = Book(isbn='111', title='Alice Book', author_id=a.id)
        db.session.add(b)
        db.session.commit()

        rv = client.get('/admin')
        assert rv.status_code == 200
        body = rv.get_data(as_text=True)
        assert 'Alice' in body
        assert 'Alice Book' in body


def test_admin_delete_book_and_author(client):
    with app.app_context():
        a = Author(name='Bob')
        db.session.add(a)
        db.session.commit()
        b = Book(isbn='222', title='Bob Book', author_id=a.id)
        db.session.add(b)
        db.session.commit()

        # Delete book
        rv = client.post(f'/admin/delete_book/{b.id}')
        assert rv.status_code in (302, 200)
        assert Book.query.filter_by(id=b.id).first() is None

        # Delete author
        rv = client.post(f'/admin/delete_author/{a.id}')
        assert rv.status_code in (302, 200)
        assert Author.query.filter_by(id=a.id).first() is None
