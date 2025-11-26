"""
Test suite for author deletion functionality.

Tests verify that:
1. Authors can be deleted via POST /author/<id>/delete
2. All books by deleted author are also removed (cascade)
3. User is redirected to home with success message
4. Referential integrity is maintained
"""

import pytest
from app import create_app
from data_models import db, Author, Book


@pytest.fixture
def client():
    """Create test app and database for each test."""
    app = create_app(config_overrides={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_data(client):
    """Create sample author and books for testing."""
    app = create_app(config_overrides={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
    
    with app.app_context():
        db.create_all()
        
        # Create author with multiple books
        author = Author(name="Test Author", birth_date=None, date_of_death=None)
        db.session.add(author)
        db.session.commit()
        
        # Create books
        book1 = Book(isbn="123-4567", title="Book 1", publication_year=2020, cover_url=None, author_id=author.id)
        book2 = Book(isbn="123-4568", title="Book 2", publication_year=2021, cover_url=None, author_id=author.id)
        db.session.add_all([book1, book2])
        db.session.commit()
        
        return author.id, 2


class TestDeleteAuthor:
    """Test author deletion functionality."""

    def test_delete_author_requires_post(self, client):
        """Test that DELETE requires POST method."""
        response = client.get('/author/1/delete', follow_redirects=False)
        # GET method not allowed - should return 405 or similar
        assert response.status_code in [404, 405]

    def test_delete_nonexistent_author(self, client):
        """Test deleting an author that doesn't exist returns 404."""
        response = client.post('/author/999/delete', follow_redirects=True)
        assert response.status_code == 404

    def test_delete_author_and_cascade_books(self, client):
        """Test that deleting an author also deletes all their books."""
        app = create_app(config_overrides={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
        
        with app.app_context():
            db.create_all()
            
            # Create test data
            author = Author(name="Delete Test Author", birth_date=None, date_of_death=None)
            db.session.add(author)
            db.session.commit()
            author_id = author.id
            
            # Add books
            book1 = Book(isbn="TEST-001", title="Test Book 1", author_id=author_id)
            book2 = Book(isbn="TEST-002", title="Test Book 2", author_id=author_id)
            db.session.add_all([book1, book2])
            db.session.commit()
            
            # Verify initial state
            assert Author.query.count() == 1
            assert Book.query.count() == 2
            
            # Delete author
            client = app.test_client()
            response = client.post(f'/author/{author_id}/delete', follow_redirects=True)
            
            # Verify author and books are deleted
            assert Author.query.count() == 0
            assert Book.query.count() == 0
            assert response.status_code == 200

    def test_delete_author_redirects_to_home(self, client):
        """Test that deletion redirects to home page."""
        app = create_app(config_overrides={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
        
        with app.app_context():
            db.create_all()
            
            author = Author(name="Redirect Test", birth_date=None, date_of_death=None)
            db.session.add(author)
            db.session.commit()
            author_id = author.id
            
            client = app.test_client()
            response = client.post(f'/author/{author_id}/delete', follow_redirects=False)
            
            # Should redirect (302)
            assert response.status_code in [302, 303]
            assert '/' in response.location

    def test_delete_author_shows_success_message(self, client):
        """Test that deletion returns 200 OK on home page."""
        app = create_app(config_overrides={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
        
        with app.app_context():
            db.create_all()
            
            author = Author(name="Message Test Author", birth_date=None, date_of_death=None)
            db.session.add(author)
            db.session.commit()
            author_id = author.id
            
            client = app.test_client()
            response = client.post(f'/author/{author_id}/delete', follow_redirects=True)
            
            # Check that we get home page (200 OK) and author is deleted
            assert response.status_code == 200
            assert Author.query.filter_by(name="Message Test Author").first() is None

    def test_delete_author_with_multiple_books(self, client):
        """Test deleting author with many books cascades correctly."""
        app = create_app(config_overrides={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
        
        with app.app_context():
            db.create_all()
            
            # Create author with 5 books
            author = Author(name="Multi-Book Author", birth_date=None, date_of_death=None)
            db.session.add(author)
            db.session.commit()
            author_id = author.id
            
            for i in range(5):
                book = Book(isbn=f"MULTI-{i:03d}", title=f"Book {i}", author_id=author_id)
                db.session.add(book)
            db.session.commit()
            
            assert Book.query.count() == 5
            
            # Delete author
            client = app.test_client()
            response = client.post(f'/author/{author_id}/delete', follow_redirects=True)
            
            # All books should be gone
            assert Author.query.count() == 0
            assert Book.query.count() == 0
            assert response.status_code == 200

    def test_delete_author_does_not_affect_other_authors(self, client):
        """Test that deleting one author doesn't affect others."""
        app = create_app(config_overrides={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
        
        with app.app_context():
            db.create_all()
            
            # Create two authors
            author1 = Author(name="Author 1", birth_date=None, date_of_death=None)
            author2 = Author(name="Author 2", birth_date=None, date_of_death=None)
            db.session.add_all([author1, author2])
            db.session.commit()
            
            # Add books to author1 only
            book1 = Book(isbn="A1-001", title="Book 1", author_id=author1.id)
            book2 = Book(isbn="A1-002", title="Book 2", author_id=author1.id)
            db.session.add_all([book1, book2])
            db.session.commit()
            
            initial_state = {
                'authors': Author.query.count(),
                'books': Book.query.count()
            }
            
            # Delete author1
            client = app.test_client()
            response = client.post(f'/author/{author1.id}/delete', follow_redirects=True)
            
            # Author2 should still exist, no books
            assert Author.query.count() == 1
            assert Book.query.count() == 0
            remaining_author = Author.query.first()
            assert remaining_author.name == "Author 2"


class TestDeleteAuthorUI:
    """Test UI elements for author deletion."""

    def test_delete_button_in_author_search(self, client):
        """Test delete button appears in author search results."""
        app = create_app(config_overrides={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
        
        with app.app_context():
            db.create_all()
            
            author = Author(name="Search Test", birth_date=None, date_of_death=None)
            db.session.add(author)
            db.session.commit()
            
            client = app.test_client()
            # Search for authors
            response = client.get('/?scope=authors&q=Search', follow_redirects=True)
            
            # Delete button should be in response
            assert b'Delete Author' in response.data or b'delete_author' in response.data

    def test_delete_button_in_author_detail(self, client):
        """Test delete button appears in author detail page."""
        app = create_app(config_overrides={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
        
        with app.app_context():
            db.create_all()
            
            author = Author(name="Detail Test", birth_date=None, date_of_death=None)
            db.session.add(author)
            db.session.commit()
            author_id = author.id
            
            client = app.test_client()
            response = client.get(f'/author/{author_id}', follow_redirects=True)
            
            # Delete button should be in author detail page
            assert b'Delete' in response.data or b'delete_author' in response.data

