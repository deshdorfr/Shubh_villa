import datetime
from django.contrib.auth.models import User
from residents.models import ResidentProfile, LedgerEntry
from .models import MaintenancePayment
from django.contrib import admin
from django import forms
from datetime import date
from django.db import models
from django.db.models import Sum
from decimal import Decimal
from django.db import models
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from maintenance import envVar


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
    actions = ['export_as_pdf']  # <-- ✅ added action

    change_list_template = "admin/maintenancepayment_changelist.html"

    def changelist_view(self, request, extra_context=None):
        today = datetime.date.today()
        current_year = today.year
        current_month = today.strftime("%B")  # "August", matches MONTH_CHOICES

        # Apply default only if no filters at all
        if not request.GET:  
            q = request.GET.copy()
            q["year__exact"] = str(current_year)
            q["month__exact"] = current_month
            request.GET = q
            request.META["QUERY_STRING"] = q.urlencode()

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

    # ✅ Custom action to export PDF
    def export_as_pdf(self, request, queryset):
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="maintenance_payments.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # ✅ Title
        p.setFont("Helvetica-Bold", 14)
        p.drawString(260, height - 40, "Shubh Villa")
        p.drawString(200, height - 60, "Maintenance Payments Report")

        # Table Data
        data = [["Resident", "Month", "Year", "Month Amount", "Month Due","Total Due", "Status", "Payment Date"]]
        queryset = queryset.order_by("resident__villa_number")
        for obj in queryset:
            
            total_due = (
                MaintenancePayment.objects.filter(resident=obj.resident)
                .aggregate(total_due=models.Sum("due"))["total_due"]
                or 0
            )
            
            row = [
                str(obj.resident),
                obj.month,
                str(obj.year),
                f"Rs {obj.amount}",
                f"Rs {obj.due}",
                str(total_due),
                obj.status,
                obj.payment_date.strftime("%d-%m-%Y"),
            ]
            data.append(row)

        # Add summary row
        total_amount = sum([obj.amount for obj in queryset])
        total_due = sum([obj.due or Decimal(0) for obj in queryset])
        data.append(["", "", f"Total Rs {total_amount}","", "", f"Total Due Rs {total_due}", "", ""])

        # Create table
        table = Table(data, colWidths=[90, 60, 50, 80, 80, 70, 80])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ])

        # Highlight rows with dues
        for i, obj in enumerate(queryset, start=1):  # +1 because header row
            total_due = (
                MaintenancePayment.objects.filter(resident=obj.resident)
                .aggregate(total_due=models.Sum("due"))["total_due"]
                or 0
            )
            if total_due and total_due > envVar.base_maintenance:
                style.add('TEXTCOLOR', (0, i), (-1, i), colors.red) 
            elif obj.due and obj.due > 0:
                style.add('BACKGROUND', (0, i), (-1, i), colors.yellow)
                style.add('TEXTCOLOR', (0, i), (-1, i), colors.black)               
            else:
                style.add('BACKGROUND', (0, i), (-1, i), colors.lightgreen)
                style.add('TEXTCOLOR', (0, i), (-1, i), colors.black)

        # Highlight summary row
        style.add('BACKGROUND', (0, len(data)-1), (-1, len(data)-1), colors.lightblue)
        style.add('TEXTCOLOR', (0, len(data)-1), (-1, len(data)-1), colors.black)

        table.setStyle(style)

        # Draw table
        table.wrapOn(p, width, height)
        table_height = 400
        table.drawOn(p, 30, height - 100 - (20 * len(data)))

        p.save()
        return response

    export_as_pdf.short_description = "Export selected payments to PDF"
    
    
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
