from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarViewSet, RentViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'bookings', RentViewSet, basename='booking')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
