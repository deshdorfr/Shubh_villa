from django.contrib import admin
from django.urls import path, include
from .views import MaintenanceSummaryView

urlpatterns = [
    path('maintenance-summary/', MaintenanceSummaryView.as_view(), name='maintenance-summary'),
    # path('admin/', admin.site.urls),
    # path('residents/', include('residents.urls')),
    # path('maintenance/', include('maintenance.urls')),
    # # path('events/', include('events.urls')),
    # # path('complaints/', include('complaints.urls')),
]