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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # To'lov ma'lumotlarini qaytarish
        return Response({
            'booking_id': booking.id,
            'total_price': booking.total_price,
            'message': "Buyurtma yaratildi. To'lovni amalga oshiring."
        }, status=status.HTTP_201_CREATED)

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
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            
            # Tranzaksiyani boshlash
            with transaction.atomic():
                # To'lovni amalga oshirish
                payment = serializer.save(user=request.user)
                
                # Shartnoma yaratish
                booking = payment.booking
                contract = Contract.objects.create(
                    booking=booking,
                    car=booking.car,
                    user=booking.user,
                    start_date=booking.start_date,
                    end_date=booking.end_date,
                    total_price=booking.total_price,
                    status='faol'
                )
                
                # To'lov muvaffaqiyatli bo'lsa
                response_serializer = PaymentDetailSerializer(payment)
                return Response({
                    'success': True,
                    'message': "To'lov muvaffaqiyatli amalga oshirildi",
                    'data': {
                        'payment': response_serializer.data,
                        'contract_id': contract.id
                    }
                }, status=status.HTTP_201_CREATED)
                
        except serializers.ValidationError as e:
            return Response({
                'success': False,
                'message': "Validatsiya xatosi",
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except IntegrityError:
            return Response({
                'success': False,
                'message': "Ma'lumotlar bazasida xatolik yuz berdi"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Xatoni logga yozish
            logger.error(f"Payment error: {str(e)}")
            return Response({
                'success': False,
                'message': "Serverda xatolik yuz berdi"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

class ContractUpdateView(generics.UpdateAPIView):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Contract.objects.filter(
            user=self.request.user,
            status='faol'
        )
    
    def update(self, request, *args, **kwargs):
        contract = self.get_object()
        
        # Faqat bekor qilish yoki yakunlashga ruxsat berish
        new_status = request.data.get('status')
        if new_status not in ['yakunlangan', 'bekor_qilingan']:
            return Response({
                'success': False,
                'message': "Noto'g'ri status"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            with transaction.atomic():
                # Shartnoma statusini yangilash
                contract.status = new_status
                contract.save()
                
                # Buyurtma statusini yangilash
                if new_status == 'bekor_qilingan':
                    contract.booking.status = 'rad_etildi'
                else:
                    contract.booking.status = 'yakunlangan'
                contract.booking.save()
                
                return Response({
                    'success': True,
                    'message': f"Shartnoma {contract.get_status_display().lower()}"
                })
                
        except Exception as e:
            logger.error(f"Contract update error: {str(e)}")
            return Response({
                'success': False,
                'message': "Serverda xatolik yuz berdi"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

