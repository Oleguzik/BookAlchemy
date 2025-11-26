#!/bin/bash

# Codio Deployment Script for BookAlchemy
# Run this script after importing the repository to Codio

echo "========================================="
echo "BookAlchemy - Codio Setup Script"
echo "========================================="

# Check Python version
echo ""
echo "1. Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "2. Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo ""
echo "3. Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "4. Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "5. Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create data directory if it doesn't exist
echo ""
echo "6. Ensuring data directory exists..."
mkdir -p data

# Ensure we're in project root
cd ~/workspace/BookAlchemy

# Initialize database
echo ""
echo "7. Initializing database..."
python3 -m backend.init_db

# Seed database (optional)
echo ""
echo "8. Seeding database with example data..."
if [ -f "data/seed_authors.py" ]; then
    python3 -m data.seed_authors
fi
if [ -f "data/seed_books.py" ]; then
    python3 -m data.seed_books
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To start the application, run:"
echo "  source .venv/bin/activate"
echo "  python run.py"
echo ""
echo "Then access your app at:"
echo "  https://[your-codio-box-url]-5002.codio.io"
echo "========================================="
