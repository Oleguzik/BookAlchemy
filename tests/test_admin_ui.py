import sys
import os
import pytest
# Add project root to sys.path so `app` is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as main_app
from data_models import db, Author, Book


@pytest.fixture
def app():
    from app import create_app
    test_app = create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_admin_page_lists_authors_and_books(client, app):
    with app.app_context():
        a = Author(name='Alice')
        db.session.add(a)
        db.session.commit()
        b = Book(isbn='111', title='Alice Book', author_id=a.id, cover_url='https://example.org/111.jpg')
        db.session.add(b)
        db.session.commit()

        rv = client.get('/admin')
        assert rv.status_code == 200
        body = rv.get_data(as_text=True)
        assert 'Alice' in body
        assert 'Alice Book' in body
        assert 'https://example.org/111.jpg' in body


def test_admin_delete_book_and_author(client, app):
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
