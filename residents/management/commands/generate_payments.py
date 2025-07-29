from django.core.management.base import BaseCommand
from django.utils import timezone
from residents.models import ResidentProfile, MaintenancePayment
import calendar

class Command(BaseCommand):
    help = 'Generate missing maintenance payments for residents'

    def handle(self, *args, **kwargs):
        current_year = timezone.now().year
        current_month = timezone.now().month

        for resident in ResidentProfile.objects.all():
            reg_date = resident.registration_date
            start_year = reg_date.year
            start_month = reg_date.month

            for year in range(start_year, current_year + 1):
                month_range = range(1, 13)
                if year == start_year:
                    month_range = range(start_month, 13)
                if year == current_year:
                    month_range = range(start_month if year == start_year else 1, current_month + 1)

                for month in month_range:
                    month_name = calendar.month_name[month]

                    if not MaintenancePayment.objects.filter(resident=resident, month=month_name).exists():
                        MaintenancePayment.objects.create(
                            resident=resident,
                            amount=1000.00,  # Set default amount here
                            month=month_name,
                            status='pending'
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f"Created payment for {resident.user.username} - {month_name} {year}"
                        ))
