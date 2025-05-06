from django.contrib import admin
from .models import Brand, Car, Booking, Contract

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'seats', 'color', 'price_per_day', 'total_quantity', 'available_count')
    list_filter = ('brand', 'year', 'seats')
    search_fields = ('brand__name', 'model')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__username', 'car__model')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('booking', 'car', 'user', 'start_date', 'end_date', 'total_price', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__username', 'car__model')
