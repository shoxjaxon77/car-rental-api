from rest_framework import serializers
from django.utils import timezone
from .models import Brand, Car, Booking, Payment, Contract

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']

class CarListSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    available_count = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Car
        fields = [
            'id', 'brand', 'brand_name', 'model', 'year', 'seats',
            'color', 'price_per_day', 'transmission', 'photo',
            'description', 'available_count', 'is_available'
        ]

class CarDetailSerializer(CarListSerializer):
    class Meta(CarListSerializer.Meta):
        fields = CarListSerializer.Meta.fields + ['total_quantity']

class BookingCreateSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Booking
        fields = ['car', 'start_date', 'end_date', 'total_price']

    def validate(self, data):
        # Sanalarni tekshirish
        if data['start_date'] < timezone.now().date():
            raise serializers.ValidationError(
                "O'tgan sana uchun buyurtma berish mumkin emas"
            )

        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError(
                "Tugash sanasi boshlanish sanasidan keyin bo'lishi kerak"
            )

        # Avtomobil mavjudligini tekshirish
        car = data['car']
        if not car.is_available():
            raise serializers.ValidationError(
                "Kechirasiz, bu avtomobil hozirda mavjud emas"
            )

        return data

    def create(self, validated_data):
        # Foydalanuvchini qo'shish
        user = self.context['request'].user
        validated_data['user'] = user

        # Umumiy narxni hisoblash
        booking = Booking(**validated_data)
        booking.total_price = booking.calculate_total_price()
        booking.save()

        return booking

class BookingListSerializer(serializers.ModelSerializer):
    car = CarListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'car', 'start_date', 'end_date', 'status',
            'status_display', 'total_price', 'created_at'
        ]

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['booking', 'card_type', 'card_number', 'card_expire']
        extra_kwargs = {
            'card_number': {'write_only': True},
            'card_expire': {'write_only': True}
        }

    def validate(self, data):
        # Booking statusini tekshirish
        booking = data['booking']
        if booking.status != 'kutilmoqda':
            raise serializers.ValidationError(
                "Bu buyurtma uchun to'lov qilib bo'lmaydi"
            )

        # Booking foydalanuvchisini tekshirish
        user = self.context['request'].user
        if booking.user != user:
            raise serializers.ValidationError(
                "Siz faqat o'z buyurtmalaringiz uchun to'lov qila olasiz"
            )

        return data

    def create(self, validated_data):
        # Foydalanuvchini va summani qo'shish
        booking = validated_data['booking']
        validated_data['user'] = self.context['request'].user
        validated_data['amount'] = booking.total_price

        # To'lovni yaratish
        payment = Payment.objects.create(**validated_data)

        # Booking statusini yangilash
        booking.status = 'qabul_qilindi'
        booking.save()

        return payment

class PaymentDetailSerializer(serializers.ModelSerializer):
    booking = BookingListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    card_number = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'amount', 'status', 'status_display',
            'card_type', 'card_number', 'created_at'
        ]

    def get_card_number(self, obj):
        # Karta raqamining faqat oxirgi 4 ta raqamini ko'rsatish
        return f"**** **** **** {obj.card_number[-4:]}" if obj.card_number else None

class ContractSerializer(serializers.ModelSerializer):
    booking = BookingListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'booking', 'start_date', 'end_date', 'total_price',
            'status', 'status_display', 'created_at'
        ]
        read_only_fields = ['created_at', 'total_price', 'start_date', 'end_date']
