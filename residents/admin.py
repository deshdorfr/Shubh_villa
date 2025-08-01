from django.contrib.auth.models import User
from residents.models import ResidentProfile, LedgerEntry
from .models import MaintenancePayment
from django.contrib import admin
from django import forms
from datetime import date
from django.db import models

admin.site.site_header = "Shubh Villa Society Administration"
admin.site.site_title = "Shubh Villa Admin Portal"
admin.site.index_title = "Welcome to Shubh Villa Admin Panel"

@admin.register(ResidentProfile)
class ResidentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'villa_number', 'phone', 'registration_date')
    search_fields = ('user__username', 'user__email', 'villa_number', 'phone')
    list_filter = ('villa_number',)


@admin.register(MaintenancePayment)
class MaintenancePaymentAdmin(admin.ModelAdmin):
    list_display = ('resident', 'month', 'year', 'amount', 'due', 'payment_date', 'status')
    list_filter = ('status', 'month')
    search_fields = ('resident__user__username', 'resident__villa_number')
    readonly_fields = ['due', 'year']
    sortable_by= ['due']

    change_list_template = "admin/maintenancepayment_changelist.html"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            qs = response.context_data['cl'].queryset
            total_amount = qs.aggregate(total=models.Sum('amount'))['total'] or 0
            total_due = qs.aggregate(total=models.Sum('due'))['total'] or 0

            extra_context = extra_context or {}
            extra_context['summary'] = {
                'total_amount': total_amount,
                'total_due': total_due,
            }
            response.context_data.update(extra_context)
        except (AttributeError, KeyError):
            pass

        return response
    
    
class LedgerEntryAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current = date.today().year
        self.fields["year"].choices = [(y, y) for y in range(current - 5, current + 6)]

class LedgerEntryAdmin(admin.ModelAdmin):
    form = LedgerEntryAdminForm
    list_display = ("note", "entry_type", "amount", "resident", "category", "payment_method", "month", "year", "date")
    list_filter = ("entry_type", "category", "payment_method", "month", "year", "date")
    search_fields = ("resident__user__username", "resident__villa_number", "note")

admin.site.register(LedgerEntry, LedgerEntryAdmin)
