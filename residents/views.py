from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from .serializers import UserDetailSerializer
from .models import ResidentProfile
from .serializers import ResidentProfileSerializer, RegisterSerializer, UpdateUserSerializer, ChangePermissionSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.decorators import api_view
from django.db.models import Sum
from django.utils import timezone
from .models import MaintenancePayment, LedgerEntry

from .serializers import MaintenancePaymentSerializer, LedgerEntrySerializer
from .filters import MaintenancePaymentFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.text import capfirst


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)


class LoginView(APIView):

    @swagger_auto_schema(
        operation_description="Resident login with username and password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: openapi.Response(description="Auth token")},
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=400)

    
class ProfileView(generics.RetrieveAPIView):
    serializer_class = ResidentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return ResidentProfile.objects.get(user=self.request.user)
    
    
    
# Register
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# Update
class UpdateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# Delete
class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({'message': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)

# Change permissions (admin only)
class ChangePermissionView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePermissionSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'
    
    
class ResidentProfileListAPIView(generics.ListAPIView):
    queryset = ResidentProfile.objects.all()
    serializer_class = ResidentProfileSerializer  
    
class MaintenancePaymentListView(generics.ListAPIView):
    queryset = MaintenancePayment.objects.all().order_by("-due").select_related('resident__user')
    serializer_class = MaintenancePaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MaintenancePaymentFilter
    


class LedgerEntryListView(generics.ListAPIView):
    """
    GET /api/ledger-entries/?entry_type=credit|debit&month=July|7&year=2025
    All filters are optional; combine as needed.
    """
    serializer_class = LedgerEntrySerializer

    def get_queryset(self):
        qs = LedgerEntry.objects.select_related("resident__user").all()

        entry_type = self.request.query_params.get("entry_type")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")

        # Filter by entry_type (only allow 'credit' or 'debit')
        if entry_type and entry_type.lower() in {"credit", "debit"}:
            qs = qs.filter(entry_type=entry_type.lower())

        # Filter by year
        if year and year.isdigit():
            qs = qs.filter(year=int(year))

        # Filter by month: accept name (case-insensitive) or numeric 1-12
        if month:
            month_val = month.strip()
            if month_val.isdigit():  # numeric month
                num = int(month_val)
                if 1 <= num <= 12:
                    # Map to full month name stored in choices
                    MONTHS = [
                        "January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"
                    ]
                    qs = qs.filter(month=MONTHS[num - 1])
            else:
                # Accept case-insensitive month name
                qs = qs.filter(month__iexact=capfirst(month_val))

        return qs
