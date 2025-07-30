from django.urls import path
from .views import (LoginView, 
                    ProfileView,
                    RegisterUserView, 
                    UpdateUserView,
                    DeleteUserView, 
                    ChangePermissionView,
                    CurrentUserView,
                    ResidentProfileListAPIView,
                    MaintenancePaymentListView,
                    LedgerEntryListView
                    )

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('update/', UpdateUserView.as_view(), name='update-user'),
    path('delete/', DeleteUserView.as_view(), name='delete-user'),
    path('permissions/<int:id>/', ChangePermissionView.as_view(), name='change-permissions'),
    path('residents/', ResidentProfileListAPIView.as_view(), name='resident-list'),
    path('maintenance-payments/', MaintenancePaymentListView.as_view(), name='maintenance-payment-list'),
    path("ledger-entries/", LedgerEntryListView.as_view(), name="ledger-entry-list"),
]
