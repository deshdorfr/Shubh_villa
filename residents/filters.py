# filters.py

from django_filters import rest_framework as filters
from .models import MaintenancePayment

class MaintenancePaymentFilter(filters.FilterSet):
    username = filters.CharFilter(field_name='resident__user__username', lookup_expr='icontains')
    month = filters.CharFilter(field_name='month', lookup_expr='iexact')
    year = filters.NumberFilter(field_name='year')

    class Meta:
        model = MaintenancePayment
        fields = ['month', 'year', 'username']
