#!/usr/bin/env bash
# exit on error
set -o errexit

# Create necessary directories
mkdir -p static
mkdir -p media
mkdir -p staticfiles

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser if not exists
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
END

# Collect static files
python manage.py collectstatic --no-input

# Start the application
gunicorn config.wsgi:application
