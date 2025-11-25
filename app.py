
from flask import Flask, render_template, request, redirect, url_for, flash
from markupsafe import Markup, escape
import os

from data_models import db, Author, Book
try:
	from flask_migrate import Migrate
except Exception:
	Migrate = None
from datetime import datetime
from sqlalchemy import or_, inspect
import re


# Jinja filter to highlight keyword matches in results
def highlight(text, q):
	if not q or not text:
		return text
	# escape q for regex and do case-insensitive replacement, wrap in <mark>
	try:
		pat = re.compile(re.escape(q), re.IGNORECASE)
		esc = escape
		return Markup(pat.sub(lambda m: f"<mark class=\"match\">{esc(m.group(0))}</mark>", esc(text)))
	except Exception:
		return text


def check_db_tables(required_tables=None):
	"""Return (ok, missing) where ok is True if every required table is present.

	This function uses SQLAlchemy's inspector to check the presence of the tables.
	"""
	if required_tables is None:
		required_tables = ['author', 'book']
	try:
		inspector = inspect(db.engine)
		missing = [t for t in required_tables if not inspector.has_table(t)]
		return (len(missing) == 0, missing)
	except Exception as exc:
		# If the DB engine can't be connected, report the error message as missing info
		return (False, [str(exc)])


def create_app(config_overrides=None):
	# Create Flask application instance
	app = Flask(__name__)

	# For flash messages in dev, set a simple secret key (change for production!).
	app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret')

	# Use an absolute path for the SQLite file to avoid path issues with Flask
	basedir = os.path.abspath(os.path.dirname(__file__))
	db_path = os.path.join(basedir, 'data', 'library.sqlite')
	app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
	# Turn off the extra event system to keep things simple and avoid a warning
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

	if config_overrides:
		app.config.update(config_overrides)

	# If `db` was provided by data_models, initialize it with the Flask app
	if db is not None:
		db.init_app(app)
		# Initialize Flask-Migrate for migration support if it's available.
		if Migrate is not None:
			try:
				migrate = Migrate(app, db)
			except Exception:
				migrate = None
		else:
			migrate = None

	# Helpful runtime warning if Flask-Migrate isn't installed
	if Migrate is None:
		# Prefer app.logger where available for visibility when Flask runs
		try:
			app.logger.warning("Flask-Migrate not installed - migrations disabled. Install Flask-Migrate or run 'bash bin/setup.sh' to enable migrations.")
		except Exception:
			# fallback to print for very early runtime
			print("Warning: Flask-Migrate not installed - migrations disabled. Install Flask-Migrate or run 'bash bin/setup.sh' to enable migrations.")

	app.jinja_env.filters['highlight'] = highlight

	@app.before_request
	def ensure_db_schema():
		ok, missing = check_db_tables()
		if not ok:
			# Show error page if tables are missing - do not auto-create to prevent data loss
			return render_template('error_db_missing.html', missing=missing), 503

	@app.route('/')
	def home():
		# Query all books and pass to the template. The Book model includes a
		# relationship to Author so we can access book.author.name directly.
		# Allow sorting through query parameters: sort=title|author and order=asc|desc
		# Also support keyword search via `q` query param (search title, isbn, author name)
		q = request.args.get('q', '').strip()
		scope = request.args.get('scope', request.args.get('scope', 'books'))
		sort_by = request.args.get('sort', 'title')
		order = request.args.get('order', 'asc')

		# Build the base query
		query = Book.query

		# If a search term is provided, filter books or authors depending on scope
		if q:
			if scope == 'authors':
				# we will handle author results separately
				author_results = Author.query.filter(Author.name.ilike(f"%{q}%")).order_by(Author.name).all()
			else:
				# join Author so we can search against author.name as well
				query = query.join(Author).filter(
					or_(Book.title.ilike(f"%{q}%"), Book.isbn.ilike(f"%{q}%"), Author.name.ilike(f"%{q}%"))
				)

		# Apply ordering after filtering
		if sort_by == 'author':
			# join Author and order by author's name
			query = query.join(Author)
			if order == 'desc':
				query = query.order_by(Author.name.desc())
			else:
				query = query.order_by(Author.name)
		else:
			# default to ordering by title
			if order == 'desc':
				query = query.order_by(Book.title.desc())
			else:
				query = query.order_by(Book.title)
		# Fetch results
		books = query.all()
		if q and scope == 'authors':
			# when searching authors only, clear books and have authors_search set
			books = []
			authors_search = author_results
		else:
			authors_search = []

		# Also query authors for display (we keep authors listing but not shown anymore per UI change)
		authors = Author.query.order_by(Author.name).all()
		total_authors = Author.query.count()
		total_books = Book.query.count()
		no_results = (len(books) == 0 and bool(q))
		return render_template('home.html', books=books, authors=authors, sort_by=sort_by, order=order, q=q, no_results=no_results, scope=scope, authors_search=authors_search, total_authors=total_authors, total_books=total_books)

	@app.route('/add_author', methods=['GET', 'POST'])
	def add_author():
		# Preserve current sorting when navigating from home
		sort_by = request.args.get('sort', request.form.get('sort')) or 'title'
		order = request.args.get('order', request.form.get('order')) or 'asc'
		q = request.args.get('q', request.form.get('q')) or ''

		author_id = request.args.get('author_id') or request.form.get('author_id')
		if request.method == 'POST':
			name = request.form.get('name')
			birthdate_str = request.form.get('birthdate')
			deathdate_str = request.form.get('date_of_death')

			def parse_date(s):
				if not s:
					return None
				return datetime.strptime(s, '%Y-%m-%d').date()

			birthdate = parse_date(birthdate_str)
			date_of_death = parse_date(deathdate_str)

			if author_id:
				# Update existing
				try:
					author_id = int(author_id)
					existing = Author.query.get(author_id)
					if existing:
						existing.name = name
						existing.birth_date = birthdate
						existing.date_of_death = date_of_death
						db.session.commit()
						return redirect(url_for('home', sort=sort_by, order=order, q=q, success='author_updated'))
				except Exception:
					pass
			new_author = Author(name=name, birth_date=birthdate, date_of_death=date_of_death)
			db.session.add(new_author)
			db.session.commit()
			# Redirect to home, preserving sort/order and showing a success flag
			return redirect(url_for('home', sort=sort_by, order=order, q=q, success='author_added'))

		# On GET, render add form. If editing, pass `author` to prefill form
		author_obj = None
		if author_id:
			try:
				author_obj = Author.query.get(int(author_id))
			except Exception:
				author_obj = None
		return render_template('add_author.html', sort=sort_by, order=order, q=q, author=author_obj)

	@app.route('/add_book', methods=['GET', 'POST'])
	def add_book():
		# Provide list of authors for the dropdown and keep any sorting state
		sort_by = request.args.get('sort', request.form.get('sort')) or 'title'
		order = request.args.get('order', request.form.get('order')) or 'asc'
		q = request.args.get('q', request.form.get('q')) or ''
		message = None
		authors = Author.query.order_by(Author.name).all()
		book_id = request.args.get('book_id') or request.form.get('book_id')
		if request.method == 'POST':
			isbn = request.form.get('isbn')
			title = request.form.get('title')
			pub_year = request.form.get('publication_year')
			cover_url = request.form.get('cover_url')
			author_id = request.form.get('author_id')

			try:
				pub_year = int(pub_year) if pub_year else None
				author_id = int(author_id) if author_id else None
			except ValueError:
				pub_year = None
				author_id = None

			if book_id:
				try:
					book_id = int(book_id)
					existing = Book.query.get(book_id)
					if existing:
						existing.isbn = isbn
						existing.title = title
						existing.publication_year = pub_year
						existing.cover_url = cover_url
						existing.author_id = author_id
						db.session.commit()
						return redirect(url_for('home', sort=sort_by, order=order, q=q, success='book_updated'))
				except Exception:
					pass
			new_book = Book(isbn=isbn, title=title, publication_year=pub_year, author_id=author_id, cover_url=cover_url)
			db.session.add(new_book)
			db.session.commit()
			return redirect(url_for('home', sort=sort_by, order=order, q=q, success='book_added'))

		# For GET, allow prefill if editing
		book_obj = None
		if book_id:
			try:
				book_obj = Book.query.get(int(book_id))
			except Exception:
				book_obj = None
		return render_template('add_book.html', authors=authors, sort=sort_by, order=order, q=q, book=book_obj)

	@app.route('/admin')
	def admin():
		# Test page that lists authors and books with controls for edit/delete
		authors = Author.query.order_by(Author.name).all()
		books = Book.query.order_by(Book.title).all()
		return render_template('test_ui.html', authors=authors, books=books)

	@app.route('/admin/delete_author/<int:author_id>', methods=['POST'])
	def admin_delete_author(author_id):
		a = Author.query.get_or_404(author_id)
		# For safety in demo, cascade or reassign books will be blocked by FK constraints; we'll delete books first
		Book.query.filter_by(author_id=author_id).delete()
		db.session.delete(a)
		db.session.commit()
		flash('Author deleted', 'success')
		return redirect(url_for('admin'))

	@app.route('/admin/delete_book/<int:book_id>', methods=['POST'])
	def admin_delete_book(book_id):
		b = Book.query.get_or_404(book_id)
		db.session.delete(b)
		db.session.commit()
		flash('Book deleted', 'success')
		return redirect(url_for('admin'))

	@app.route('/book/<int:book_id>/delete', methods=['POST'])
	def delete_book(book_id):
		"""Delete a book from the database. Check if it's the author's last book."""
		b = Book.query.get_or_404(book_id)
		author_id = b.author_id
		
		# Check if this is the author's last book
		remaining_books = Book.query.filter_by(author_id=author_id).count()
		
		if remaining_books == 1:
			# This is the last book by this author
			# Ask user if they want to delete the author too
			return redirect(url_for('confirm_delete_book', book_id=book_id))
		else:
			# Not the last book, safe to delete
			db.session.delete(b)
			db.session.commit()
			flash('Book deleted successfully.', 'success')
			return redirect(url_for('home'))

	@app.route('/book/<int:book_id>/confirm_delete', methods=['GET', 'POST'])
	def confirm_delete_book(book_id):
		"""Show confirmation dialog for deleting a book when it's the author's last book."""
		b = Book.query.get_or_404(book_id)
		author = b.author
		
		if request.method == 'POST':
			delete_author = request.form.get('delete_author') == 'yes'
			
			# Delete the book
			db.session.delete(b)
			db.session.commit()
			
			# Delete author if requested
			if delete_author and author:
				db.session.delete(author)
				db.session.commit()
				flash('Book and author deleted successfully.', 'success')
			else:
				flash('Book deleted successfully. Author kept in database.', 'success')
			
			return redirect(url_for('home'))
		
		# GET request - show confirmation page
		return render_template('confirm_delete_book.html', book=b, author=author)

	return app


# Create the global app instance for running the app
app = create_app()


if __name__ == '__main__':
	app.run(debug=True)
