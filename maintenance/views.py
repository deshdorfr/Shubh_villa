from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from residents.models import MaintenancePayment, LedgerEntry
from decimal import Decimal


class MaintenanceSummaryView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        year_param = request.GET.get('year')
        month = request.GET.get('month')

        now = timezone.now()
        year = int(year_param) if year_param else now.year
        if not month:
            month = now.strftime("%B")

        # -------- Year-level aggregates --------
        payments_qs = MaintenancePayment.objects.filter(year=year)
        payments_total = payments_qs.aggregate(sum=Sum('amount'))['sum'] or Decimal('0')

        total_due = payments_qs.aggregate(sum=Sum('due'))['sum'] or Decimal('0')

        credits_qs = LedgerEntry.objects.filter(year=year, entry_type='credit')
        debits_qs = LedgerEntry.objects.filter(year=year, entry_type='debit')

        credit_total = credits_qs.aggregate(sum=Sum('amount'))['sum'] or Decimal('0')
        debit_total = debits_qs.aggregate(sum=Sum('amount'))['sum'] or Decimal('0')

        total_amount = payments_total + credit_total - debit_total

        # -------- Month-level aggregates --------
        payments_month_qs = payments_qs.filter(month=month)
        payments_month_total = payments_month_qs.aggregate(sum=Sum('amount'))['sum'] or Decimal('0')

        month_due = payments_month_qs.aggregate(sum=Sum('due'))['sum'] or Decimal('0')

        credit_month_total = credits_qs.filter(month=month).aggregate(sum=Sum('amount'))['sum'] or Decimal('0')
        debit_month_total = debits_qs.filter(month=month).aggregate(sum=Sum('amount'))['sum'] or Decimal('0')

        month_total_amount = payments_month_total + credit_month_total - debit_month_total

        return Response({
            "filters": {
                "year": year,
                "month": month
            },
            "summary": {
                "totalAmount": total_amount,
                "totalDue": total_due,
                "monthTotalAmount": month_total_amount,
                "monthTotalDue": month_due,
                "breakdown": {
                    "year": {
                        "paymentsTotal": payments_total,
                        "creditTotal": credit_total,
                        "debitTotal": debit_total,
                    },
                    "month": {
                        "paymentsTotal": payments_month_total,
                        "creditTotal": credit_month_total,
                        "debitTotal": debit_month_total,
                    }
                }
            }
        })
