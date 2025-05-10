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
        start_date = data['start_date']
        end_date = data['end_date']
        today = timezone.now().date()

        if start_date < today:
            raise serializers.ValidationError({
                'start_date': "O'tgan sana uchun buyurtma berish mumkin emas"
            })

        if end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': "Tugash sanasi boshlanish sanasidan keyin bo'lishi kerak"
            })

        # Buyurtma muddatini tekshirish (maksimum 30 kun)
        duration = (end_date - start_date).days
        if duration > 30:
            raise serializers.ValidationError({
                'end_date': "Buyurtma muddati 30 kundan oshmasligi kerak"
            })

        # Avtomobil mavjudligini tekshirish
        car = data['car']
        
        # Parallel buyurtmalarni tekshirish
        overlapping_bookings = Booking.objects.filter(
            car=car,
            status='qabul_qilindi',
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()

        overlapping_contracts = Contract.objects.filter(
            car=car,
            status='faol',
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()

        if overlapping_bookings or overlapping_contracts:
            raise serializers.ValidationError({
                'car': "Bu vaqt oralig'ida avtomobil band"
            })

        # Foydalanuvchining aktiv buyurtmalari sonini tekshirish
        user = self.context['request'].user
        active_bookings = Booking.objects.filter(
            user=user,
            status__in=['kutilmoqda', 'qabul_qilindi']
        ).count()

        if active_bookings >= 3:
            raise serializers.ValidationError(
                "Sizda 3 ta aktiv buyurtma mavjud. Yangi buyurtma berish uchun avval ularni yakunlang."
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
        booking = data['booking']
        user = self.context['request'].user

        # Booking statusini tekshirish
        if booking.status != 'kutilmoqda':
            raise serializers.ValidationError({
                'booking': "Bu buyurtma uchun to'lov qilib bo'lmaydi"
            })

        # Booking foydalanuvchisini tekshirish
        if booking.user != user:
            raise serializers.ValidationError({
                'booking': "Siz faqat o'z buyurtmalaringiz uchun to'lov qila olasiz"
            })

        # Buyurtma muddati o'tib ketmaganligini tekshirish
        if booking.start_date < timezone.now().date():
            booking.status = 'rad_etildi'
            booking.save()
            raise serializers.ValidationError({
                'booking': "Buyurtma muddati o'tib ketgan"
            })

        # Karta raqami validatsiyasi (Luhn algoritmi)
        card_number = data['card_number']
        if not self.is_valid_card_number(card_number):
            raise serializers.ValidationError({
                'card_number': "Noto'g'ri karta raqami"
            })

        # Karta amal qilish muddatini tekshirish
        try:
            month, year = data['card_expire'].split('/')
            month = int(month)
            year = int('20' + year)
            
            if not (1 <= month <= 12):
                raise ValueError("Noto'g'ri oy")
                
            expiry_date = timezone.datetime(year, month, 1).date()
            if expiry_date < timezone.now().date():
                raise serializers.ValidationError({
                    'card_expire': "Karta muddati tugagan"
                })
        except (ValueError, IndexError):
            raise serializers.ValidationError({
                'card_expire': "Noto'g'ri sana formati (MM/YY)"
            })

        return data

    def is_valid_card_number(self, card_number):
        """Luhn algoritmi yordamida karta raqamini tekshirish"""
        if not card_number.isdigit() or len(card_number) != 16:
            return False

        digits = [int(d) for d in card_number]
        checksum = 0
        is_odd = True

        for d in digits[::-1]:
            if is_odd:
                checksum += d
            else:
                d *= 2
                if d > 9:
                    d -= 9
                checksum += d
            is_odd = not is_odd

        return (checksum % 10) == 0

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
