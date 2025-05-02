# Car Rental API

Django REST framework based API for car rental service.

## Features

- User authentication with JWT
- Car management
- Rental requests with payment image upload
- Order management
- Admin approval system

## API Documentation

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Local Development

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file from `.env.example`
6. Run migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Run server: `python manage.py runserver`

## Deployment

### Heroku

1. Create Heroku app
2. Add PostgreSQL addon
3. Configure environment variables in Heroku dashboard
4. Connect GitHub repository
5. Deploy main branch

### Required Environment Variables

```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-database-url

# AWS S3 for media files
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=your-region

# CORS settings
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## API Endpoints

### Authentication
- `POST /api/users/register/` - Register new user
- `POST /api/users/token/` - Get JWT token
- `POST /api/users/token/refresh/` - Refresh JWT token

### Cars
- `GET /api/cars/` - List all cars
- `POST /api/cars/` - Add new car (admin only)
- `GET /api/cars/{id}/` - Get car details
- `PUT /api/cars/{id}/` - Update car (admin only)
- `DELETE /api/cars/{id}/` - Delete car (admin only)

### Rentals
- `GET /api/rents/` - List user's rental requests
- `POST /api/rents/` - Create rental request
- `GET /api/rents/{id}/` - Get request details
- `POST /api/rents/{id}/add_payment/` - Add payment image

### Orders
- `GET /api/orders/` - List orders
- `POST /api/orders/{id}/approve_rent/` - Approve rental request (admin only)

This is a RESTful API for a car rental service built with Django Rest Framework.

## Features

- Car management (CRUD operations)
- Booking management
- User authentication and authorization
- Image upload for cars
- Filtering and searching capabilities

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run server:
```bash
python manage.py runserver
```

## API Documentation

API documentation will be available at `/swagger/` or `/redoc/` after running the server.
# car-rental-api
# car-rental-api
