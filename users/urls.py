from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Registration
    # POST: Register a new user
    # Request: {
    #   "username": "user1",
    #   "password": "strong_pass",
    #   "password2": "strong_pass",
    #   "email": "user@example.com",
    #   "first_name": "John",
    #   "last_name": "Doe",
    #   "phone_number": "+998901234567"
    # }
    path('api/v1/register/', views.UserRegisterView.as_view(), name='register'),

    # Profile
    # GET: Get user profile
    # PUT/PATCH: Update user profile
    # Request: {
    #   "first_name": "John",
    #   "last_name": "Doe",
    #   "phone_number": "+998901234567",
    #   "old_password": "old_pass",  # Optional
    #   "new_password": "new_pass"   # Required if old_password is provided
    # }
    path('api/v1/profile/', views.UserProfileView.as_view(), name='profile'),

    # Current User
    # GET: Get current authenticated user info
    path('api/v1/me/', views.current_user, name='current-user'),

    # Authentication
    # POST: Get JWT tokens
    # Request: {"username": "user1", "password": "pass"}
    # Response: {"access": "token", "refresh": "token"}
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # POST: Refresh JWT token
    # Request: {"refresh": "token"}
    # Response: {"access": "new_token"}
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
