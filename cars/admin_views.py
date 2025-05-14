from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import Booking, Car, Contract, Payment, Brand
from users.models import CustomUser

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('cars:admin_dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                return redirect('cars:admin_dashboard')
            else:
                messages.error(request, 'Sizda admin huquqlari mavjud emas')
    else:
        form = AuthenticationForm()
    
    return render(request, 'cars/admin/login.html', {'form': form})

@login_required
def admin_logout(request):
    logout(request)
    return redirect('cars:admin_login')

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def dashboard(request):
    # Statistika
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='kutilmoqda').count()
    active_contracts = Contract.objects.filter(status='faol').count()
    total_users = CustomUser.objects.filter(is_staff=False).count()
    
    # So'nggi arizalar
    recent_bookings = Booking.objects.select_related('user', 'car').order_by('-created_at')[:5]
    
    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'active_contracts': active_contracts,
        'total_users': total_users,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'cars/admin/dashboard.html', context)

@login_required
@user_passes_test(is_staff)
def booking_list(request):
    status = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    bookings = Booking.objects.all()
    
    # Apply status filter
    if status:
        bookings = bookings.filter(status=status)
    
    # Apply search
    if search_query:
        bookings = bookings.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__phone__icontains=search_query) |
            Q(car__name__icontains=search_query) |
            Q(car__number__icontains=search_query)
        )
    
    bookings = bookings.select_related('user', 'car').order_by('-created_at')
    
    context = {
        'bookings': bookings,
        'current_status': status,
        'search_query': search_query
    }
    return render(request, 'cars/admin/booking_list.html', context)

@login_required
@user_passes_test(is_staff)
def booking_action(request, booking_id, action):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if action == 'accept':
        if booking.car.is_available():
            booking.status = 'qabul_qilindi'
            booking.save()
            
            # Shartnoma yaratish
            contract = Contract.objects.create(
                booking=booking,
                car=booking.car,
                user=booking.user,
                start_date=booking.start_date,
                end_date=booking.end_date,
                total_price=booking.total_price,
                status='faol'
            )
            messages.success(request, 'Ariza qabul qilindi va shartnoma yaratildi')
        else:
            messages.error(request, 'Avtomobil hozirda mavjud emas')
    
    elif action == 'reject':
        booking.status = 'rad_etildi'
        booking.save()
        messages.success(request, 'Ariza rad etildi')
    
    return redirect('cars:admin_booking_list')

@login_required
@user_passes_test(is_staff)
def contract_list(request):
    status = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    contracts = Contract.objects.all()
    
    # Apply status filter
    if status:
        contracts = contracts.filter(status=status)
    
    # Apply search
    if search_query:
        contracts = contracts.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__phone__icontains=search_query) |
            Q(car__name__icontains=search_query) |
            Q(car__number__icontains=search_query) |
            Q(booking__id__icontains=search_query)
        )
    
    contracts = contracts.select_related('user', 'car', 'booking').order_by('-created_at')
    
    context = {
        'contracts': contracts,
        'current_status': status,
        'search_query': search_query
    }
    return render(request, 'cars/admin/contract_list.html', context)

@login_required
@user_passes_test(is_staff)
def contract_action(request, contract_id, action):
    contract = get_object_or_404(Contract, id=contract_id)
    
    if action == 'complete':
        contract.status = 'yakunlangan'
        contract.save()
        messages.success(request, 'Shartnoma yakunlandi')
    
    elif action == 'cancel':
        contract.status = 'bekor_qilingan'
        contract.save()
        messages.success(request, 'Shartnoma bekor qilindi')
    
    return redirect('cars:admin_contract_list')

@login_required
@user_passes_test(is_staff)
def customer_list(request):
    # Get filters from request
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    sort = request.GET.get('sort', '-created_at')
    
    # Base queryset
    customers = CustomUser.objects.filter(is_staff=False)
    
    # Apply search
    if search_query:
        customers = customers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Apply status filter
    if status == 'active':
        customers = customers.filter(is_active=True)
    elif status == 'inactive':
        customers = customers.filter(is_active=False)
    
    # Annotate with bookings count
    customers = customers.annotate(
        bookings_count=Count('bookings'),
        last_booking_date=Max('bookings__created_at')
    )
    
    # Apply sorting
    customers = customers.order_by(sort)
    
    # Get statistics
    total_customers = customers.count()
    active_customers = customers.filter(is_active=True).count()
    today_bookings = Booking.objects.filter(
        user__in=customers,
        created_at__date=timezone.now().date()
    ).count()
    
    context = {
        'customers': customers,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'today_bookings': today_bookings,
        'search_query': search_query,
        'selected_status': status,
        'selected_sort': sort
    }
    
    return render(request, 'cars/admin/customer_list.html', context)

@login_required
@user_passes_test(is_staff)
def car_list(request):
    # Get filters from request
    search_query = request.GET.get('search', '')
    brand = request.GET.get('brand', '')
    transmission = request.GET.get('transmission', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Base queryset
    cars = Car.objects.select_related('brand')
    
    # Apply search
    if search_query:
        cars = cars.filter(
            Q(brand__name__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(color__icontains=search_query)
        )
    
    # Apply filters
    if brand:
        cars = cars.filter(brand__name=brand)
    if transmission:
        cars = cars.filter(transmission=transmission)
    
    min_price = request.GET.get('min_price')
    if min_price:
        cars = cars.filter(price_per_day__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        cars = cars.filter(price_per_day__lte=max_price)
    
    # Statistika
    total_cars = cars.count()
    available_cars = sum(1 for car in cars if car.is_available())
    total_bookings = Booking.objects.filter(car__in=cars).count()
    active_contracts = Contract.objects.filter(car__in=cars, status='faol').count()
    
    # Brendlar ro'yxati (filter uchun)
    brands = Brand.objects.all()
    
    context = {
        'cars': cars,
        'brands': brands,
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_bookings': total_bookings,
        'active_contracts': active_contracts,
        'search_query': search_query,
        'selected_brand': brand,
        'selected_transmission': transmission,
        'min_price': min_price,
        'max_price': max_price
    }
    
    return render(request, 'cars/admin/car_list.html', context)

@login_required
@user_passes_test(is_staff)
def car_create(request):
    if request.method == 'POST':
        car = Car()
        brand_name = request.POST.get('brand')
        brand, created = Brand.objects.get_or_create(name=brand_name)
        
        car.brand = brand
        car.model = request.POST.get('model')
        car.year = request.POST.get('year')
        car.seats = request.POST.get('seats')
        car.total_quantity = request.POST.get('total_quantity')
        car.price_per_day = request.POST.get('price_per_day')
        car.color = request.POST.get('color')
        car.transmission = request.POST.get('transmission')
        car.description = request.POST.get('description')
        car.is_available = request.POST.get('is_available') == 'on'
        
        if request.FILES.get('image'):
            car.image = request.FILES['image']
        
        car.save()
        messages.success(request, "Avtomobil muvaffaqiyatli qo'shildi")
        return redirect('cars:admin_car_list')
    return render(request, 'cars/admin/car_form.html')

@login_required
@user_passes_test(is_staff)
def car_edit(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        brand_name = request.POST.get('brand')
        brand, created = Brand.objects.get_or_create(name=brand_name)
        
        car.brand = brand
        car.model = request.POST.get('model')
        car.year = request.POST.get('year')
        car.seats = request.POST.get('seats')
        car.total_quantity = request.POST.get('total_quantity')
        car.price_per_day = request.POST.get('price_per_day')
        car.color = request.POST.get('color')
        car.transmission = request.POST.get('transmission')
        car.description = request.POST.get('description')
        car.is_available = request.POST.get('is_available') == 'on'
        
        if request.FILES.get('image'):
            car.image = request.FILES['image']
        
        car.save()
        messages.success(request, "Avtomobil muvaffaqiyatli yangilandi")
        return redirect('cars:admin_car_list')
    return render(request, 'cars/admin/car_form.html', {'car': car})

@login_required
@user_passes_test(is_staff)
def car_delete(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    car.delete()
    messages.success(request, "Avtomobil muvaffaqiyatli o'chirildi")
    return redirect('cars:admin_car_list')
