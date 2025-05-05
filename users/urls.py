from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('profile/', views.get_profile),
    path('profile/update/', views.update_profile),
]