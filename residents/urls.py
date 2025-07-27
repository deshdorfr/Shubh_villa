from django.urls import path
from .views import (LoginView, 
                    ProfileView,
                    RegisterUserView, 
                    UpdateUserView,
                    DeleteUserView, 
                    ChangePermissionView,
                    CurrentUserView
                    )

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('update/', UpdateUserView.as_view(), name='update-user'),
    path('delete/', DeleteUserView.as_view(), name='delete-user'),
    path('permissions/<int:id>/', ChangePermissionView.as_view(), name='change-permissions'),
]
