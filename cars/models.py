from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from users.models import CustomUser

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Avtomobil brendining nomi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Brend'
        verbose_name_plural = 'Brendlar'

    def __str__(self):
        return self.name

class Car(models.Model):
    TRANSMISSION_CHOICES = (
        ('avtomat', 'Avtomat'),
        ('mexanik', 'Mexanik'),
    )

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='cars', verbose_name="Brend")
    model = models.CharField(max_length=100, verbose_name="Model")
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(timezone.now().year + 1)],
        verbose_name="Ishlab chiqarilgan yil"
    )
    seats = models.PositiveIntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(50)],
        verbose_name="O'rindiqlar soni"
    )
    color = models.CharField(max_length=30, verbose_name="Rangi")
    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Kunlik ijara narxi"
    )
    total_quantity = models.PositiveIntegerField(verbose_name="Umumiy soni")
    transmission = models.CharField(
        max_length=10,
        choices=TRANSMISSION_CHOICES,
        default='avtomat',
        verbose_name="Transmissiya"
    )
    photo = models.ImageField(
        upload_to='car_photos/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Rasm"
    )
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Avtomobil'
        verbose_name_plural = 'Avtomobillar'

    def available_count(self):
        # Faol shartnomalar va tasdiqlangan buyurtmalarni hisobga olish
        active_contracts = Contract.objects.filter(car=self, status='faol').count()
        confirmed_bookings = Booking.objects.filter(
            car=self,
            status='qabul_qilindi',
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).count()
        return self.total_quantity - (active_contracts + confirmed_bookings)

    def is_available(self):
        return self.available_count() > 0

    def __str__(self):
        return f"{self.brand.name} {self.model} ({self.year})"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('kutilmoqda', 'Kutilmoqda'),
        ('qabul_qilindi', 'Qabul qilindi'),
        ('rad_etildi', 'Rad etildi'),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Foydalanuvchi"
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Avtomobil"
    )
    start_date = models.DateField(verbose_name="Boshlanish sanasi")
    end_date = models.DateField(verbose_name="Tugash sanasi")
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='kutilmoqda',
        verbose_name="Holat",
        db_index=True  # Status bo'yicha tez-tez qidiriladi
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Umumiy narx",
        help_text="Kunlik narx * Kunlar soni"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'status']),
        ]

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("Tugash sanasi boshlanish sanasidan oldin bo'lishi mumkin emas.")
            
        if self.start_date < timezone.now().date():
            raise ValidationError("O'tgan sana uchun buyurtma berish mumkin emas.")
            
        # Avtomobil mavjudligini tekshirish
        overlapping_bookings = Booking.objects.filter(
            car=self.car,
            status='qabul_qilindi',
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exclude(pk=self.pk).exists()
        
        overlapping_contracts = Contract.objects.filter(
            car=self.car,
            status='faol',
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exists()
        
        if overlapping_bookings or overlapping_contracts:
            raise ValidationError("Bu vaqt oralig'ida avtomobil band.")
            
        # Umumiy narxni hisoblash
        duration = (self.end_date - self.start_date).days
        if duration < 1:
            raise ValidationError("Ijara muddati kamida 1 kun bo'lishi kerak.")
        self.total_price = self.car.price_per_day * duration

    def get_duration(self):
        return (self.end_date - self.start_date).days

    def calculate_total_price(self):
        duration = self.get_duration()
        return duration * self.car.price_per_day

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.car} ({self.get_status_display()})"

class Payment(models.Model):
    STATUS_CHOICES = (
        ('kutilmoqda', 'Kutilmoqda'),
        ('tugallangan', 'Tugallangan'),
        ('xatolik', 'Xatolik'),
    )

    CARD_TYPE_CHOICES = (
        ('uzcard', 'UzCard'),
        ('humo', 'Humo'),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
    )

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name="Buyurtma"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Foydalanuvchi"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Summa",
        help_text="To'lov summasi"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='kutilmoqda',
        verbose_name="Holat",
        db_index=True  # Status bo'yicha tez-tez qidiriladi
    )
    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPE_CHOICES,
        verbose_name="Karta turi"
    )
    card_number = models.CharField(
        max_length=16,
        verbose_name="Karta raqami",
        help_text="16 xonali karta raqami"
    )
    card_expire = models.CharField(
        max_length=5,
        verbose_name="Amal qilish muddati",
        help_text="Format: MM/YY"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'status']),
        ]

    def clean(self):
        # Buyurtma tasdiqlangan bo'lishi kerak
        if self.booking.status != 'qabul_qilindi':
            raise ValidationError("Faqat tasdiqlangan buyurtmalar uchun to'lov qilish mumkin.")
            
        # To'lov summasi buyurtma summasiga teng bo'lishi kerak
        if self.amount and self.amount != self.booking.total_price:
            raise ValidationError("To'lov summasi buyurtma summasiga teng bo'lishi kerak.")
            
        # Karta raqami validatsiyasi
        if not self.card_number.isdigit() or len(self.card_number) != 16:
            raise ValidationError("Karta raqami 16 ta raqamdan iborat bo'lishi kerak")

        # Amal qilish muddati validatsiyasi
        if not self.card_expire or len(self.card_expire) != 5:
            raise ValidationError("Amal qilish muddati MM/YY formatida bo'lishi kerak")

        try:
            month, year = self.card_expire.split('/')
            if not (1 <= int(month) <= 12 and len(year) == 2):
                raise ValidationError("Noto'g'ri sana formati")
        except ValueError:
            raise ValidationError("Noto'g'ri sana formati")

    def save(self, *args, **kwargs):
        if not self.amount:
            self.amount = self.booking.total_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"To'lov: {self.user.get_full_name()} - {self.amount:,.2f} so'm ({self.get_status_display()})"

class Contract(models.Model):
    STATUS_CHOICES = (
        ('faol', 'Faol'),
        ('yakunlangan', 'Yakunlangan'),
        ('bekor_qilingan', 'Bekor qilingan'),
    )

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='contract',
        verbose_name="Buyurtma"
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='contracts',
        verbose_name="Avtomobil"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='contracts',
        verbose_name="Foydalanuvchi"
    )
    start_date = models.DateField(verbose_name="Boshlanish sanasi")
    end_date = models.DateField(verbose_name="Tugash sanasi")
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Umumiy narx"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='faol',
        verbose_name="Holat"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Shartnoma'
        verbose_name_plural = 'Shartnomalar'

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("Tugash sanasi boshlanish sanasidan oldin bo'lishi mumkin emas.")
            
        # Avtomobil mavjudligini tekshirish
        overlapping_contracts = Contract.objects.filter(
            car=self.car,
            status='faol',
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exclude(pk=self.pk).exists()
        
        if overlapping_contracts:
            raise ValidationError("Bu vaqt oralig'ida avtomobil band.")
            
        # Buyurtma tasdiqlangan bo'lishi kerak
        if self.booking.status != 'qabul_qilindi':
            raise ValidationError("Faqat tasdiqlangan buyurtmalar uchun shartnoma tuzish mumkin.")
            
        # Shartnoma ma'lumotlari buyurtma ma'lumotlariga mos kelishi kerak
        if (self.car != self.booking.car or
            self.user != self.booking.user or
            self.start_date != self.booking.start_date or
            self.end_date != self.booking.end_date or
            self.total_price != self.booking.total_price):
            raise ValidationError("Shartnoma ma'lumotlari buyurtma ma'lumotlariga mos kelishi kerak.")

    def get_duration(self):
        return (self.end_date - self.start_date).days

    def __str__(self):
        return f"Shartnoma: {self.car} - {self.user.get_full_name()}"
