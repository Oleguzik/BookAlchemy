# BookAlchemy 📚

A beginner-friendly Flask web application for managing your personal book library. Add books and authors, search your collection, and organize your reading materials with an intuitive interface.

## Features

### 📖 Core Features

- **Browse Library** - View all books in your library with sorting and filtering
- **Add Authors** - Create author profiles with birth date and death date information
- **Add Books** - Add books to your library with ISBN, title, publication year, and cover image URL
- **Search** - Search books by title, ISBN, or author name
- **Sort** - Sort books by title or author in ascending/descending order
- **Cover Images** - Display book cover images from provided URLs or Open Library service
- **Delete Books** - Remove books from your library with confirmation dialog
- **Smart Author Deletion** - When deleting an author's last book, choose whether to keep or delete the author

### 🎯 Advanced Features

- **Author-Centric Organization** - View author information including number of books
- **Book-Author Relationships** - Track which author wrote each book
- **Author Stats** - See count of total authors and books in your library
- **Scope-Based Search** - Search within "Books" or "Authors" scopes
- **Smart Delete Confirmation** - Two-step confirmation when deleting an author's last book
- **Book Detail Pages** - Click any book title to view detailed information including ISBN, publication year, cover image, and author biography
- **Author Detail Pages** - Click any author name to view their profile with all books they've written, birth/death dates, and book statistics
- **Cross-Navigation** - Seamlessly navigate between book and author detail pages
- **Cascade Delete Author** - Delete an author and automatically remove all their books with a single operation
- **Protected Author Deletion** - Confirmation dialogs warn about cascade effects before deletion

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Jinja2 templates with custom CSS
- **Testing**: pytest with isolated test databases
- **Migrations**: Flask-Migrate (optional, for schema management)

## Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation & Running

```bash
# Clone or navigate to the project
cd /path/to/BookAlchemy

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Seed with example data (optional)
python data/seed_authors.py
python data/seed_books.py

# Start the development server
python app.py
```

Open your browser and navigate to: **http://127.0.0.1:5000**

### Using the Setup Script (Optional)

For convenience, use the automated setup script:

```bash
bash bin/setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Initialize the database
- Seed with example data

## Usage Guide

### 🏠 Home Page - Browse Your Library

The main page displays all books in your library with:
- Book covers (if available)
- Book title and author
- Sort controls for title and author
- Global search bar

**Actions:**
- Click "Title" or "Author" headers to sort
- Use the search bar to find books
- Click "Delete" button to remove a book from your library

### ➕ Add Author

Navigate to "Add Author" to create a new author profile.

**Fields:**
- **Name** (required) - Author's full name
- **Birth Date** (optional) - Birth date in YYYY-MM-DD format
- **Death Date** (optional) - Death date in YYYY-MM-DD format

After adding an author, you can add books by that author.

### ➕ Add Book

Navigate to "Add Book" to add a new book to your library.

**Fields:**
- **Title** (required) - Book title
- **ISBN** (required) - International Standard Book Number (must be unique)
- **Author** (required) - Select from existing authors
- **Publication Year** (optional) - Year the book was published
- **Cover URL** (optional) - Direct link to book cover image

### 📖 Book Detail Page

Click on any **book title** from the home page to view the complete book details:

**Information displayed:**
- Book cover image (if available)
- Full book metadata (ISBN, publication year, title)
- Author information with link to author profile
- List of other books by the same author
- Edit and delete options

**Navigation:**
- Click author name to view author profile
- Click other books to view their details
- "Back to Library" button to return to home

### 👤 Author Detail Page

Click on any **author name** from the home page or book detail page to view the author's profile:

**Information displayed:**
- Author name and biography (birth/death dates)
- Total number of books in library
- Grid layout of all books by this author
- Book covers and metadata for each book
- Edit and delete buttons for each book

**Navigation:**
- Click book titles to view book details
- View complete author statistics
- Add new books by this author

### 🗑️ Delete a Book

Click the red "Delete" button next to any book to remove it:

**Two scenarios:**

1. **Book is not author's last book** → Book is deleted immediately, author remains
2. **Book is author's last book** → Confirmation page appears asking:
   - **Keep author** - Delete book only, author stays in database
   - **Delete author too** - Remove both book and author permanently

### 🗑️ Delete an Author

Delete an author and **all their books** in one operation using the red "Delete Author & Books" button:

**Where to find the delete button:**
- On the **Home Page** - In the author search results section next to each author name
- On the **Author Detail Page** - Prominent red button at the bottom of the author profile

**Cascade Deletion Behavior:**
When you delete an author, the application automatically:
1. Identifies all books by that author
2. Deletes all books associated with the author
3. Removes the author from the database
4. Shows a flash message confirming deletion

**Example:**
```
Deleting "J.K. Rowling" will automatically delete:
- Harry Potter and the Philosopher's Stone
- Harry Potter and the Chamber of Secrets
- Harry Potter and the Prisoner of Azkaban
- ... and all other books by this author
```

**Confirmation Dialog:**
Before deletion, a warning dialog appears showing:
- Author name
- ⚠️  Warning symbol
- Exact count of books to be deleted
- Clear notice that the action cannot be undone

**Example warning:**
```
⚠️  DANGER: Delete "Stephen King" AND ALL 47 book(s)?

This action cannot be undone!
```

**After Deletion:**
- Success message displays: `"Author 'Author Name' and all their books have been deleted successfully."`
- Redirects automatically to the home page
- All books by that author are removed from your library

## Database Schema

### Author Table
```
id (Integer, Primary Key)
name (String, Required)
birth_date (Date, Optional)
date_of_death (Date, Optional)
```

### Book Table
```
id (Integer, Primary Key)
isbn (String, Unique, Required)
title (String, Required)
publication_year (Integer, Optional)
cover_url (String, Optional)
author_id (Integer, Foreign Key to Author)
```

## Testing

Run the test suite to verify all features work correctly:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_delete_book.py -v
pytest tests/test_delete_author.py -v

# Run with coverage
pytest tests/ --cov
```

**Test Coverage:**
- Admin UI functionality
- Delete book operations
- Delete author operations (with cascade deletion)
- Author/Book searches
- Cover image display
- Author-book relationships
- Cascade deletion integrity

## Project Structure

```
BookAlchemy/
├── app.py                    # Main Flask application
├── data_models.py            # SQLAlchemy models (Author, Book)
├── init_db.py               # Database initialization script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── static/
│   └── styles.css          # Application styling (beginner-friendly)
├── templates/
│   ├── base.html           # Base template with header/footer
│   ├── home.html           # Main library view with books/authors list
│   ├── book_detail.html    # Detailed book information page
│   ├── author_detail.html  # Author profile with all their books
│   ├── add_author.html     # Author creation form
│   ├── add_book.html       # Book creation form
│   ├── confirm_delete_book.html  # Delete confirmation page
│   └── error_db_missing.html     # Database error page
├── data/
│   ├── library.sqlite      # SQLite database file
│   ├── seed_authors.py     # Author seed data
│   └── seed_books.py       # Book seed data
└── tests/
    ├── test_admin_ui.py
    ├── test_search.py
    ├── test_delete_book.py
    └── test_delete_author.py   # New: Cascade deletion tests
```

## Configuration

### Database URI

The app uses SQLite by default. To change the database, modify `app.py`:

```python
db_path = os.path.join(basedir, 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
```

### Flask Secret Key

For production, set the `FLASK_SECRET_KEY` environment variable:

```bash
export FLASK_SECRET_KEY='your-secret-key-here'
```

## Advanced: Using Migrations

For managing database schema changes in production:

```bash
# Initialize migrations (first time only)
export FLASK_APP=app.py
flask db init

# Create a migration after model changes
flask db migrate -m "Add new column"

# Apply migration to database
flask db upgrade
```

## Troubleshooting

### "Address already in use" Port 5000

Another application is using port 5000. Either:
- Stop the other application
- Kill the process: `lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9`

### "No such column" Error

The database schema is out of sync with models. Run:

```bash
python bin/ensure_cover_column.py
```

Or reset the database:

```bash
python data/reset_db.py
```

### Tests Failing

Ensure the virtual environment is activated and all dependencies are installed:

```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

## CSS Styling

The application uses a beginner-friendly, well-commented CSS file (`static/styles.css`) that includes:

- **Color variables** - Easy theme customization
- **Flexbox layouts** - Responsive design
- **Clear sections** - Organized code structure
- **Helpful comments** - Educational for learning CSS

## Development Notes

### Test Isolation

Tests use isolated in-memory SQLite databases to prevent data loss during testing. The production database (`data/library.sqlite`) is never affected by test runs.

### Code Style

The codebase is written to be beginner-friendly with:
- Clear variable names
- Comments explaining logic
- Organized function structure
- Consistent indentation

## API Routes Reference

### Public Routes
- `GET /` - Home page with all books/authors
- `GET /book/<id>` - Book detail page
- `GET /author/<id>` - Author detail page
- `GET /add_author` - Add author form
- `GET /add_book` - Add book form
- `POST /add_author` - Submit new author
- `POST /add_book` - Submit new book
- `POST /book/<id>/delete` - Delete book (with author check)
- `POST /author/<id>/delete` - Delete author and all their books (cascade deletion)
- `GET /book/<id>/confirm_delete` - Delete confirmation page
- `POST /book/<id>/confirm_delete` - Confirm book deletion

### Admin Routes
- `GET /admin` - Admin test interface
- `POST /admin/delete_author/<id>` - Admin delete author
- `POST /admin/delete_book/<id>` - Admin delete book

## Frontend-Backend Communication

The application uses RESTful principles:
- **GET requests** - Retrieve and display data
- **POST requests** - Submit forms (add/delete operations)
- **Query parameters** - Preserve state (sort, order, search)
- **Redirects** - Maintain user context after operations
- **Jinja2 templating** - Dynamic HTML generation with database data
- **Form highlighting** - Search results highlight matching text

For detailed communication patterns, see `FRONTEND_BACKEND_COMMUNICATION.md`

## Future Enhancements

Potential features for expansion:
- User accounts and authentication
- Book ratings and reviews
- Reading lists and collections
- Book recommendations
- Export/import functionality
- Advanced filtering options
- Reading progress tracking
- Book notes and annotations

## License

This project is for educational purposes.

## Support & Contribution

For issues or questions, please check the code comments and docstrings first. The codebase is designed to be readable and understandable for learning purposes.

---

**Happy reading! 📖✨**

