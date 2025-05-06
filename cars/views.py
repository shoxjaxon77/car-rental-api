from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime
from .models import Brand, Car, Booking, Contract
from .serializers import BrandSerializer, CarSerializer, BookingSerializer, ContractSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        car = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({'error': 'Please provide start_date and end_date'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        active_bookings = Booking.objects.filter(
            Q(car=car) & 
            Q(status='accepted') & 
            (Q(start_date__range=[start_date, end_date]) | 
             Q(end_date__range=[start_date, end_date]))
        ).count()

        is_available = active_bookings < car.total_quantity
        return Response({'available': is_available, 
                        'available_quantity': car.total_quantity - active_bookings})

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Check if this is a schema generation request
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'pending':
            return Response({'error': 'Booking can only be accepted when pending'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price
        days = (booking.end_date - booking.start_date).days
        total_price = booking.car.price_per_day * days

        # Create contract
        contract_data = {
            'booking': booking,
            'car': booking.car,
            'user': booking.user,
            'start_date': booking.start_date,
            'end_date': booking.end_date,
            'total_price': total_price,
        }
        Contract.objects.create(**contract_data)

        booking.status = 'accepted'
        booking.save()
        return Response({'status': 'booking accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'pending':
            return Response({'error': 'Booking can only be rejected when pending'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'rejected'
        booking.save()
        return Response({'status': 'booking rejected'})

class ContractViewSet(viewsets.ModelViewSet):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Check if this is a schema generation request
        if getattr(self, 'swagger_fake_view', False):
            return Contract.objects.none()

        if self.request.user.is_staff:
            return Contract.objects.all()
        return Contract.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        contract = self.get_object()
        if contract.status != 'active':
            return Response({'error': 'Contract must be active to complete'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        contract.status = 'completed'
        contract.save()
        return Response({'status': 'contract completed'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        contract = self.get_object()
        if contract.status != 'active':
            return Response({'error': 'Contract must be active to cancel'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        contract.status = 'cancelled'
        contract.save()
        return Response({'status': 'contract cancelled'})
