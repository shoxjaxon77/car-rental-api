from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?998\d{9}$',
        message="Telefon raqam +998 bilan boshlanishi va 12 ta raqamdan iborat bo'lishi kerak"
    )

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[phone_regex],
        verbose_name="Telefon raqami",
        help_text="Format: +998901234567"
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Manzil"
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Profil rasmi"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email', 'phone_number', 'first_name', 'last_name']
    USERNAME_FIELD = 'username'

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    def get_active_bookings(self):
        return self.bookings.filter(status='qabul_qilindi')

    def get_active_contracts(self):
        return self.contracts.filter(status='faol')
