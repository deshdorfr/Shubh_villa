from django.contrib.auth.models import User
from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from decimal import Decimal
from maintenance import envVar


class ResidentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    villa_number = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    registration_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - Villa No- {self.villa_number}"
    

from django.db import models
from django.utils import timezone
from decimal import Decimal
from maintenance import envVar  # Make sure this import works relative to your project structure

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
    due = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_date = models.DateField(default=timezone.now)
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year = models.IntegerField(default=timezone.now().year)  # <-- added year field
    status = models.CharField(max_length=20, choices=[
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('failed', 'Failed')
    ], default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Ensure year is set
        if not self.year:
            self.year = timezone.now().year

        # Automatically calculate the due amount before saving
        self.due = Decimal(envVar.base_maintenance) - self.amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.resident.user.username} - {self.month} {self.year} - ₹{self.amount} - Due ₹{self.due} - {self.status}"
