import sys
import os
import pytest
# Add project root to sys.path so `app` is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from data_models import db, Author, Book


@pytest.fixture
def app():
    test_app = create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_delete_book_removes_book(client, app):
    """Test that DELETE /book/<id>/delete removes the book when author has multiple books."""
    with app.app_context():
        # Create author and two books
        a = Author(name='Test Author')
        db.session.add(a)
        db.session.commit()
        
        b1 = Book(isbn='123', title='Test Book 1', author_id=a.id)
        b2 = Book(isbn='124', title='Test Book 2', author_id=a.id)
        db.session.add(b1)
        db.session.add(b2)
        db.session.commit()
        
        book_id = b1.id
        author_id = a.id
        
        # Verify books exist
        assert Book.query.get(book_id) is not None
        assert Author.query.count() == 1
        
        # Delete the first book (not last book)
        rv = client.post(f'/book/{book_id}/delete', follow_redirects=True)
        assert rv.status_code == 200
        
        # Verify book is deleted
        assert Book.query.get(book_id) is None
        
        # Verify author still exists
        assert Author.query.get(author_id) is not None
        assert Author.query.count() == 1


def test_delete_book_with_multiple_books_keeps_author(client, app):
    """Test that deleting one book keeps the author if they have other books."""
    with app.app_context():
        # Create author and two books
        a = Author(name='Prolific Author')
        db.session.add(a)
        db.session.commit()
        
        b1 = Book(isbn='111', title='Book One', author_id=a.id)
        b2 = Book(isbn='222', title='Book Two', author_id=a.id)
        db.session.add(b1)
        db.session.add(b2)
        db.session.commit()
        
        book_id = b1.id
        
        # Delete first book
        rv = client.post(f'/book/{book_id}/delete', follow_redirects=True)
        assert rv.status_code == 200
        
        # Verify book is deleted
        assert Book.query.get(book_id) is None
        
        # Verify author still exists (has one book left)
        assert Author.query.count() == 1
        assert Book.query.count() == 1


def test_delete_book_orphaned_author(client, app):
    """Test that deleting author's last book shows confirmation page."""
    with app.app_context():
        # Create author and single book
        a = Author(name='Solo Author')
        db.session.add(a)
        db.session.commit()
        
        b = Book(isbn='999', title='Only Book', author_id=a.id)
        db.session.add(b)
        db.session.commit()
        
        book_id = b.id
        
        # Try to delete the book (should redirect to confirmation)
        rv = client.post(f'/book/{book_id}/delete')
        assert rv.status_code == 302  # Redirect to confirmation page
        assert 'confirm_delete' in rv.location


def test_delete_book_keep_author_on_last_book(client, app):
    """Test that user can keep author when deleting their last book."""
    with app.app_context():
        # Create author and single book
        a = Author(name='Solo Author')
        db.session.add(a)
        db.session.commit()
        
        b = Book(isbn='999', title='Only Book', author_id=a.id)
        db.session.add(b)
        db.session.commit()
        
        author_id = a.id
        book_id = b.id
        
        # First get confirmation page
        rv = client.get(f'/book/{book_id}/confirm_delete')
        assert rv.status_code == 200
        body = rv.get_data(as_text=True)
        assert "Solo Author" in body
        assert "Only Book" in body
        
        # Submit form to keep author (delete_author=no)
        rv = client.post(f'/book/{book_id}/confirm_delete', 
                        data={'delete_author': 'no'}, 
                        follow_redirects=True)
        assert rv.status_code == 200
        
        # Verify book is deleted
        assert Book.query.get(book_id) is None
        
        # Verify author is still in database
        assert Author.query.get(author_id) is not None


def test_delete_book_and_author_on_last_book(client, app):
    """Test that user can delete author when deleting their last book."""
    with app.app_context():
        # Create author and single book
        a = Author(name='Solo Author')
        db.session.add(a)
        db.session.commit()
        
        b = Book(isbn='999', title='Only Book', author_id=a.id)
        db.session.add(b)
        db.session.commit()
        
        author_id = a.id
        book_id = b.id
        
        # Submit form to delete both book and author (delete_author=yes)
        rv = client.post(f'/book/{book_id}/confirm_delete', 
                        data={'delete_author': 'yes'}, 
                        follow_redirects=True)
        assert rv.status_code == 200
        
        # Verify book is deleted
        assert Book.query.get(book_id) is None
        
        # Verify author is also deleted
        assert Author.query.get(author_id) is None
        assert Author.query.count() == 0


def test_delete_book_redirect_to_home(client, app):
    """Test that delete redirects to home page when not the last book."""
    with app.app_context():
        a = Author(name='Author')
        db.session.add(a)
        db.session.commit()
        
        b1 = Book(isbn='555', title='Book 1', author_id=a.id)
        b2 = Book(isbn='556', title='Book 2', author_id=a.id)
        db.session.add(b1)
        db.session.add(b2)
        db.session.commit()
        
        book_id = b1.id
        
        # Delete without following redirects (should redirect to home)
        rv = client.post(f'/book/{book_id}/delete')
        assert rv.status_code == 302  # Redirect status
        assert rv.location.endswith('/')  # Redirects to home
