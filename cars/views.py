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
        serializer.is_valid(raise_exception=True)

        try:
            # To'lovni amalga oshirish
            payment = serializer.save(user=request.user)
            
            # To'lov muvaffaqiyatli bo'lsa
            response_serializer = PaymentDetailSerializer(payment)
            return Response({
                'success': True,
                'message': "To'lov muvaffaqiyatli amalga oshirildi",
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'message': "To'lov amalga oshirilmadi",
                'error': str(e)
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

