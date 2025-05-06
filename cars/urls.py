from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cars'

router = DefaultRouter()
router.register('brands', views.BrandViewSet)
router.register('cars', views.CarViewSet)
router.register('bookings', views.BookingViewSet, basename='booking')
router.register('contracts', views.ContractViewSet, basename='contract')

urlpatterns = [
    path('', include(router.urls)),
]
