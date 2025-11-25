
from flask import Flask, render_template, request, redirect, url_for
import os

from data_models import db, Author, Book
from datetime import datetime


# Create Flask application instance
app = Flask(__name__)

# Use an absolute path for the SQLite file to avoid path issues with Flask
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
# Turn off the extra event system to keep things simple and avoid a warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# If `db` was provided by data_models, initialize it with the Flask app
if db is not None:
	db.init_app(app)


@app.route('/')
def home():
	# Query all books and pass to the template. The Book model includes a
	# relationship to Author so we can access book.author.name directly.
	# Allow sorting through query parameters: sort=title|author and order=asc|desc
	sort_by = request.args.get('sort', 'title')
	order = request.args.get('order', 'asc')

	if sort_by == 'author':
		# join Author and order by author's name
		if order == 'desc':
			books = Book.query.join(Author).order_by(Author.name.desc()).all()
		else:
			books = Book.query.join(Author).order_by(Author.name).all()
	else:
		# default to ordering by title
		if order == 'desc':
			books = Book.query.order_by(Book.title.desc()).all()
		else:
			books = Book.query.order_by(Book.title).all()
	# Also query authors for display
	authors = Author.query.order_by(Author.name).all()
	return render_template('home.html', books=books, authors=authors, sort_by=sort_by, order=order)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
	# Preserve current sorting when navigating from home
	sort_by = request.args.get('sort', request.form.get('sort')) or 'title'
	order = request.args.get('order', request.form.get('order')) or 'asc'

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

		new_author = Author(name=name, birth_date=birthdate, date_of_death=date_of_death)
		db.session.add(new_author)
		db.session.commit()
		# Redirect to home, preserving sort/order and showing a success flag
		return redirect(url_for('home', sort=sort_by, order=order, success='author_added'))

	# On GET, render add form. Pass sorting for sticky params.
	return render_template('add_author.html', sort=sort_by, order=order)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
	# Provide list of authors for the dropdown and keep any sorting state
	sort_by = request.args.get('sort', request.form.get('sort')) or 'title'
	order = request.args.get('order', request.form.get('order')) or 'asc'
	message = None
	authors = Author.query.order_by(Author.name).all()
	if request.method == 'POST':
		isbn = request.form.get('isbn')
		title = request.form.get('title')
		pub_year = request.form.get('publication_year')
		author_id = request.form.get('author_id')

		try:
			pub_year = int(pub_year) if pub_year else None
			author_id = int(author_id) if author_id else None
		except ValueError:
			pub_year = None
			author_id = None

		new_book = Book(isbn=isbn, title=title, publication_year=pub_year, author_id=author_id)
		db.session.add(new_book)
		db.session.commit()
		return redirect(url_for('home', sort=sort_by, order=order, success='book_added'))

	return render_template('add_book.html', authors=authors, sort=sort_by, order=order)


if __name__ == '__main__':
	app.run(debug=True)
