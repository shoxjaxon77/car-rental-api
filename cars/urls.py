from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarViewSet, RentViewSet, OrderViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'rents', RentViewSet, basename='rent')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'car-categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]