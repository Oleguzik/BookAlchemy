
import re
from sqlalchemy import or_, inspect
from datetime import datetime
from backend.data_models import db, Author, Book
from flask import Flask, render_template, request, redirect, url_for, flash
from markupsafe import Markup, escape
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from flask_migrate import Migrate
except Exception:
    Migrate = None


# Jinja filter to highlight keyword matches in results
def highlight(text, q):
    if not q or not text:
        return text
    # escape q for regex and do case-insensitive replacement, wrap in <mark>
    try:
        pat = re.compile(re.escape(q), re.IGNORECASE)
        esc = escape
        return Markup(
            pat.sub(
                lambda m: f"<mark class=\"match\">{esc(m.group(0))}</mark>",
                esc(text)))
    except Exception:
        return text


def check_db_tables(required_tables=None):
    """Return (ok, missing) where ok is True if every required
    table is present.

    This function uses SQLAlchemy's inspector to check the
    presence of the tables.
    """
    if required_tables is None:
        required_tables = ['author', 'book']
    try:
        inspector = inspect(db.engine)
        missing = [t for t in required_tables if not inspector.has_table(t)]
        return (len(missing) == 0, missing)
    except Exception as exc:
        # If the DB engine can't be connected, report the error message as
        # missing info
        return (False, [str(exc)])


def create_app(config_overrides=None):
    # Create Flask application instance
    # Point to frontend directory for templates and static files
    import os
    basedir = os.path.abspath(os.path.dirname(__file__))
    frontend_dir = os.path.join(os.path.dirname(basedir), 'frontend')
    app = Flask(__name__,
                template_folder=os.path.join(frontend_dir, 'templates'),
                static_folder=os.path.join(frontend_dir, 'static'))

    # For flash messages in dev, set a simple secret key (change for
    # production!).
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret')

    # Use an absolute path for the SQLite file to avoid path issues with Flask
    # Database is in project root, one level up from backend/
    project_root = os.path.dirname(basedir)
    db_path = os.path.join(project_root, 'data', 'library.sqlite')
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
            app.logger.warning(
                "Flask-Migrate not installed - migrations disabled. "
                "Install Flask-Migrate or run 'bash bin/setup.sh' "
                "to enable migrations.")
        except Exception:
            # fallback to print for very early runtime
            print(
                "Warning: Flask-Migrate not installed - "
                "migrations disabled. Install Flask-Migrate or run "
                "'bash bin/setup.sh' to enable migrations.")

    app.jinja_env.filters['highlight'] = highlight

    @app.before_request
    def ensure_db_schema():
        ok, missing = check_db_tables()
        if not ok:
            # Show error page if tables are missing - do not auto-create to
            # prevent data loss
            return render_template(
                'error_db_missing.html', missing=missing), 503

    @app.route('/')
    def home():
        # Query all books and pass to the template. The Book model includes a
        # relationship to Author so we can access book.author.name directly.
        # Allow sorting through query parameters:
        # sort=title|author and order=asc|desc
        # Also support keyword search via `q` query param
        # (search title, isbn, author name)
        q = request.args.get('q', '').strip()
        scope = request.args.get('scope', request.args.get('scope', 'books'))
        sort_by = request.args.get('sort', 'title')
        order = request.args.get('order', 'asc')

        # Build the base query
        query = Book.query

        # If a search term is provided, filter books or authors depending on
        # scope
        if q:
            if scope == 'authors':
                # we will handle author results separately
                author_results = Author.query.filter(
                    Author.name.ilike(f"%{q}%")).order_by(
                    Author.name).all()
            else:
                # join Author so we can search against author.name as well
                query = query.join(Author).filter(or_(Book.title.ilike(
                    f"%{q}%"), Book.isbn.ilike(f"%{q}%"), Author.name.ilike(f"%{q}%")))

        # Apply ordering after filtering
        if sort_by == 'author':
            # join Author and order by author's name
            query = query.join(Author)
            if order == 'desc':
                query = query.order_by(Author.name.desc())
            else:
                query = query.order_by(Author.name)
        elif sort_by == 'rating':
            # Order by rating (nulls last for 'not rated' books)
            if order == 'desc':
                query = query.order_by(Book.rating.desc())
            else:
                query = query.order_by(Book.rating)
        else:
            # default to ordering by title
            if order == 'desc':
                query = query.order_by(Book.title.desc())
            else:
                query = query.order_by(Book.title)
        # Fetch results
        books = query.all()
        if q and scope == 'authors':
            # when searching authors only, clear books and have authors_search
            # set
            books = []
            authors_search = author_results
        else:
            authors_search = []

        # Also query authors for display (we keep authors listing but not shown
        # anymore per UI change)
        authors = Author.query.order_by(Author.name).all()
        total_books = Book.query.count()
        total_authors = Author.query.count()
        no_results = (len(books) == 0 and bool(q))
        return render_template(
            'home.html',
            books=books,
            authors=authors,
            sort_by=sort_by,
            order=order,
            q=q,
            no_results=no_results,
            scope=scope,
            authors_search=authors_search,
            total_authors=total_authors,
            total_books=total_books)

    @app.route('/add_author', methods=['GET', 'POST'])
    def add_author():
        """Add a new author to the database."""
        if request.method == 'POST':
            name = request.form.get('name')
            birth_date = request.form.get('birth_date')
            date_of_death = request.form.get('date_of_death')

            if not name:
                flash('Author name is required.', 'error')
            else:
                try:
                    from datetime import datetime
                    b_date = datetime.strptime(
                        birth_date, "%Y-%m-%d").date() if birth_date else None
                    d_date = datetime.strptime(
                        date_of_death, "%Y-%m-%d").date() if date_of_death else None

                    author = Author(
                        name=name,
                        birth_date=b_date,
                        date_of_death=d_date)
                    db.session.add(author)
                    db.session.commit()
                    flash(f'Author "{name}" added successfully!', 'success')
                    return redirect(url_for('home'))
                except Exception as e:
                    flash(f'Error adding author: {str(e)}', 'error')

        return render_template('add_author.html')

    @app.route('/book/<int:book_id>/ai_review', methods=['POST'])
    def ai_review_book(book_id):
        """Fetch AI recommendation for a book and cache it in DB."""
        book = Book.query.get_or_404(book_id)
        # Prepare prompt for AI
        prompt = (
            f"Based on the following book in my library, please "
            f"provide a detailed recommendation or analysis.\n"
            f"Book: {book.title} by "
            f"{book.author.name if book.author else 'Unknown Author'}\n"
            f"Rating: {book.rating if book.rating else 'Not rated'}\n\n"
            f"Please provide:\n"
            f"1. Book title\n"
            f"2. Author name\n"
            f"3. Why you recommend it or analysis\n"
            f"4. Genre/themes it shares with other books\n"
        )
        try:
            url = os.environ.get(
                'RAPIDAPI_URL',
                'https://open-ai21.p.rapidapi.com/conversationllama')
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "web_access": False
            }
            headers = {
                "x-rapidapi-key": os.environ.get('RAPIDAPI_KEY'),
                "x-rapidapi-host": os.environ.get('RAPIDAPI_HOST', 'open-ai21.p.rapidapi.com'),
                "Content-Type": "application/json"
            }
            timeout = int(os.environ.get('AI_REQUEST_TIMEOUT', 60))
            # Increased timeout to 60 seconds (30 was too short for some
            # requests)
            response = requests.post(
                url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            result = response.json()
            recommendation = result.get(
                'result', 'No recommendation generated')
            if isinstance(recommendation, dict):
                recommendation = recommendation.get(
                    'message', str(recommendation))
            # Save to DB
            book.ai_recommendation = recommendation
            db.session.commit()
            flash('AI recommendation fetched and saved!', 'success')
        except requests.exceptions.Timeout:
            flash(
                'AI service is taking too long to respond. '
                'Please try again in a few moments. '
                '(The free tier has limited resources)',
                'error')
        except requests.exceptions.ConnectionError as e:
            flash(
                'Connection error: Unable to reach AI service. '
                'Please check your internet connection.',
                'error')
        except requests.exceptions.RequestException as e:
            flash(f'Error connecting to AI service: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error generating recommendation: {str(e)}', 'error')
        return redirect(url_for('recommend'))

    @app.route('/book/<int:book_id>/edit_review', methods=['POST'])
    def edit_review(book_id):
        """Edit and save the AI recommendation for a book."""
        book = Book.query.get_or_404(book_id)
        ai_recommendation = request.form.get('ai_recommendation', '').strip()

        if ai_recommendation:
            book.ai_recommendation = ai_recommendation
            db.session.commit()
            flash('Review updated successfully!', 'success')
        else:
            flash('Review cannot be empty.', 'error')

        return redirect(url_for('recommend'))

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
            rating = request.form.get('rating')
            author_id = request.form.get('author_id')

            try:
                pub_year = int(pub_year) if pub_year else None
                rating = int(rating) if rating else None
                author_id = int(author_id) if author_id else None
            except ValueError:
                pub_year = None
                rating = None
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
                        existing.rating = rating
                        existing.author_id = author_id
                        db.session.commit()
                        return redirect(
                            url_for(
                                'home',
                                sort=sort_by,
                                order=order,
                                q=q,
                                success='book_updated'))
                except Exception:
                    pass
            new_book = Book(
                isbn=isbn,
                title=title,
                publication_year=pub_year,
                author_id=author_id,
                cover_url=cover_url,
                rating=rating)
            db.session.add(new_book)
            db.session.commit()
            return redirect(
                url_for(
                    'home',
                    sort=sort_by,
                    order=order,
                    q=q,
                    success='book_added'))

        # For GET, allow prefill if editing
        book_obj = None
        if book_id:
            try:
                book_obj = Book.query.get(int(book_id))
            except Exception:
                book_obj = None
        return render_template(
            'add_book.html',
            authors=authors,
            sort=sort_by,
            order=order,
            q=q,
            book=book_obj)

    @app.route('/admin')
    def admin():
        # Test page that lists authors and books with controls for edit/delete
        authors = Author.query.order_by(Author.name).all()
        books = Book.query.order_by(Book.title).all()
        return render_template('test_ui.html', authors=authors, books=books)

    @app.route('/admin/delete_author/<int:author_id>', methods=['POST'])
    def admin_delete_author(author_id):
        a = Author.query.get_or_404(author_id)
        # For safety in demo, cascade or reassign books will be blocked by FK
        # constraints; we'll delete books first
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
                flash(
                    'Book deleted successfully. Author kept in database.',
                    'success')

            return redirect(url_for('home'))

        # GET request - show confirmation page
        return render_template(
            'confirm_delete_book.html',
            book=b,
            author=author)

    @app.route('/book/<int:book_id>')
    def book_detail(book_id):
        """Display detailed information about a specific book."""
        book = Book.query.get_or_404(book_id)
        return render_template('book_detail.html', book=book)

    @app.route('/book/<int:book_id>/rate', methods=['POST'])
    def rate_book(book_id):
        """Update the rating for a book (1-10)."""
        book = Book.query.get_or_404(book_id)
        rating = request.form.get('rating')

        if rating:
            try:
                rating_val = int(rating)
                if 1 <= rating_val <= 10:
                    book.rating = rating_val
                    db.session.commit()
                    flash(
                        f'Rating updated to {rating_val}/10 for "{book.title}".',
                        'success')
                else:
                    flash('Rating must be between 1 and 10.', 'error')
            except (ValueError, TypeError):
                flash('Invalid rating value.', 'error')

        return redirect(url_for('book_detail', book_id=book_id))

    @app.route('/author/<int:author_id>')
    def author_detail(author_id):
        """Display detailed information about a specific author and all their books."""
        author = Author.query.get_or_404(author_id)
        # Get all books by this author, sorted by title
        books = Book.query.filter_by(
            author_id=author_id).order_by(
            Book.title).all()
        return render_template(
            'author_detail.html',
            author=author,
            books=books)

    @app.route('/author/<int:author_id>/delete', methods=['POST'])
    def delete_author(author_id):
        """Delete an author and all their books from the database."""
        author = Author.query.get_or_404(author_id)
        author_name = author.name

        # Delete all books by this author (cascade handles this automatically)
        Book.query.filter_by(author_id=author_id).delete()

        # Delete the author
        db.session.delete(author)
        db.session.commit()

        flash(
            f'Author "{author_name}" and all their books have been deleted successfully.',
            'success')
        return redirect(url_for('home'))

    @app.route('/recommend')
    def recommend():
        """Show cached AI recommendations for books in the user's library."""
        books = Book.query.order_by(Book.title).all()

        if not books:
            flash(
                'Add some books to your library first to get recommendations!',
                'info')
            return redirect(url_for('home'))

        # Count books with cached reviews
        books_with_reviews = [book for book in books if book.ai_recommendation]

        if not books_with_reviews:
            flash(
                'No AI recommendations cached yet. '
                'Trigger a new review for any book to fetch data.',
                'info')

        return render_template(
            'recommend.html',
            book_count=len(books),
            books=books,
            books_with_reviews_count=len(books_with_reviews))

    return app


# Create the global app instance for running the app
app = create_app()


if __name__ == '__main__':
    # Bind to 0.0.0.0 for Codio deployment (makes app accessible externally)
    app.run(host='0.0.0.0', port=5002, debug=True)
