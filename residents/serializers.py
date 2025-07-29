from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ResidentProfile
from .models import MaintenancePayment


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

# class ResidentProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer()

#     class Meta:
#         model = ResidentProfile
#         fields = ['user', 'villa_number', 'phone']
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    villa_number = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'villa_number']

    def create(self, validated_data):
        villa_number = validated_data.pop('villa_number')
        password = validated_data.pop('password')

        # Create user
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Create profile
        ResidentProfile.objects.create(user=user, villa_number=villa_number)

        return user


    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

class ChangePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_staff', 'is_superuser']
        
        
class ResidentProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ResidentProfile
        fields = ['id', 'username', 'name', 'email', 'villa_number', 'phone', 'registration_date']
        

# serializers.py
class MaintenancePaymentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='resident.user.username', read_only=True)
    villa_number = serializers.CharField(source='resident.villa_number', read_only=True)

    class Meta:
        model = MaintenancePayment
        fields = ['id', 'username', 'villa_number', 'amount', 'due', 'payment_date', 'month', 'year', 'status', 'payment_method']

