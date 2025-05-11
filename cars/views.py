from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F, Q
from django.utils import timezone
from .models import Brand, Car, Booking, Payment, Contract
from .serializers import (
    BrandSerializer, CarListSerializer, CarDetailSerializer,
    BookingCreateSerializer, BookingListSerializer,
    PaymentCreateSerializer, PaymentDetailSerializer,
    ContractSerializer
)

class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated]

class CarListView(generics.ListAPIView):
    serializer_class = CarListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Car.objects.all().select_related('brand')

        # Filtrlash
        brand = self.request.query_params.get('brand', None)
        if brand:
            queryset = queryset.filter(brand_id=brand)

        seats = self.request.query_params.get('seats', None)
        if seats:
            queryset = queryset.filter(seats=seats)

        transmission = self.request.query_params.get('transmission', None)
        if transmission:
            queryset = queryset.filter(transmission=transmission)

        min_price = self.request.query_params.get('min_price', None)
        if min_price:
            queryset = queryset.filter(price_per_day__gte=min_price)

        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(price_per_day__lte=max_price)

        # Faqat mavjud avtomobillarni ko'rsatish
        available = self.request.query_params.get('available', None)
        if available and available.lower() == 'true':
            queryset = queryset.filter(total_quantity__gt=0)

        return queryset

class CarDetailView(generics.RetrieveAPIView):
    queryset = Car.objects.all().select_related('brand')
    serializer_class = CarDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Ma'lumotlarni olish
            car_id = request.data.get('car')
            try:
                start_date = timezone.datetime.strptime(request.data.get('start_date'), '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(request.data.get('end_date'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'message': "Sana formati noto'g'ri (YYYY-MM-DD)"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Avtomobilni olish
            car = Car.objects.get(id=car_id)
            
            # Buyurtmani yaratish
            booking = Booking.objects.create(
                car=car,
                user=request.user,
                start_date=start_date,
                end_date=end_date,
                status='kutilmoqda'
            )
            
            # Kunlar sonini va umumiy summani hisoblash
            days = (booking.end_date - booking.start_date).days
            total_price = days * car.price_per_day
            
            return Response({
                'success': True,
                'message': 'Buyurtma yaratildi',
                'data': {
                    'booking_id': booking.id,
                    'car_name': car.name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': days,
                    'price_per_day': car.price_per_day,
                    'total_price': total_price
                }
            })
            
        except Car.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Avtomobil topilmadi'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class BookingListView(generics.ListAPIView):
    serializer_class = BookingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related('car', 'car__brand')

class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # To'lov ma'lumotlarini olish
            booking_id = request.data.get('booking')
            card_number = request.data.get('card_number', '')
            card_expire = request.data.get('card_expire', '')
            
            # Karta raqamini tekshirish
            if not card_number.isdigit() or len(card_number) != 16:
                return Response({
                    'success': False,
                    'message': "Karta raqami 16 ta raqamdan iborat bo'lishi kerak"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Karta muddatini tekshirish
            if not card_expire or len(card_expire) != 5:
                return Response({
                    'success': False,
                    'message': "Karta muddati MM/YY formatida bo'lishi kerak"
                }, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                month, year = card_expire.split('/')
                if not (1 <= int(month) <= 12 and len(year) == 2):
                    raise ValueError
            except ValueError:
                return Response({
                    'success': False,
                    'message': "Karta muddati noto'g'ri"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buyurtmani olish
            booking = Booking.objects.get(id=booking_id, user=request.user)
            
            # To'lov summasini hisoblash
            days = (booking.end_date - booking.start_date).days
            total_price = days * booking.car.price_per_day
            
            # To'lovni saqlash
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                amount=total_price,
                card_number=card_number,
                card_expire=card_expire,
                status='kutilmoqda'
            )
            
            # Buyurtma statusini yangilash
            booking.status = 'kutilmoqda'
            booking.save()
            
            return Response({
                'success': True,
                'message': "To'lov muvaffaqiyatli amalga oshirildi",
                'data': {
                    'payment_id': payment.id,
                    'amount': total_price,
                    'status': 'kutilmoqda'
                }
            })
            
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'message': "Buyurtma topilmadi"
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            user=self.request.user
        ).select_related('booking', 'booking__car')

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            user=self.request.user
        ).select_related('booking', 'booking__car')

class ContractListView(generics.ListAPIView):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contract.objects.filter(
            user=self.request.user
        ).select_related('booking', 'booking__car')

class ContractDetailView(generics.RetrieveAPIView):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contract.objects.filter(
            user=self.request.user
        ).select_related('booking', 'booking__car')

class ContractCreateView(generics.CreateAPIView):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def create(self, request, *args, **kwargs):
        try:
            # Ma'lumotlarni olish
            booking_id = request.data.get('booking')
            booking = Booking.objects.get(id=booking_id)
            
            # Buyurtma statusini tekshirish
            if booking.status != 'kutilmoqda':
                return Response({
                    'success': False,
                    'message': "Buyurtma holati noto'g'ri"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # To'lovni tekshirish
            payment = Payment.objects.filter(booking=booking, status='kutilmoqda').first()
            if not payment:
                return Response({
                    'success': False,
                    'message': "To'lov topilmadi yoki yakunlanmagan"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Shartnoma yaratish
            contract = Contract.objects.create(
                booking=booking,
                car=booking.car,
                user=booking.user,
                start_date=booking.start_date,
                end_date=booking.end_date,
                total_price=payment.amount,
                status='faol'
            )
            
            # Buyurtma statusini yangilash
            booking.status = 'qabul_qilindi'
            booking.save()
            
            return Response({
                'success': True,
                'message': 'Shartnoma yaratildi',
                'data': {
                    'contract_id': contract.id
                }
            })
            
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'message': "Buyurtma topilmadi"
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

