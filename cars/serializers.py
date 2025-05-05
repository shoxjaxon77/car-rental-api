from rest_framework import serializers
from .models import Car, Rent, Order, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class CarSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Car
        fields = ['id', 'name', 'description', 'price_per_day', 'image', 'category', 'category_id', 'available']

class RentSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    car_id = serializers.PrimaryKeyRelatedField(
        queryset=Car.objects.all(),
        source='car',
        write_only=True
    )

    class Meta:
        model = Rent
        fields = ['id', 'car', 'car_id', 'start_date', 'end_date', 'total_price', 'status']
        read_only_fields = ['status', 'total_price']

    def create(self, validated_data):
        car = validated_data['car']
        days = (validated_data['end_date'] - validated_data['start_date']).days + 1
        total_price = car.price_per_day * days
        
        rent = Rent.objects.create(
            user=self.context['request'].user,
            car=car,
            total_price=total_price,
            **validated_data
        )
        return rent

class OrderSerializer(serializers.ModelSerializer):
    rent = RentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'rent']