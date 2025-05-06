from django.db import models
from users.models import CustomUser

class Brand(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Car(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='cars')
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    seats = models.PositiveIntegerField()
    color = models.CharField(max_length=30)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.PositiveIntegerField()
    photo = models.ImageField(upload_to='car_photos/', blank=True, null=True)
    description = models.TextField(blank=True)

    def available_count(self):
        active_contracts = Contract.objects.filter(car=self, status='active').count()
        return self.total_quantity - active_contracts

    def __str__(self):
        return f"{self.brand.name} {self.model} ({self.year})"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.car} ({self.status})"

class Contract(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, default='active')  # active/completed/cancelled
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contract: {self.car} to {self.user.username}"
