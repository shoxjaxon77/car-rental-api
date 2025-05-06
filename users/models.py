from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    REQUIRED_FIELDS = ['email', 'phone_number', 'first_name', 'last_name']
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username
