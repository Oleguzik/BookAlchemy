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


def test_book_search(client):
    with app.app_context():
        # create author and book
        import uuid
        uid = uuid.uuid4().hex[:8]
        a = Author(name=f'Unit Tester {uid}')
        db.session.add(a)
        db.session.commit()
        b = Book(isbn=uid, title=f'Unit Test Book {uid}', author_id=a.id)
        db.session.add(b)
        db.session.commit()

        rv = client.get('/?q=Unit')
        assert rv.status_code == 200
        body = rv.get_data(as_text=True)
        # highlighted title will have <mark> tags, so check a fragment exists and a <mark> present
        assert f'Unit Test Book {uid}'.split()[1] in body
        assert '<mark' in body
        # cleanup
        Book.query.filter_by(isbn=uid).delete()
        Author.query.filter_by(name=f'Unit Tester {uid}').delete()
        db.session.commit()


def test_author_search_scope(client):
    with app.app_context():
        import uuid
        uid = uuid.uuid4().hex[:8]
        a = Author(name=f'Search Author {uid}')
        db.session.add(a)
        db.session.commit()
        rv = client.get('/?q=Search&scope=authors')
        assert rv.status_code == 200
        body = rv.get_data(as_text=True)
        assert f'Author {uid}' in body
        assert '<mark' in body
        # cleanup
        Author.query.filter_by(name=f'Search Author {uid}').delete()
        db.session.commit()


def test_book_cover_url_shows_in_home(client):
    with app.app_context():
        import uuid
        uid = uuid.uuid4().hex[:8]
        a = Author(name=f'Cover Tester {uid}')
        db.session.add(a)
        db.session.commit()
        cover = f'https://example.com/{uid}.jpg'
        b = Book(isbn=uid, title=f'Cover Test {uid}', author_id=a.id, cover_url=cover)
        db.session.add(b)
        db.session.commit()

        rv = client.get('/')
        assert rv.status_code == 200
        body = rv.get_data(as_text=True)
        assert cover in body
        # cleanup
        Book.query.filter_by(isbn=uid).delete()
        Author.query.filter_by(name=f'Cover Tester {uid}').delete()
        db.session.commit()
