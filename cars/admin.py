from django.contrib import admin
from .models import Car, Rent, Order, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_day', 'category', 'available']
    list_filter = ['category', 'available']
    search_fields = ['name', 'description']

@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'start_date', 'end_date', 'total_price', 'status']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['user__email', 'car__name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['rent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['rent__user__email', 'rent__car__name']
