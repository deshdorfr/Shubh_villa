from django.contrib.auth.models import User
from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class ResidentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    villa_number = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    registration_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - Villa No- {self.villa_number}"
    

class MaintenancePayment(models.Model):
    MONTH_CHOICES = [
            ('January', 'January'),
            ('February', 'February'),
            ('March', 'March'),
            ('April', 'April'),
            ('May', 'May'),
            ('June', 'June'),
            ('July', 'July'),
            ('August', 'August'),
            ('September', 'September'),
            ('October', 'October'),
            ('November', 'November'),
            ('December', 'December'),
        ]
    resident = models.ForeignKey('ResidentProfile', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    status = models.CharField(max_length=20, choices=[
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('failed', 'Failed')
    ], default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # e.g., "UPI", "Credit Card"

    def __str__(self):
        return f"{self.resident.user.username} - {self.month} - ₹{self.amount} - {self.status}"
