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

### 🔍 Search

Use the global search bar at the top to find books or authors:
- **Default scope**: Searches by title, ISBN, and author name
- **Author scope**: Search only by author names
- Matching text is highlighted in the results

### 🗑️ Delete a Book

Click the red "Delete" button next to any book to remove it:

**Two scenarios:**

1. **Book is not author's last book** → Book is deleted immediately, author remains
2. **Book is author's last book** → Confirmation page appears asking:
   - **Keep author** - Delete book only, author stays in database
   - **Delete author too** - Remove both book and author permanently

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

# Run with coverage
pytest tests/ --cov
```

**Test Coverage:**
- Admin UI functionality
- Delete book operations
- Author/Book searches
- Cover image display
- Author-book relationships

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
│   ├── home.html           # Main library view
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
    └── test_delete_book.py
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

## Future Enhancements

Potential features for expansion:
- User accounts and authentication
- Book ratings and reviews
- Reading lists and collections
- Book recommendations
- Export/import functionality
- Advanced filtering options

## License

This project is for educational purposes.

## Support & Contribution

For issues or questions, please check the code comments and docstrings first. The codebase is designed to be readable and understandable for learning purposes.

---

**Happy reading! 📖✨**

