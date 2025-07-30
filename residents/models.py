from django.contrib.auth.models import User
from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from decimal import Decimal
from maintenance import envVar

from django.core.validators import MinValueValidator
from datetime import date


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
    


class LedgerEntry(models.Model):
    """
    General ledger table for both debits (money out) and credits (money in).
    Amount is always positive; direction is defined by entry_type.
    """

    ENTRY_TYPES = (
        ("debit", "Debit"),    # Money OUT (e.g., expenses, payouts)
        ("credit", "Credit"),  # Money IN  (e.g., maintenance, donations)
    )

    MONTH_CHOICES = [
        ("January", "January"),
        ("February", "February"),
        ("March", "March"),
        ("April", "April"),
        ("May", "May"),
        ("June", "June"),
        ("July", "July"),
        ("August", "August"),
        ("September", "September"),
        ("October", "October"),
        ("November", "November"),
        ("December", "December"),
    ]

    # Build a reasonable rolling set of years for the dropdown
    _CURRENT_YEAR = date.today().year
    YEAR_CHOICES = [(y, y) for y in range(_CURRENT_YEAR - 5, _CURRENT_YEAR + 6)]

    resident = models.ForeignKey(
        'ResidentProfile',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ledger_entries'
    )

    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Positive amount (₹). Direction is set by entry_type."
    )

    # ▼ Dropdowns
    month = models.CharField(max_length=20, choices=MONTH_CHOICES, blank=True, null=True)
    year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, default=_CURRENT_YEAR)

    category = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="e.g., maintenance, donation, security, utilities, repairs"
    )
    payment_method = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="e.g., UPI, Cash, Card, Bank, Cheque"
    )
    note = models.TextField(blank=True, null=True)

    date = models.DateField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Ledger entry"
        verbose_name_plural = "Ledger entries"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["entry_type"]),
            models.Index(fields=["year", "month"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        who = self.resident.user.username if self.resident and getattr(self.resident, "user", None) else "N/A"
        ym = f"{self.month or ''} {self.year or ''}".strip()
        return f"{self.entry_type.title()} | {who} | ₹{self.amount} | {ym or self.date}"

    @property
    def signed_amount(self) -> Decimal:
        """Negative for debits (out), positive for credits (in)."""
        return self.amount if self.entry_type == "credit" else -self.amount

