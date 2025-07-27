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

