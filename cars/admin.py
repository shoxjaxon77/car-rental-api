from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Brand, Car, Booking, Contract

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_count')
    search_fields = ('name',)
    
    def car_count(self, obj):
        return obj.cars.count()
    car_count.short_description = 'Total Cars'

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('car_info', 'price_display', 'availability_status', 'booking_count')
    list_filter = ('brand', 'year', 'seats', 'color')
    search_fields = ('brand__name', 'model', 'color')
    list_per_page = 20
    ordering = ('brand', 'model')

    def car_info(self, obj):
        return format_html(
            '<strong>{}</strong> - {} ({})<br/>'
            '<small style="color: #666;">{}-seats, {}</small>',
            obj.brand.name, obj.model, obj.year,
            obj.seats, obj.color
        )
    car_info.short_description = 'Car Details'

    def price_display(self, obj):
        return format_html('<b style="color: green;">${}/day</b>', obj.price_per_day)
    price_display.short_description = 'Price'

    def availability_status(self, obj):
        available = obj.available_count()
        total = obj.total_quantity
        color = 'green' if available == total else 'orange' if available > 0 else 'red'
        return format_html(
            '<span style="color: {};">Available: {}/{}</span>',
            color, available, total
        )
    availability_status.short_description = 'Availability'

    def booking_count(self, obj):
        count = obj.bookings.count()
        return format_html('<span style="color: blue;">{}</span>', count)
    booking_count.short_description = 'Total Bookings'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_info', 'duration', 'status_badge', 'created_at')
    list_filter = ('status', 'start_date', 'end_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'car__model', 'car__brand__name')
    list_per_page = 20
    ordering = ('-created_at',)
    
    def save_model(self, request, obj, form, change):
        # Agar status o'zgartirilgan bo'lsa va yangi status 'qabul_qilindi' bo'lsa
        if change and 'status' in form.changed_data and obj.status == 'qabul_qilindi':
            # Kunlar sonini va umumiy summani hisoblash
            days = (obj.end_date - obj.start_date).days
            total_price = days * obj.car.price_per_day
            
            # Shartnoma yaratish
            Contract.objects.create(
                booking=obj,
                car=obj.car,
                user=obj.user,
                start_date=obj.start_date,
                end_date=obj.end_date,
                total_price=total_price,
                status='faol'
            )
        
        super().save_model(request, obj, form, change)

    def booking_info(self, obj):
        return format_html(
            '<strong>{}</strong> booked by {}<br/>'
            '<small style="color: #666;">{} {} ({})</small>',
            obj.car.model,
            obj.user.username,
            obj.car.brand.name,
            obj.car.year,
            obj.car.color
        )
    booking_info.short_description = 'Booking Details'

    def duration(self, obj):
        days = (obj.end_date - obj.start_date).days
        return format_html('{} days<br/><small>{} → {}</small>', 
                         days, obj.start_date.strftime('%Y-%m-%d'), 
                         obj.end_date.strftime('%Y-%m-%d'))
    duration.short_description = 'Duration'

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
            'completed': 'blue'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status.lower(), 'gray'),
            obj.status.title()
        )
    status_badge.short_description = 'Status'

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_info', 'price_info', 'status_badge', 'dates_info')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('booking__user__username', 'booking__car__model', 'booking__car__brand__name')
    list_per_page = 20
    ordering = ('-start_date',)

    def contract_info(self, obj):
        return format_html(
            '<strong>{}</strong><br/>'
            '<small style="color: #666;">User: {}</small>',
            f"{obj.car.brand.name} {obj.car.model}",
            obj.user.username
        )
    contract_info.short_description = 'Contract Details'

    def price_info(self, obj):
        return format_html(
            '<strong style="color: green;">${}</strong><br/>'
            '<small>(${}/day)</small>',
            obj.total_price,
            obj.car.price_per_day
        )
    price_info.short_description = 'Price Info'

    def dates_info(self, obj):
        days = (obj.end_date - obj.start_date).days
        return format_html(
            '{} days<br/>'
            '<small>{} → {}</small>',
            days,
            obj.start_date.strftime('%Y-%m-%d'),
            obj.end_date.strftime('%Y-%m-%d')
        )
    dates_info.short_description = 'Duration'

    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'completed': 'blue',
            'cancelled': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status.lower(), 'gray'),
            obj.status.title()
        )
    status_badge.short_description = 'Status'
