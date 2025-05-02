from rest_framework import serializers
from .models import Car, Rent, Order
from users.serializers import UserSerializer


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'


class RentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    car = CarSerializer(read_only=True)
    car_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Rent
        fields = ('id', 'user', 'car', 'car_id', 'start_date', 'end_date', 
                 'status', 'total_price', 'payment_image', 'created_at')
        read_only_fields = ('status', 'total_price')
    
    def create(self, validated_data):
        car = Car.objects.get(id=validated_data.pop('car_id'))
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
        fields = ('id', 'rent', 'confirmed_at', 'is_active')
        read_only_fields = ('confirmed_at',)
