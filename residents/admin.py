import datetime
from django.contrib.auth.models import User
from residents.models import ResidentProfile, LedgerEntry
from .models import MaintenancePayment
from django.contrib import admin
from django import forms
from datetime import date
from django.db import models
from django.db.models import Sum

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
    list_filter = ('status', 'month', 'year')
    search_fields = ('resident__user__username', 'resident__villa_number')
    readonly_fields = ['due', 'year']
    sortable_by = ['due']

    change_list_template = "admin/maintenancepayment_changelist.html"

    def changelist_view(self, request, extra_context=None):
        today = datetime.date.today()
        current_year = today.year
        current_month = today.strftime("%B")  # e.g. "August"

        # make a mutable copy of GET
        q = request.GET.copy()
        changed = False

        # Django admin filters use `field__exact`
        if "year__exact" not in q:
            q["year__exact"] = str(current_year)
            changed = True

        if "month__exact" not in q:
            q["month__exact"] = current_month
            changed = True

        if changed:
            request.GET = q
            request.META['QUERY_STRING'] = q.urlencode()

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

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    form = LedgerEntryAdminForm
    change_list_template = "admin/ledgerentry_changelist.html"

    list_display = (
        "note",
        "entry_type",
        "amount",
        "resident",
        "category",
        "payment_method",
        "month",
        "year",
        "date",
    )
    list_filter = (
        "entry_type",
        "category",
        "payment_method",
        "month",
        "year",
        "date",
    )
    search_fields = (
        "resident__user__username",
        "resident__villa_number",
        "note",
    )

    def changelist_view(self, request, extra_context=None):
        today = datetime.date.today()
        current_year = today.year
        current_month = today.strftime("%B")  # if month is stored as string ("August")
        # 👉 If stored as integer (1–12) instead, use:  current_month = today.month

        # ✅ Inject defaults only if user hasn’t chosen them
        q = request.GET.copy()
        changed = False

        if "year__exact" not in q:
            q["year__exact"] = str(current_year)
            changed = True

        if "month__exact" not in q:
            q["month__exact"] = current_month
            changed = True

        if changed:
            request.GET = q
            request.META["QUERY_STRING"] = q.urlencode()

        response = super().changelist_view(request, extra_context=extra_context)

        try:
            queryset = response.context_data["cl"].queryset
            totals = queryset.values("entry_type").annotate(total=Sum("amount")).order_by("entry_type")
            summary = {
                "total_credit": 0,
                "total_debit": 0,
            }
            for t in totals:
                if t["entry_type"] == "credit":
                    summary["total_credit"] = t["total"]
                elif t["entry_type"] == "debit":
                    summary["total_debit"] = t["total"]

            response.context_data["summary"] = summary
        except (AttributeError, KeyError):
            pass

        return response
