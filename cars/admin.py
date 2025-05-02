from django.contrib import admin
from .models import Car, Rent, Order

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'price_per_day', 'available')
    list_filter = ('available', 'brand')
    search_fields = ('name', 'brand', 'model')

@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'start_date', 'end_date', 'total_price', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'car__brand')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('rent', 'confirmed_at', 'is_active')
    list_filter = ('is_active',)
