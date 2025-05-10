# Car Rental API

Backend REST API for a car rental mobile application built with Django REST Framework.

## Features

- User authentication and authorization
- Car listing and management
- Booking management
- Image upload support
- API documentation with Swagger/ReDoc

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env` file

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## API Documentation

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## API Endpoints

- `/api/v1/users/` - User management
- `/api/v1/cars/` - Car management and bookings
# car-rental-react
