from django.urls import path
from . import views

app_name = 'cars'

urlpatterns = [
    # Brands (GET)
    # Response: List of all car brands
    # Example: {"id": 1, "name": "Toyota"}
    path('api/v1/brands/', views.BrandListView.as_view(), name='brand-list'),

    # Cars
    # GET: List of cars with filters
    # Filters: ?brand=1&seats=4&transmission=avtomat&min_price=100&max_price=500&available=true
    # Response: List of cars with basic info
    path('api/v1/cars/', views.CarListView.as_view(), name='car-list'),
    
    # GET: Detailed car info
    # Response: Single car with full details
    path('api/v1/cars/<int:pk>/', views.CarDetailView.as_view(), name='car-detail'),

    # Bookings
    # GET: List of user's bookings
    # Response: User's booking history with status
    path('api/v1/bookings/', views.BookingListView.as_view(), name='booking-list'),
    
    # POST: Create new booking
    # Request: {"car": 1, "start_date": "2025-05-15", "end_date": "2025-05-20"}
    # Response: {"booking_id": 1, "total_price": "1000.00"}
    path('api/v1/bookings/create/', views.BookingCreateView.as_view(), name='booking-create'),

    # Payments
    # GET: List of user's payments
    # Response: Payment history with booking details
    path('api/v1/payments/', views.PaymentListView.as_view(), name='payment-list'),
    
    # POST: Process payment
    # Request: {"booking": 1, "card_type": "visa", "card_number": "4242...", "card_expire": "12/25"}
    # Response: {"success": true, "payment_id": 1}
    path('api/v1/payments/create/', views.PaymentCreateView.as_view(), name='payment-create'),
    
    # GET: Payment details
    # Response: Full payment info with booking details
    path('api/v1/payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),

    # Contracts
    # GET: List of user's contracts
    # Response: Contract history with booking details
    path('api/v1/contracts/', views.ContractListView.as_view(), name='contract-list'),
    
    # GET: Contract details
    # Response: Full contract info with booking and payment details
    path('api/v1/contracts/<int:pk>/', views.ContractDetailView.as_view(), name='contract-detail'),
]
