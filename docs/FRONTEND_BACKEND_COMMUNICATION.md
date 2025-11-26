# BookAlchemy: Frontend-Backend Communication Analysis

## Overview
This document provides a comprehensive analysis of how the BookAlchemy Flask application communicates between frontend (HTML/CSS) and backend (Python/SQLAlchemy). It covers all HTTP routes, request/response patterns, form submissions, template rendering, and data flow.

---

## Architecture Overview

### Technology Stack
- **Backend**: Flask 2.1+ with SQLAlchemy ORM
- **Frontend**: Jinja2 templates with HTML5 and CSS3
- **Database**: SQLite with two main tables (author, book)
- **Styling**: CSS with CSS variables and Flexbox layout
- **Icons**: Font Awesome 6.4.0 CDN

### Request Flow Pattern
```
User Input (HTML Form/Link) 
    ↓ 
HTTP Request (GET/POST)
    ↓ 
Flask Route Handler
    ↓ 
Database Query (SQLAlchemy)
    ↓ 
Template Rendering (Jinja2)
    ↓ 
HTTP Response (HTML)
    ↓ 
Browser Displays Page
```

---

## HTTP Routes & Communication Patterns

### 1. **GET / (Home Page)**

**Purpose**: Display all books with search, sort, and filter capabilities

**Request Details**:
- **HTTP Method**: GET
- **URL**: `http://localhost:5000/`
- **Query Parameters**:
  - `q` (optional): Search keyword (e.g., `?q=Python`)
  - `scope` (optional): Search scope - `books` or `authors` (default: `books`)
  - `sort` (optional): Sort field - `title` or `author` (default: `title`)
  - `order` (optional): Sort order - `asc` or `desc` (default: `asc`)

**Request Example**:
```
GET /?q=Python&sort=author&order=desc&scope=books
```

**Backend Processing**:
```python
# 1. Extract query parameters
q = request.args.get('q', '').strip()
scope = request.args.get('scope', 'books')
sort_by = request.args.get('sort', 'title')
order = request.args.get('order', 'asc')

# 2. Build SQLAlchemy query
if q and scope == 'authors':
    # Search authors by name
    author_results = Author.query.filter(Author.name.ilike(f"%{q}%")).order_by(Author.name).all()
else:
    # Search books by title, ISBN, or author name
    query = Book.query.join(Author).filter(
        or_(Book.title.ilike(f"%{q}%"), 
            Book.isbn.ilike(f"%{q}%"), 
            Author.name.ilike(f"%{q}%"))
    )

# 3. Apply sorting
if sort_by == 'author':
    query = query.join(Author).order_by(Author.name.desc() if order == 'desc' else Author.name)
else:
    query = query.order_by(Book.title.desc() if order == 'desc' else Book.title)

# 4. Fetch results
books = query.all()
```

**Response**:
- **Content-Type**: `text/html`
- **Template Used**: `home.html`
- **Template Context Variables**:
  - `books`: List of Book objects
  - `authors`: List of all Author objects
  - `sort_by`: Current sort field
  - `order`: Current sort order
  - `q`: Current search query
  - `scope`: Current search scope
  - `authors_search`: Author search results (if scope=='authors')
  - `total_authors`: Count of all authors
  - `total_books`: Count of all books
  - `no_results`: Boolean indicating if search returned no results

**Frontend Rendering**:
- Search box in header shows current `q` value
- Sort links toggle sort direction: `url_for('home', sort='title', order=('desc' if sort_by == 'title' and order == 'asc' else 'asc'), q=q)`
- Books displayed in `.book-row` cards with delete button
- Search results highlighted using Jinja filter: `{{ book.title | highlight(q) }}`
- Success messages shown if `success` query param present (e.g., `?success=book_added`)

**HTML Form in base.html**:
```html
<form class="global-search" method="GET" action="/">
  <input type="search" name="q" value="{{ q }}" />
  <input type="hidden" name="sort" value="{{ sort_by }}">
  <input type="hidden" name="order" value="{{ order }}">
  <select name="scope">
    <option value="books" {% if scope == 'books' %}selected{% endif %}>Books</option>
    <option value="authors" {% if scope == 'authors' %}selected{% endif %}>Authors</option>
  </select>
  <button title="Search"><i class="fa fa-search"></i></button>
  <a class="reset-link" href="{{ url_for('home') }}">Reset</a>
</form>
```

---

### 2. **GET/POST /add_author (Add/Edit Author)**

**Purpose**: Display author creation form and process author submissions

**GET Request**:
- **URL**: `http://localhost:5000/add_author`
- **Query Parameters** (optional):
  - `sort`: Preserved from home for back-navigation
  - `order`: Preserved from home for back-navigation
  - `q`: Preserved search query
  - `author_id`: If editing, the ID of author to edit

**POST Request**:
- **Content-Type**: `application/x-www-form-urlencoded`
- **Form Fields**:
  - `name`: Author's full name (required)
  - `birthdate`: Date in YYYY-MM-DD format (optional)
  - `date_of_death`: Date in YYYY-MM-DD format (optional)
  - `author_id`: If editing, the author's ID
  - `sort`, `order`, `q`: Preserved navigation state

**Backend Processing**:
```python
if request.method == 'POST':
    name = request.form.get('name')
    birthdate_str = request.form.get('birthdate')
    deathdate_str = request.form.get('date_of_death')
    
    # Parse dates from YYYY-MM-DD format
    birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date() if birthdate_str else None
    date_of_death = datetime.strptime(deathdate_str, '%Y-%m-%d').date() if deathdate_str else None
    
    author_id = request.form.get('author_id')
    
    if author_id:
        # UPDATE existing author
        existing = Author.query.get(int(author_id))
        existing.name = name
        existing.birth_date = birthdate
        existing.date_of_death = date_of_death
        db.session.commit()
        return redirect(url_for('home', sort=sort_by, order=order, q=q, success='author_updated'))
    else:
        # CREATE new author
        new_author = Author(name=name, birth_date=birthdate, date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()
        return redirect(url_for('home', sort=sort_by, order=order, q=q, success='author_added'))
```

**Response (GET)**:
- **Template Used**: `add_author.html`
- **Context Variables**:
  - `sort`: Sort field to preserve
  - `order`: Sort order to preserve
  - `q`: Search query to preserve
  - `author`: Author object if editing (None if creating)

**Response (POST)**:
- **Status Code**: 302 (Redirect)
- **Location Header**: `/home?sort=...&order=...&q=...&success=author_added/author_updated`
- Displays success message on home page

**HTML Form**:
```html
<form action="/add_author" method="POST">
  <input type="hidden" name="author_id" value="{{ author.id if author else '' }}" />
  <input type="hidden" name="sort" value="{{ sort }}">
  <input type="hidden" name="order" value="{{ order }}">
  <input type="hidden" name="q" value="{{ q }}">
  <label for="name">Author Name:</label> 
  <input type="text" id="name" name="name" value="{{ author.name if author else '' }}" required>
  <label for="birthdate">Birthdate:</label> 
  <input type="date" id="birthdate" name="birthdate" value="{{ author.birth_date if author and author.birth_date else '' }}">
  <label for="date_of_death">Date of Death:</label> 
  <input type="date" id="date_of_death" name="date_of_death" value="{{ author.date_of_death if author and author.date_of_death else '' }}">
  <button class="btn" type="submit">{{ 'Update Author' if author else '➕ Add Author' }} <i class="fa fa-user"></i></button>
</form>
<p><a href="{{ url_for('home', sort=sort, order=order, q=q) }}">Back to home</a></p>
```

---

### 3. **GET/POST /add_book (Add/Edit Book)**

**Purpose**: Display book creation form and process book submissions

**GET Request**:
- **URL**: `http://localhost:5000/add_book`
- **Query Parameters** (optional):
  - `sort`: Preserved from home
  - `order`: Preserved from home
  - `q`: Preserved search query
  - `book_id`: If editing, the ID of book to edit

**POST Request**:
- **Content-Type**: `application/x-www-form-urlencoded`
- **Form Fields**:
  - `isbn`: ISBN code (required)
  - `title`: Book title (required)
  - `publication_year`: Year as integer (optional)
  - `cover_url`: Image URL (optional)
  - `author_id`: Selected author ID (required, integer)
  - `sort`, `order`, `q`: Navigation state

**Backend Processing**:
```python
if request.method == 'POST':
    isbn = request.form.get('isbn')
    title = request.form.get('title')
    pub_year = request.form.get('publication_year')
    cover_url = request.form.get('cover_url')
    author_id = request.form.get('author_id')
    
    # Validate numeric fields
    pub_year = int(pub_year) if pub_year else None
    author_id = int(author_id) if author_id else None
    
    book_id = request.form.get('book_id')
    
    if book_id:
        # UPDATE existing book
        existing = Book.query.get(int(book_id))
        existing.isbn = isbn
        existing.title = title
        existing.publication_year = pub_year
        existing.cover_url = cover_url
        existing.author_id = author_id
        db.session.commit()
        return redirect(url_for('home', sort=sort_by, order=order, q=q, success='book_updated'))
    else:
        # CREATE new book
        new_book = Book(isbn=isbn, title=title, publication_year=pub_year, 
                       author_id=author_id, cover_url=cover_url)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home', sort=sort_by, order=order, q=q, success='book_added'))
```

**Response (GET)**:
- **Template Used**: `add_book.html`
- **Context Variables**:
  - `authors`: List of all Author objects (for dropdown)
  - `sort`, `order`, `q`: Navigation state
  - `book`: Book object if editing (None if creating)

**Response (POST)**:
- **Status Code**: 302 (Redirect)
- **Location**: `/home?sort=...&order=...&q=...&success=book_added/book_updated`

**HTML Form**:
```html
<form action="/add_book" method="POST">
  <input type="hidden" name="book_id" value="{{ book.id if book else '' }}" />
  <input type="hidden" name="sort" value="{{ sort }}">
  <input type="hidden" name="order" value="{{ order }}">
  <input type="hidden" name="q" value="{{ q }}">
  
  <label for="isbn">ISBN:</label>
  <input type="text" id="isbn" name="isbn" value="{{ book.isbn if book else '' }}" required>
  
  <label for="title">Title:</label>
  <input type="text" id="title" name="title" value="{{ book.title if book else '' }}" required>
  
  <label for="publication_year">Publication Year:</label>
  <input type="number" id="publication_year" name="publication_year" value="{{ book.publication_year if book and book.publication_year else '' }}">
  
  <label for="cover_url">Cover URL (optional):</label>
  <input type="url" id="cover_url" name="cover_url" value="{{ book.cover_url if book else '' }}" placeholder="https://example.com/cover.jpg">
  
  <label for="author_id">Author:</label>
  <select id="author_id" name="author_id" required>
    <option value="">Select an author</option>
    {% for a in authors %}
    <option value="{{ a.id }}" {% if book and book.author_id == a.id %}selected{% endif %}>{{ a.name }}</option>
    {% endfor %}
  </select>
  
  <button class="btn" type="submit">{{ 'Update Book' if book else '➕ Add Book' }} <i class="fa fa-book"></i></button>
</form>
```

---

### 4. **GET /admin (Admin Test Page)**

**Purpose**: Display admin interface with all authors and books for testing

**Request**:
- **HTTP Method**: GET
- **URL**: `http://localhost:5000/admin`

**Backend Processing**:
```python
authors = Author.query.order_by(Author.name).all()
books = Book.query.order_by(Book.title).all()
```

**Response**:
- **Template Used**: `test_ui.html`
- **Context Variables**:
  - `authors`: All authors sorted by name
  - `books`: All books sorted by title

---

### 5. **POST /admin/delete_author/<int:author_id> (Admin Delete Author)**

**Purpose**: Delete an author and all associated books (admin function)

**Request**:
- **HTTP Method**: POST
- **URL**: `http://localhost:5000/admin/delete_author/1`
- **Form Data**: None required (just a confirmation form submission)

**Backend Processing**:
```python
author = Author.query.get_or_404(author_id)
# Delete all books by this author first
Book.query.filter_by(author_id=author_id).delete()
# Delete the author
db.session.delete(author)
db.session.commit()
flash('Author deleted', 'success')
```

**Response**:
- **Status Code**: 302 (Redirect)
- **Location**: `/admin`
- Flash message displayed on admin page

---

### 6. **POST /admin/delete_book/<int:book_id> (Admin Delete Book)**

**Purpose**: Delete a specific book (admin function)

**Request**:
- **HTTP Method**: POST
- **URL**: `http://localhost:5000/admin/delete_book/1`

**Backend Processing**:
```python
book = Book.query.get_or_404(book_id)
db.session.delete(book)
db.session.commit()
flash('Book deleted', 'success')
```

**Response**:
- **Status Code**: 302 (Redirect)
- **Location**: `/admin`

---

### 7. **POST /book/<int:book_id>/delete (Delete Book with Author Check)**

**Purpose**: Initiate book deletion with smart author detection

**Request**:
- **HTTP Method**: POST
- **URL**: `http://localhost:5000/book/1/delete`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Form Data**: None required

**Backend Processing**:
```python
book = Book.query.get_or_404(book_id)
author_id = book.author_id

# Check if this is the author's last book
remaining_books = Book.query.filter_by(author_id=author_id).count()

if remaining_books == 1:
    # This is the last book - ask user about deleting author too
    return redirect(url_for('confirm_delete_book', book_id=book_id))
else:
    # Not the last book - safe to delete immediately
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully.', 'success')
    return redirect(url_for('home'))
```

**Response**:
- **If not last book**: 302 redirect to home with success message
- **If last book**: 302 redirect to confirmation page at `/book/{book_id}/confirm_delete`

**HTML Form (in home.html)**:
```html
<form method="POST" action="{{ url_for('delete_book', book_id=book.id) }}" 
      style="display:inline;" onsubmit="return confirm('Are you sure you want to delete this book?');">
  <button type="submit" class="btn btn-danger">
    <i class="fa fa-trash"></i> Delete
  </button>
</form>
```

---

### 8. **GET/POST /book/<int:book_id>/confirm_delete (Delete Confirmation)**

**Purpose**: Show confirmation dialog for deleting a book when it's the author's last book

**GET Request**:
- **URL**: `http://localhost:5000/book/1/confirm_delete`
- **Purpose**: Display confirmation form

**Backend Processing (GET)**:
```python
book = Book.query.get_or_404(book_id)
author = book.author
```

**Response (GET)**:
- **Template Used**: `confirm_delete_book.html`
- **Context Variables**:
  - `book`: The book object
  - `author`: The associated author object

**POST Request**:
- **Content-Type**: `application/x-www-form-urlencoded`
- **Form Data**:
  - `delete_author`: Either `yes` or `no`

**Backend Processing (POST)**:
```python
book = Book.query.get_or_404(book_id)
author = book.author
delete_author = request.form.get('delete_author') == 'yes'

# Delete the book
db.session.delete(book)
db.session.commit()

# Conditionally delete author
if delete_author and author:
    db.session.delete(author)
    db.session.commit()
    flash('Book and author deleted successfully.', 'success')
else:
    flash('Book deleted successfully. Author kept in database.', 'success')

return redirect(url_for('home'))
```

**Response (POST)**:
- **Status Code**: 302 (Redirect)
- **Location**: `/`
- Flash message indicating deletion result

**HTML Form**:
```html
<form method="POST">
  <div>
    <input type="radio" name="delete_author" value="no" id="keep_author" checked>
    <label for="keep_author">Keep the author in the database</label>
  </div>
  
  <div>
    <input type="radio" name="delete_author" value="yes" id="delete_author">
    <label for="delete_author">Delete the author too</label>
  </div>
  
  <button type="submit" class="btn">Delete Book</button>
  <a href="{{ url_for('home') }}" class="btn">Cancel</a>
</form>
```

---

## Data Models & Database Schema

### Author Model
```python
class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)
    books = db.relationship('Book', backref='author', lazy='dynamic')
```

**Relationships**:
- One Author can have many Books
- Books reference Author via `author_id` foreign key
- Template access: `{{ book.author.name }}` or `{{ author.books }}`

### Book Model
```python
class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20))
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer)
    cover_url = db.Column(db.String(512))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
```

---

## Search & Highlight Mechanism

### Search Functionality
The application uses **case-insensitive partial matching** via SQLAlchemy:

```python
# Search across multiple fields
query = Book.query.join(Author).filter(
    or_(
        Book.title.ilike(f"%{q}%"),      # Partial title match
        Book.isbn.ilike(f"%{q}%"),       # Partial ISBN match
        Author.name.ilike(f"%{q}%")      # Partial author name match
    )
)
```

### Highlight Filter (Jinja2)
Matched search terms are highlighted in results using a custom Jinja filter:

```python
def highlight(text, q):
    """Highlight matching text in regex-safe way"""
    if not q or not text:
        return text
    try:
        pat = re.compile(re.escape(q), re.IGNORECASE)
        esc = escape
        return Markup(pat.sub(
            lambda m: f"<mark class=\"match\">{esc(m.group(0))}</mark>", 
            esc(text)
        ))
    except Exception:
        return text
```

**Usage in Templates**:
```html
{{ book.title | highlight(q) }}
{{ book.author.name | highlight(q) }}
```

**CSS for highlighted matches**:
```css
mark.match {
  background-color: #fff59d;
  font-weight: bold;
  padding: 0 2px;
}
```

---

## Sorting Mechanism

### Sort Parameters
- **sort_by**: `title` (default) or `author`
- **order**: `asc` (default) or `desc`

### Implementation
```python
if sort_by == 'author':
    query = query.join(Author)
    query = query.order_by(Author.name.desc() if order == 'desc' else Author.name)
else:
    query = query.order_by(Book.title.desc() if order == 'desc' else Book.title)
```

### Toggle Sort Links
```html
<!-- Clicking toggles sort direction if already sorting by this field -->
<a href="{{ url_for('home', sort='title', order=('desc' if sort_by == 'title' and order == 'asc' else 'asc'), q=q) }}">
  Title {% if sort_by == 'title' %}
    {% if order=='asc' %}<i class="fa fa-arrow-up"></i>{% else %}<i class="fa fa-arrow-down"></i>{% endif %}
  {% endif %}
</a>
```

---

## Navigation State Preservation

### Problem
When users navigate between pages (home → add_book → home), the sorting, order, and search query parameters could be lost.

### Solution
All navigation links and forms include hidden fields to preserve state:

```html
<!-- Hidden fields in add_book.html form -->
<input type="hidden" name="sort" value="{{ sort }}">
<input type="hidden" name="order" value="{{ order }}">
<input type="hidden" name="q" value="{{ q }}">
```

### URL Construction
All redirects preserve parameters:
```python
return redirect(url_for('home', sort=sort_by, order=order, q=q, success='book_added'))
```

---

## Flash Messages

### Implementation
Flask's built-in flash message system shows temporary notifications:

```python
flash('Book deleted successfully.', 'success')
return redirect(url_for('home'))
```

### Display in Template
```html
{% if request.args.get('success') %}
  <p style="color:green; margin:8px 0;">
    {% if request.args.get('success') == 'author_added' %}
      Author added successfully.
    {% elif request.args.get('success') == 'book_added' %}
      Book added successfully.
    {% else %}
      Operation completed successfully.
    {% endif %}
  </p>
{% endif %}
```

---

## Form Security & Validation

### CSRF Protection
- **Method**: POST forms include all necessary state in hidden fields
- **No explicit CSRF token** (development setup - should add in production)

### Input Validation
1. **Required Fields**: HTML `required` attribute + server-side check
2. **Date Parsing**: `datetime.strptime(s, '%Y-%m-%d')` with error handling
3. **Integer Parsing**: `int()` with try/except for numeric fields
4. **URL Validation**: HTML `type="url"` for cover image URLs

### Server-Side Safety
```python
try:
    pub_year = int(pub_year) if pub_year else None
    author_id = int(author_id) if author_id else None
except ValueError:
    pub_year = None
    author_id = None
```

---

## Error Handling

### Database Check
```python
@app.before_request
def ensure_db_schema():
    ok, missing = check_db_tables()
    if not ok:
        return render_template('error_db_missing.html', missing=missing), 503
```

### 404 Errors
```python
book = Book.query.get_or_404(book_id)  # Returns 404 if not found
```

### Template
```html
<!-- error_db_missing.html shows which tables are missing -->
<p>Missing tables: {{ missing|join(', ') }}</p>
```

---

## CSS Styling & Frontend Architecture

### Layout Structure
```
┌─────────────────────────────────────┐
│         Header (Site Header)        │  40px
│  BookAlchemy | [Search Form]        │
├──────────────────────────────────────┤
│ Main Content (Flexbox Layout)       │
│  ┌──────────────┬──────────────┐   │
│  │  Main Col    │  Sidebar     │   │
│  │  (70-80%)    │  (20-30%)    │   │
│  │              │              │   │
│  │  Book Cards  │  Action      │   │
│  │              │  Links       │   │
│  └──────────────┴──────────────┘   │
├──────────────────────────────────────┤
│           Footer                    │  40px
└──────────────────────────────────────┘
```

### CSS Variables (for beginner readability)
```css
:root {
  --primary-color: #2196F3;
  --danger-color: #d9534f;
  --success-color: #5cb85c;
  --text-color: #333;
  --bg-light: #f5f5f5;
  --border-color: #ddd;
  --border-radius: 4px;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

### Key Classes
- `.layout`: Main flexbox container
- `.main-col`: Primary content area (70-80% width)
- `.side-col`: Sidebar area (20-30% width)
- `.book-row`: Individual book display with flexbox
- `.card`: Bordered content container
- `.btn`: Button styling with hover effects
- `.btn-danger`: Red danger button for delete operations
- `.global-search`: Header search form styling

---

## Request/Response Cycle Example

### Complete Example: Adding a Book

**1. User navigates to `/add_book`**
```
GET /add_book?sort=author&order=desc&q=python
```

**2. Flask processes request**
```python
# Route handler
authors = Author.query.order_by(Author.name).all()
return render_template('add_book.html', authors=authors, sort=sort_by, order=order, q=q, book=None)
```

**3. Template renders form**
```html
<form action="/add_book" method="POST">
  <input type="hidden" name="sort" value="author">
  <input type="hidden" name="order" value="desc">
  <input type="hidden" name="q" value="python">
  <!-- form fields -->
  <button type="submit">Add Book</button>
</form>
```

**4. User fills form and clicks submit**
```
POST /add_book
Content-Type: application/x-www-form-urlencoded

isbn=978-0-13-110362-7&title=The+C+Programming+Language&publication_year=1988&author_id=5&sort=author&order=desc&q=python
```

**5. Flask processes POST request**
```python
# Extract form data
isbn = '978-0-13-110362-7'
title = 'The C Programming Language'
pub_year = 1988
author_id = 5

# Create database record
new_book = Book(isbn=isbn, title=title, publication_year=pub_year, author_id=5)
db.session.add(new_book)
db.session.commit()

# Redirect preserving state
return redirect(url_for('home', sort='author', order='desc', q='python', success='book_added'))
```

**6. Browser receives redirect response**
```
HTTP/1.1 302 Found
Location: /?sort=author&order=desc&q=python&success=book_added
```

**7. Browser fetches new page**
```
GET /?sort=author&order=desc&q=python&success=book_added
```

**8. Flask processes GET request**
```python
# Build query with sorting and searching
query = Book.query.join(Author).filter(
    or_(Book.title.ilike('%python%'), ...)
).order_by(Author.name.desc())

books = query.all()
```

**9. Flask renders home.html**
- Success message: "Book added successfully."
- Books sorted by author descending
- Search highlights "python" text
- Previous search/sort state preserved in links

---

## HTTP Status Codes Used

| Status | Context | Meaning |
|--------|---------|---------|
| 200 | GET requests | Success - page displayed |
| 302 | POST requests | Redirect after form submission |
| 404 | Invalid ID | Book/author not found (get_or_404) |
| 503 | DB check fails | Database schema missing |

---

## Summary: Frontend-Backend Communication Flow

1. **User Input** → HTML form or clickable link
2. **HTTP Request** → GET query params or POST form data
3. **Route Handler** → Extract params, build SQLAlchemy queries
4. **Database Query** → Filter, sort, join with relationships
5. **Response** → Either render template (GET) or redirect (POST)
6. **Template Rendering** → Pass context variables, apply Jinja filters
7. **HTML Output** → Browser receives rendered page
8. **Display** → CSS styling applied, JavaScript interactions ready

This architecture ensures:
- ✅ State preservation across navigation
- ✅ Smart UX (confirm deletion of last book)
- ✅ Search highlighting with case-insensitive matching
- ✅ Flexible sorting by title or author
- ✅ Clean separation of concerns (routes, models, templates)
- ✅ Database safety (proper ORM queries, type validation)

