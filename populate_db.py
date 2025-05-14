import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from cars.models import Brand, Car, Booking, Payment, Contract
from django.utils import timezone

User = get_user_model()

def create_users():
    users = []
    user_data = [
        {'username': 'admin', 'password': 'admin123', 'is_staff': True, 'is_superuser': True, 'phone_number': '+998901234567'},
        {'username': 'user1', 'password': 'user123', 'first_name': 'Aziz', 'last_name': 'Aliyev', 'phone_number': '+998901234568'},
        {'username': 'user2', 'password': 'user123', 'first_name': 'Bobur', 'last_name': 'Karimov', 'phone_number': '+998901234569'},
        {'username': 'user3', 'password': 'user123', 'first_name': 'Dilshod', 'last_name': 'Umarov', 'phone_number': '+998901234570'},
        {'username': 'user4', 'password': 'user123', 'first_name': 'Eldor', 'last_name': 'Sobirov', 'phone_number': '+998901234571'},
    ]
    
    for data in user_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'is_staff': data.get('is_staff', False),
                'is_superuser': data.get('is_superuser', False),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'phone_number': data.get('phone_number', '')
            }
        )
        if created:
            user.set_password(data['password'])
            user.save()
        users.append(user)
    return users

def create_brands():
    brands = []
    brand_names = [
        'Toyota', 'Chevrolet', 'Hyundai', 'Kia', 'BMW',
        'Mercedes-Benz', 'Audi', 'Honda', 'Ford', 'Nissan'
    ]
    
    for name in brand_names:
        brand, _ = Brand.objects.get_or_create(name=name)
        brands.append(brand)
    return brands

def create_car_image_path(brand, model):
    # Generate a unique image filename based on brand and model
    filename = f"{brand}_{model}.jpg".lower().replace(' ', '_')
    return f'car_photos/2023/05/{filename}'

def create_cars(brands):
    cars = []
    car_data = [
        # Toyota
        {'brand': 'Toyota', 'models': [
            ('Camry', 2023, 5, 'Oq', 600000, 2, 'avtomat', 'Premium biznes sedan, qulaylik va tejamkorlik'),
            ('Corolla', 2022, 5, 'Qora', 450000, 3, 'avtomat', 'Ishonchli va ixcham shahar sedani'),
            ('Land Cruiser', 2023, 7, 'Kumush', 1500000, 1, 'avtomat', 'Premium darajadagi hashamatli SUV'),
        ]},
        # Chevrolet
        {'brand': 'Chevrolet', 'models': [
            ('Malibu', 2023, 5, 'Oq', 550000, 3, 'avtomat', 'Zamonaviy biznes sedan, yuqori qulaylik'),
            ('Captiva', 2022, 7, 'Qora', 600000, 2, 'avtomat', 'Keng hajmli oilaviy SUV'),
            ('Tracker', 2023, 5, 'Qizil', 400000, 4, 'avtomat', 'Ixcham va shahar uchun qulay krossover'),
        ]},
        # Hyundai
        {'brand': 'Hyundai', 'models': [
            ('Sonata', 2023, 5, 'Kumush', 500000, 3, 'avtomat', 'Zamonaviy biznes sedan, yuqori texnologiyalar'),
            ('Tucson', 2022, 5, 'Ko\'k', 550000, 2, 'avtomat', 'Stilish va zamonaviy krossover'),
            ('Santa Fe', 2023, 7, 'Qora', 700000, 2, 'avtomat', 'Premium oilaviy SUV, keng salon'),
        ]},
        # BMW
        {'brand': 'BMW', 'models': [
            ('X5', 2023, 5, 'Qora', 1500000, 1, 'avtomat', 'Premium sport SUV, yuqori quvvat'),
            ('520i', 2022, 5, 'Kumush', 1200000, 2, 'avtomat', 'Premium biznes sedan, German sifati'),
            ('X7', 2023, 7, 'Oq', 2000000, 1, 'avtomat', 'Flagman hashamatli SUV, maksimal qulaylik'),
        ]},
        # Mercedes-Benz
        {'brand': 'Mercedes-Benz', 'models': [
            ('E200', 2023, 5, 'Qora', 1300000, 2, 'avtomat', 'Premium biznes sedan, yuqori texnologiya'),
            ('GLE', 2022, 5, 'Kumush', 1600000, 1, 'avtomat', 'Premium hashamatli krossover'),
            ('S500', 2023, 5, 'Oq', 2500000, 1, 'avtomat', 'Flagman premium sedan, maksimal hashamat'),
        ]},
    ]
    
    for brand_data in car_data:
        brand = Brand.objects.get(name=brand_data['brand'])
        for model_data in brand_data['models']:
            car, _ = Car.objects.get_or_create(
                brand=brand,
                model=model_data[0],
                defaults={
                    'year': model_data[1],
                    'seats': model_data[2],
                    'color': model_data[3],
                    'price_per_day': model_data[4],
                    'total_quantity': model_data[5],
                    'transmission': model_data[6],
                    'description': model_data[7],
                    'photo': create_car_image_path(brand.name, model_data[0]),
                    'transmission': model_data[6],
                }
            )
            cars.append(car)
    return cars

def create_bookings(users, cars):
    bookings = []
    statuses = ['kutilmoqda', 'qabul_qilindi', 'rad_etildi']
    
    # Har bir foydalanuvchi uchun
    for user in users[1:]:  # admindan tashqari
        # 3-5 ta buyurtma
        for _ in range(random.randint(3, 5)):
            car = random.choice(cars)
            start_date = timezone.now().date() + timedelta(days=random.randint(1, 30))
            duration = random.randint(1, 7)
            end_date = start_date + timedelta(days=duration)
            status = random.choice(statuses)
            
            booking = Booking.objects.create(
                user=user,
                car=car,
                start_date=start_date,
                end_date=end_date,
                status=status,
                total_price=car.price_per_day * duration
            )
            bookings.append(booking)
    return bookings

def create_payments(bookings):
    payments = []
    card_types = ['uzcard', 'humo', 'visa']
    
    for booking in bookings:
        if booking.status == 'qabul_qilindi':
            card_type = random.choice(card_types)
            card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
            month = str(random.randint(1, 12)).zfill(2)
            year = str(random.randint(25, 30))
            card_expire = f"{month}/{year}"
            
            payment = Payment.objects.create(
                booking=booking,
                user=booking.user,
                amount=booking.total_price,
                card_type=card_type,
                card_number=card_number,
                card_expire=card_expire,
                status='tugallangan'
            )
            payments.append(payment)
    return payments

def create_contracts(bookings):
    contracts = []
    
    for booking in bookings:
        if booking.status == 'qabul_qilindi' and Payment.objects.filter(booking=booking, status='tugallangan').exists():
            contract = Contract.objects.create(
                booking=booking,
                car=booking.car,
                user=booking.user,
                start_date=booking.start_date,
                end_date=booking.end_date,
                total_price=booking.total_price,
                status='faol'
            )
            contracts.append(contract)
    return contracts

def main():
    print("Ma'lumotlar bazasini to'ldirish boshlandi...")
    
    print("1. Foydalanuvchilarni yaratish...")
    users = create_users()
    
    print("2. Brendlarni yaratish...")
    brands = create_brands()
    
    print("3. Avtomobillarni yaratish...")
    cars = create_cars(brands)
    
    print("4. Buyurtmalarni yaratish...")
    bookings = create_bookings(users, cars)
    
    print("5. To'lovlarni yaratish...")
    payments = create_payments(bookings)
    
    print("6. Shartnomalarni yaratish...")
    contracts = create_contracts(bookings)
    
    print("\nStatistika:")
    print(f"Foydalanuvchilar: {User.objects.count()}")
    print(f"Brendlar: {Brand.objects.count()}")
    print(f"Avtomobillar: {Car.objects.count()}")
    print(f"Buyurtmalar: {Booking.objects.count()}")
    print(f"To'lovlar: {Payment.objects.count()}")
    print(f"Shartnomalar: {Contract.objects.count()}")
    
    print("\nMa'lumotlar bazasi muvaffaqiyatli to'ldirildi!")

if __name__ == '__main__':
    main()
