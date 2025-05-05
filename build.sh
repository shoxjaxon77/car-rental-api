#!/usr/bin/env bash
# exit on error
set -o errexit

# Create static directory if it doesn't exist
mkdir -p static

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Start the application
gunicorn config.wsgi:application
