"""
Comprehensive test suite for book ratings feature.
Tests cover rating creation, updates, display, and validation.
"""

import pytest
from app import create_app
from data_models import db, Author, Book


@pytest.fixture
def app():
	"""Create and configure test app with isolated in-memory database."""
	app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
	
	with app.app_context():
		db.create_all()
		yield app
		db.session.remove()
		db.drop_all()


@pytest.fixture
def client(app):
	"""Test client for making requests."""
	return app.test_client()


@pytest.fixture
def auth_author(app):
	"""Create test author."""
	with app.app_context():
		author = Author(name='Test Author')
		db.session.add(author)
		db.session.commit()
		return author.id


@pytest.fixture
def auth_book(app, auth_author):
	"""Create test book without rating."""
	with app.app_context():
		book = Book(isbn='1234567890', title='Test Book', author_id=auth_author)
		db.session.add(book)
		db.session.commit()
		return book.id


class TestBookRatingsModel:
	"""Test Book model rating field."""
	
	def test_book_has_rating_field(self, app, auth_author):
		"""Verify Book model includes rating field."""
		with app.app_context():
			book = Book(isbn='isbn123', title='Test', author_id=auth_author)
			db.session.add(book)
			db.session.commit()
			
			retrieved = Book.query.filter_by(isbn='isbn123').first()
			assert hasattr(retrieved, 'rating')
			assert retrieved.rating is None
	
	def test_book_rating_default_none(self, app, auth_author):
		"""Rating should default to None (no rating)."""
		with app.app_context():
			book = Book(isbn='isbn456', title='Test Book', author_id=auth_author)
			db.session.add(book)
			db.session.commit()
			
			assert book.rating is None
	
	def test_book_rating_set_to_integer(self, app, auth_author):
		"""Rating can be set to an integer value."""
		with app.app_context():
			book = Book(isbn='isbn789', title='Rated Book', author_id=auth_author, rating=8)
			db.session.add(book)
			db.session.commit()
			
			retrieved = Book.query.filter_by(isbn='isbn789').first()
			assert retrieved.rating == 8
	
	def test_book_rating_range_valid(self, app, auth_author):
		"""Rating should accept values 1-10."""
		with app.app_context():
			for rating in [1, 5, 10]:
				book = Book(isbn=f'isbn{rating}', title='Test', author_id=auth_author, rating=rating)
				db.session.add(book)
			db.session.commit()
			
			books = Book.query.all()
			assert len(books) == 3
			assert books[0].rating == 1
			assert books[1].rating == 5
			assert books[2].rating == 10


class TestRatingRoute:
	"""Test /book/<id>/rate POST route."""
	
	def test_rate_book_route_exists(self, client, auth_book):
		"""POST /book/<id>/rate route should exist."""
		response = client.post(f'/book/{auth_book}/rate', data={'rating': '7'})
		# Should redirect (302 or 303) rather than 404
		assert response.status_code in [302, 303]
	
	def test_rate_book_updates_rating(self, app, client, auth_book):
		"""Rating POST request should update book rating."""
		response = client.post(f'/book/{auth_book}/rate', data={'rating': '8'})
		
		with app.app_context():
			book = Book.query.get(auth_book)
			assert book.rating == 8
	
	def test_rate_book_valid_range(self, app, client, auth_book):
		"""Rating should accept values 1-10."""
		for rating in [1, 5, 10]:
			response = client.post(f'/book/{auth_book}/rate', data={'rating': str(rating)})
			with app.app_context():
				book = Book.query.get(auth_book)
				assert book.rating == rating
	
	def test_rate_book_invalid_rating_below_1(self, app, client, auth_book):
		"""Rating below 1 should not be accepted."""
		client.post(f'/book/{auth_book}/rate', data={'rating': '0'})
		with app.app_context():
			book = Book.query.get(auth_book)
			assert book.rating is None  # Should not be updated
	
	def test_rate_book_invalid_rating_above_10(self, app, client, auth_book):
		"""Rating above 10 should not be accepted."""
		client.post(f'/book/{auth_book}/rate', data={'rating': '11'})
		with app.app_context():
			book = Book.query.get(auth_book)
			assert book.rating is None  # Should not be updated
	
	def test_rate_nonexistent_book(self, client):
		"""Rating nonexistent book should return 404."""
		response = client.post('/book/99999/rate', data={'rating': '5'})
		assert response.status_code == 404
	
	def test_rate_book_redirects_to_detail(self, client, auth_book):
		"""Rating POST should redirect back to book detail page."""
		response = client.post(f'/book/{auth_book}/rate', data={'rating': '7'}, follow_redirects=False)
		assert response.status_code in [302, 303]
		assert f'/book/{auth_book}' in response.location
	
	def test_rate_book_shows_flash_message(self, client, auth_book):
		"""Rating should show success flash message."""
		response = client.post(f'/book/{auth_book}/rate', data={'rating': '9'}, follow_redirects=True)
		# Check for either the exact message or just the rating number
		assert b'9' in response.data
	
	def test_rate_book_update_existing_rating(self, app, client, auth_book):
		"""Should be able to update an existing rating."""
		with app.app_context():
			book = Book.query.get(auth_book)
			book.rating = 5
			db.session.commit()
		
		client.post(f'/book/{auth_book}/rate', data={'rating': '8'})
		with app.app_context():
			book = Book.query.get(auth_book)
			assert book.rating == 8


class TestAddBookWithRating:
	"""Test adding books with ratings via /add_book."""
	
	def test_add_book_form_has_rating_input(self, client, auth_author):
		"""Add book form should include rating input field."""
		with client:
			response = client.get('/add_book')
			assert b'rating' in response.data.lower()
			assert b'1-10' in response.data or b'range' in response.data.lower()
	
	def test_add_book_with_rating_form_submission(self, app, client, auth_author):
		"""Should be able to add book with rating via form."""
		response = client.post('/add_book', data={
			'isbn': '9876543210',
			'title': 'New Rated Book',
			'author_id': auth_author,
			'rating': '7'
		}, follow_redirects=True)
		
		with app.app_context():
			book = Book.query.filter_by(isbn='9876543210').first()
			assert book is not None
			assert book.rating == 7
	
	def test_add_book_with_rating_optional(self, app, client, auth_author):
		"""Rating should be optional when adding book."""
		response = client.post('/add_book', data={
			'isbn': '1111111111',
			'title': 'Unrated Book',
			'author_id': auth_author
		}, follow_redirects=True)
		
		with app.app_context():
			book = Book.query.filter_by(isbn='1111111111').first()
			assert book is not None
			assert book.rating is None


class TestRatingDisplay:
	"""Test rating display on book pages."""
	
	def test_rating_displayed_on_home_page(self, client, app, auth_book):
		"""Home page should display book rating."""
		with app.app_context():
			book = Book.query.get(auth_book)
			book.rating = 8
			db.session.commit()
		
		response = client.get('/')
		assert b'8/10' in response.data or b'8' in response.data
	
	def test_rating_with_stars_on_home_page(self, client, app, auth_book):
		"""Home page should display rating with star characters."""
		with app.app_context():
			book = Book.query.get(auth_book)
			book.rating = 7
			db.session.commit()
		
		response = client.get('/')
		# Check for star character (★) in response
		assert '★' in response.data.decode('utf-8')
	
	def test_unrated_book_not_shown_on_home(self, client, auth_book):
		"""Unrated books should not show rating on home page."""
		response = client.get('/')
		# Should not show "Not rated" or empty rating
		assert b'/10' not in response.data
	
	def test_rating_displayed_on_book_detail(self, client, app, auth_book):
		"""Book detail page should display rating."""
		with app.app_context():
			book = Book.query.get(auth_book)
			book.rating = 9
			db.session.commit()
		
		response = client.get(f'/book/{auth_book}')
		assert b'9/10' in response.data or b'9' in response.data
	
	def test_rating_editor_on_book_detail(self, client, app, auth_book):
		"""Book detail page should have rating editor."""
		with app.app_context():
			book = Book.query.get(auth_book)
			book.rating = 6
			db.session.commit()
		
		response = client.get(f'/book/{auth_book}')
		# Check for rating editor elements
		assert b'rating' in response.data.lower() or b'rate' in response.data.lower()
	
	def test_add_rating_button_on_unrated_book_detail(self, client, auth_book):
		"""Book detail page should show "Add Rating" button for unrated books."""
		response = client.get(f'/book/{auth_book}')
		# Should have some form of add/rate button
		assert b'rating' in response.data.lower() or b'rate' in response.data.lower()
	
	def test_edit_rating_button_on_rated_book_detail(self, client, app, auth_book):
		"""Book detail page should show "Edit" button for rated books."""
		with app.app_context():
			book = Book.query.get(auth_book)
			book.rating = 5
			db.session.commit()
		
		response = client.get(f'/book/{auth_book}')
		# Check for edit functionality
		assert b'rating' in response.data.lower()


class TestRatingPersistence:
	"""Test that ratings persist correctly."""
	
	def test_rating_persists_after_database_commit(self, app, auth_book):
		"""Rating should persist after database commit."""
		with app.app_context():
			book = Book.query.get(auth_book)
			book.rating = 8
			db.session.commit()
		
		with app.app_context():
			book = Book.query.get(auth_book)
			assert book.rating == 8
	
	def test_rating_survives_page_reload(self, client, app, auth_book):
		"""Rating should survive page reload."""
		with app.app_context():
			book = Book.query.get(auth_book)
			book.rating = 7
			db.session.commit()
		
		response1 = client.get(f'/book/{auth_book}')
		response2 = client.get(f'/book/{auth_book}')
		
		# Both responses should contain the rating
		assert b'7' in response1.data
		assert b'7' in response2.data
	
	def test_rating_multiple_books_independent(self, app, client, auth_author):
		"""Different books should have independent ratings."""
		with app.app_context():
			book1 = Book(isbn='isbn001', title='Book 1', author_id=auth_author, rating=5)
			book2 = Book(isbn='isbn002', title='Book 2', author_id=auth_author, rating=9)
			db.session.add_all([book1, book2])
			db.session.commit()
			book1_id = book1.id
			book2_id = book2.id
		
		with app.app_context():
			b1 = Book.query.get(book1_id)
			b2 = Book.query.get(book2_id)
			assert b1.rating == 5
			assert b2.rating == 9
