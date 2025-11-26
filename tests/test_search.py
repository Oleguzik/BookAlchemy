import sys
import os
import pytest

# Add project root to sys.path so `app` is importable
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app as main_app  # noqa: E402
from backend.data_models import db, Author, Book  # noqa: E402


@pytest.fixture
def app():
    from backend.app import create_app
    test_app = create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_book_search(client, app):
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
        # highlighted title will have <mark> tags, so check a fragment exists
        # and a <mark> present
        assert f'Unit Test Book {uid}'.split()[1] in body
        assert '<mark' in body
        # cleanup
        Book.query.filter_by(isbn=uid).delete()
        Author.query.filter_by(name=f'Unit Tester {uid}').delete()
        db.session.commit()


def test_author_search_scope(client, app):
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


def test_book_cover_url_shows_in_home(client, app):
    with app.app_context():
        import uuid
        uid = uuid.uuid4().hex[:8]
        a = Author(name=f'Cover Tester {uid}')
        db.session.add(a)
        db.session.commit()
        cover = f'https://example.com/{uid}.jpg'
        b = Book(
            isbn=uid,
            title=f'Cover Test {uid}',
            author_id=a.id,
            cover_url=cover)
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
