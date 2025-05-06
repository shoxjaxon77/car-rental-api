from rest_framework import serializers
from .models import Brand, Car, Booking, Contract

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']

class CarSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    available_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'brand', 'brand_name', 'model', 'year', 'seats', 'color', 
                 'price_per_day', 'total_quantity', 'available_count', 'photo', 'description']

class BookingSerializer(serializers.ModelSerializer):
    car_details = CarSerializer(source='car', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'car', 'car_details', 'user_email', 'start_date', 
                 'end_date', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data

class ContractSerializer(serializers.ModelSerializer):
    booking_details = BookingSerializer(source='booking', read_only=True)
    car_details = CarSerializer(source='car', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Contract
        fields = ['id', 'booking', 'booking_details', 'car', 'car_details', 
                 'user', 'user_email', 'start_date', 'end_date', 'total_price', 
                 'status', 'created_at']
        read_only_fields = ['created_at']
