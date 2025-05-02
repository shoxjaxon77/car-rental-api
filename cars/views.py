from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Car, Rent, Order
from .serializers import CarSerializer, RentSerializer, OrderSerializer


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'brand', 'model']


class RentViewSet(viewsets.ModelViewSet):
    serializer_class = RentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Rent.objects.all()
        return Rent.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        rent = self.get_object()
        if rent.status != 'pending':
            return Response({'error': 'To\'lov qo\'shib bo\'lmaydi'}, status=400)
        
        if 'payment_image' not in request.data:
            return Response({'error': 'To\'lov rasmi yuborilmadi'}, status=400)
        
        rent.payment_image = request.data['payment_image']
        rent.status = 'paid'
        rent.save()
        return Response({'status': 'To\'lov qabul qilindi'})


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(rent__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve_rent(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Faqat adminlar tasdiqlashi mumkin'}, status=403)
        
        rent = Rent.objects.get(pk=pk)
        if rent.status != 'paid':
            return Response({'error': 'Faqat to\'langan arizalarni tasdiqlash mumkin'}, status=400)
        
        rent.status = 'approved'
        rent.save()
        
        # Create order
        order = Order.objects.create(rent=rent)
        
        # Update car availability
        rent.car.available = False
        rent.car.save()
        
        return Response({'status': 'Ariza tasdiqlandi'})
