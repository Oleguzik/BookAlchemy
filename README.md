# BookAlchemy 📚

A beginner-friendly Flask web application for managing your personal book library. Add books and authors, search your collection, and organize your reading materials with an intuitive interface.

## Features

### 📖 Core Features

- **Browse Library** - View all books in your library with sorting and filtering
- **Add Authors** - Create author profiles with birth date and death date information
- **Add Books** - Add books to your library with ISBN, title, publication year, and cover image URL
- **Search** - Search books by title, ISBN, or author name
- **Sort** - Sort books by title, author, or rating in ascending/descending order
- **Cover Images** - Display book cover images from provided URLs or Open Library service
- **Delete Books** - Remove books from your library with confirmation dialog
- **Smart Author Deletion** - When deleting an author's last book, choose whether to keep or delete the author

### ⭐ Book Ratings Features

- **Rate Books** - Add a 1-10 star rating to any book in your library
- **Quick Rating Modal** - Fast-access rating interface from the home page
- **Real-Time Star Display** - Visual star feedback as you adjust the rating slider
- **Rating Persistence** - Ratings are saved to the database and displayed consistently
- **Edit Ratings** - Change existing ratings anytime with the "Re-rate" button
- **Rating Sort** - Sort your library by book ratings (highest or lowest first)
- **Rating Display** - View ratings as filled/empty stars (★/☆) with numeric score (e.g., 7/10)
- **Rate on Home Page** - Use green "Rate" button for quick rating without leaving the list
- **Rate on Book Detail** - Use blue "Edit" or green "Add Rating" button on individual book pages

### 🤖 AI Book Recommendations (Latest Feature!)

**Powered by RapidAPI Llama (GPT-compatible) endpoint**

- **AI Review Generation** - Generate intelligent book reviews and recommendations powered by GPT
- **Per-Book Reviews** - Each book can have its own AI-generated review cached in the database
- **Smart Caching** - Reviews are stored in the database and reused (no permanent API connection needed)
- **On-Demand Refresh** - Generate new reviews or update existing ones anytime
- **Edit Reviews** - Manually modify AI-generated reviews to your preferences
- **Loading Indicator** - Visual spinner shows during API calls (60-second timeout for reliability)
- **Review Status Badge** - Green "AI Review" badge shows on books with generated reviews
- **Library Analysis** - AI analyzes your entire library to generate contextual recommendations
- **Multiple Views** - View AI reviews on home page, book detail page, or dedicated recommendation page
- **Error Handling** - User-friendly error messages if API calls timeout or fail

### 🔐 Environment Configuration (New!)

The application now uses environment variables for sensitive data:

**Create a `.env` file** in the project root with:
```bash
# API Configuration
RAPIDAPI_KEY=your-key-here
RAPIDAPI_HOST=open-ai21.p.rapidapi.com
RAPIDAPI_URL=https://open-ai21.p.rapidapi.com/conversationllama
AI_REQUEST_TIMEOUT=60

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=development
```

**Important**: The `.env` file is automatically excluded from git for security. Never commit it!

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
- **Book ratings** displayed as filled/empty stars (★/☆) with numeric score
- **AI Review badge** (green indicator when review is available)
- Sort controls for title, author, and **rating**
- Global search bar

**Actions:**
- Click "Title", "Author", or "Rating" headers to sort
- Use the search bar to find books
- Click green "Rate" button to rate a book
- Click blue "Generate Review" or "View Review" to manage AI reviews
- Click "Delete" button to remove a book from your library

### 🤖 Generate AI Book Reviews

**From Home Page:**
1. Look for books without a blue "View Review" button
2. Click the blue **"Generate Review"** button
3. A loading spinner appears while fetching the review
4. Once complete, click **"View Review"** to see the AI-generated text

**From Book Detail Page:**
1. Scroll to the "AI Review" section
2. If no review exists, click green **"Generate"** button
3. A loading modal appears with a spinner
4. Once generated, you can:
   - Click **"View"** to see the full review on the recommendations page
   - Click **"Edit"** to modify the review
   - Click **"Refresh"** to generate a new review

**From Recommendations Page:**
1. Click **"Suggest a Book to Read"** from home page actions
2. View all your books with their cached AI reviews
3. For each book, you can:
   - Click **"Edit"** to manually modify the review
   - Click **"Refresh"** to generate a new review
4. The page shows library statistics and analysis

### 📝 Edit AI Reviews

You can manually edit any AI-generated review:

1. Navigate to the book (home, detail, or recommendations page)
2. Click the orange **"Edit"** button (on recommendations page) or blue **"Edit"** (on detail page)
3. A modal opens showing the current review text
4. Edit the text as desired (supports any text format)
5. Click **"Save Changes"** to update the review
6. Click outside the modal or **"Cancel"** to discard changes

**Note**: Edited reviews are saved to the database and persist across sessions.

### 🔄 Refresh AI Reviews

To generate a new review and replace the old one:

1. Click the blue **"Refresh"** button (on detail page) or green **"Refresh"** (on recommendations page)
2. A new API call is made to generate fresh review content
3. The old review is replaced with the new one
4. If you want to keep the old review, use **"Edit"** instead

### ⚙️ AI Recommendation Settings

**API Configuration:**
The application connects to RapidAPI's Llama endpoint (GPT-compatible):
- Endpoint: `https://open-ai21.p.rapidapi.com/conversationllama`
- Timeout: 60 seconds (increased from default for reliability)
- Free tier: 50 requests per month

**Customizing AI Behavior:**
To modify how the AI generates reviews, edit the prompt in `app.py`:

```python
# Around line 180 in app.py
prompt = f"""
Analyze this book and provide a detailed review:
...
"""
```

**API Rate Limiting:**
- Free tier: 50 requests per month
- If you exceed limits, consider upgrading your RapidAPI plan
- Alternative AI providers: OpenAI, Anthropic, Cohere

### ⭐ Rate a Book - From Home Page

Click the green **"Rate"** or orange **"Re-rate"** button to quickly rate a book:

1. A modal dialog appears with a rating slider
2. Move the slider from 1-10 to set your rating
3. See the stars update in real-time (filled ★ for your rating, empty ☆ for remaining)
4. Click "Save Rating" to store your rating
5. Click "Cancel" or outside the modal to close without saving

**Rating Display:**
- Unrated books show: *"Not rated"* (gray text)
- Rated books show: `★★★★★☆☆☆☆☆ 5/10` format

### ⭐ Rate a Book - From Book Detail Page

On any book's detail page, you can add or edit a rating:

1. Click blue **"Edit"** button (if already rated) or green **"Add Rating"** button (if not yet rated)
2. The rating modal opens with a slider
3. Adjust the slider to your desired rating (1-10)
4. Stars and numeric display update as you move the slider
5. Click "Save Rating" to confirm your rating

**Rating Information:**
- Ratings persist across the application
- You can change a rating anytime by clicking the "Edit" button
- Rating changes are immediate and saved to the database

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
rating (Integer, Optional, Range: 1-10)
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

### Environment Variables

The application uses a `.env` file for configuration. Create one in the project root:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URI=sqlite:///data/library.sqlite

# RapidAPI Configuration (for AI recommendations)
RAPIDAPI_KEY=your-key-here
RAPIDAPI_HOST=open-ai21.p.rapidapi.com
RAPIDAPI_URL=https://open-ai21.p.rapidapi.com/conversationllama
AI_REQUEST_TIMEOUT=60
```

### Setting Up AI Recommendations

To enable AI book recommendations:

1. **Create a RapidAPI Account**:
   - Visit https://rapidapi.com
   - Sign up for free account
   - Navigate to: https://rapidapi.com/2Stallions/api/open-ai21
   - Subscribe to the free tier

2. **Get Your API Key**:
   - After subscribing, find "API Key" in your profile
   - Copy your key to the `.env` file as `RAPIDAPI_KEY`

3. **Test the Connection**:
   ```bash
   python -c "
   import os
   from dotenv import load_dotenv
   load_dotenv()
   import requests
   headers = {
       'x-rapidapi-key': os.getenv('RAPIDAPI_KEY'),
       'x-rapidapi-host': os.getenv('RAPIDAPI_HOST'),
       'Content-Type': 'application/json'
   }
   payload = {'messages': [{'role': 'user', 'content': 'Say hello'}], 'web_access': False}
   response = requests.post(os.getenv('RAPIDAPI_URL'), json=payload, headers=headers, timeout=60)
   print('Status:', response.status_code)
   "
   ```

4. **Generate Your First Review**:
   - Add a book to your library
   - Click "Generate Review" button
   - Wait for the AI to analyze and generate a review

### Database URI

The app uses SQLite by default. To change the database, modify `.env`:

```python
# For SQLite (default)
DATABASE_URI=sqlite:///data/library.sqlite

# For PostgreSQL (example)
DATABASE_URI=postgresql://user:password@localhost/bookalchemy

# For MySQL (example)
DATABASE_URI=mysql+pymysql://user:password@localhost/bookalchemy
```

### Flask Secret Key

For production, set a strong secret key:

```bash
# Generate a random secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to .env
FLASK_SECRET_KEY=your-generated-key-here
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

### AI Review Generation Issues

**"Error connecting to AI service: Connection refused"**
- Check your internet connection
- Verify `RAPIDAPI_KEY` is correctly set in `.env`
- Ensure you've subscribed to the API on RapidAPI

**"Request timed out" error**
- The API is taking longer than 60 seconds
- This is normal for the free tier
- Try again in a few moments
- Consider upgrading your RapidAPI plan

**"No recommendation generated"**
- The API returned an empty result
- Try refreshing the review
- Check your RapidAPI monthly request limit (50 for free tier)
- If limit reached, wait for next month or upgrade plan

**Reviews show different content each time**
- This is expected! The AI generates fresh reviews on each call
- To keep specific text, use the **"Edit"** button to manually save your preferred version

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
- `POST /book/<id>/rate` - Submit book rating (1-10)
- `POST /book/<id>/delete` - Delete book (with author check)
- `POST /author/<id>/delete` - Delete author and all their books (cascade deletion)
- `GET /book/<id>/confirm_delete` - Delete confirmation page
- `POST /book/<id>/confirm_delete` - Confirm book deletion
- `POST /book/<id>/ai_review` - Generate AI recommendation (NEW!)
- `POST /book/<id>/edit_review` - Edit AI recommendation (NEW!)
- `GET /recommend` - View all cached AI reviews (NEW!)

### AI-Specific Routes (New!)
- `POST /book/<id>/ai_review` - Fetch AI recommendation from RapidAPI
  - Returns: Flash message with status
  - Redirect: Back to referring page
  - Timeout: 60 seconds
  - Caches result in database

- `POST /book/<id>/edit_review` - Manually edit cached AI recommendation
  - Accepts: `ai_recommendation` (textarea)
  - Saves directly to database

- `GET /recommend` - Display all books with their cached AI reviews
  - Shows: Book grid with individual reviews
  - Actions: Edit, Refresh, View each review
  - Analysis: Library statistics and ratings

### Admin Routes
- `GET /admin` - Admin test interface
- `POST /admin/delete_author/<id>` - Admin delete author
- `POST /admin/delete_book/<id>` - Admin delete book

## AI Recommendations API Integration

### RapidAPI Configuration

**Provider**: RapidAPI Llama Endpoint (GPT-compatible)
- **Base URL**: `https://open-ai21.p.rapidapi.com/conversationllama`
- **Authentication**: API key in `x-rapidapi-key` header
- **Timeout**: 60 seconds (configurable)
- **Rate Limit**: 50 requests/month (free tier)

### Request Format

```python
headers = {
    "x-rapidapi-key": "your-api-key",
    "x-rapidapi-host": "open-ai21.p.rapidapi.com",
    "Content-Type": "application/json"
}

payload = {
    "messages": [
        {
            "role": "user",
            "content": "Your prompt here"
        }
    ],
    "web_access": False
}

response = requests.post(url, json=payload, headers=headers, timeout=60)
```

### Response Format

Successful response (200 OK):
```json
{
  "result": {
    "message": "Generated recommendation text...",
    "conversations": [...]
  }
}
```

### Error Handling

The application handles:
- **Timeout errors** (>60 seconds): User-friendly message about free tier
- **Connection errors**: Message to check internet and API key
- **Empty responses**: Fallback message
- **Invalid API key**: Connection refused error

All errors are logged and users see helpful messages.

### Caching Strategy

Reviews are cached in the database (`Book.ai_recommendation` field):
- Generated once per book, reused until "Refresh" is clicked
- Editing a review saves the custom text to database
- No permanent API connection needed after generation
- Database stores complete recommendation text

### Monthly Request Limits

**Free Tier:**
- 50 requests per month
- Counter resets on 1st of each month
- Check RapidAPI dashboard for current usage

**If You Exceed Limits:**
1. Upgrade to a paid plan on RapidAPI
2. Switch to a different AI provider (OpenAI, Anthropic, etc.)
3. Wait for the monthly reset

**Checking Usage:**
- Visit https://rapidapi.com/developer/dashboard
- Navigate to "Subscriptions"
- View current month's usage

## Frontend-Backend Communication

The application uses RESTful principles:
- **GET requests** - Retrieve and display data
- **POST requests** - Submit forms (add/delete operations, AI requests)
- **Query parameters** - Preserve state (sort, order, search)
- **Redirects** - Maintain user context after operations
- **Flash messages** - User feedback (success/error)
- **Jinja2 templating** - Dynamic HTML generation with database data
- **Form highlighting** - Search results highlight matching text
- **Loading modals** - Visual feedback during long operations

### AI Request Flow

1. User clicks "Generate Review" button
2. Frontend shows loading modal with spinner
3. Frontend sends POST request to `/book/<id>/ai_review`
4. Backend makes HTTP request to RapidAPI with 60-second timeout
5. Backend receives response and saves to database
6. Backend sends success message
7. Loading modal closes, page refreshes
8. User sees cached review on page

## Future Enhancements

Completed features (recent additions):
- ✅ Book ratings (1-10 scale) with visual star display
- ✅ AI-powered book recommendations using RapidAPI Llama
- ✅ Caching strategy for AI reviews in database
- ✅ Per-book review generation and editing
- ✅ Loading indicators for better UX
- ✅ Environment-based configuration with .env

Potential features for future expansion:
- Advanced AI providers (OpenAI GPT-4, Anthropic Claude, Cohere)
- User accounts and authentication
- Reading lists and collections
- Multi-language support
- Export/import functionality (CSV, JSON)
- Advanced filtering (by genre, publication year, rating range)
- Reading progress tracking (pages read)
- Book notes and personal annotations
- Social sharing and book club features
- Mobile app version
- Full-text search across all fields
- Email notifications for recommendations
- Batch import from external APIs (Google Books, ISBN databases)

## License

This project is for educational purposes.

## Support & Contribution

For issues or questions, please check the code comments and docstrings first. The codebase is designed to be readable and understandable for learning purposes.

---

**Happy reading! 📖✨**

