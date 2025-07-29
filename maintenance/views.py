from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from residents.models import MaintenancePayment


class MaintenanceSummaryView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        year = request.GET.get('year')
        month = request.GET.get('month')

        now = timezone.now()
        if not year:
            year = now.year
        if not month:
            month = now.strftime("%B")

        queryset = MaintenancePayment.objects.filter(year=year)

        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0
        total_due = queryset.aggregate(total=Sum('due'))['total'] or 0

        month_queryset = queryset.filter(month=month)
        month_amount = month_queryset.aggregate(total=Sum('amount'))['total'] or 0
        month_due = month_queryset.aggregate(total=Sum('due'))['total'] or 0

        return Response({
            "filters": {
                "year": year,
                "month": month
            },
            "summary": {
                "totalAmount": total_amount,
                "totalDue": total_due,
                "monthTotalAmount": month_amount,
                "monthTotalDue": month_due,
            }
        })
