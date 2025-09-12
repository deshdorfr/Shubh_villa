from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ResidentProfile
from .models import MaintenancePayment, LedgerEntry
from django.db import models


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
    username = serializers.SerializerMethodField()
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ResidentProfile
        fields = ['id', 'username', 'name', 'email', 'villa_number', 'phone', 'registration_date']

    def get_username(self, obj):
        user = getattr(obj, 'user', None)  # Use obj.user directly, not obj.resident.user
        if user:
            first = user.first_name or ''
            last = user.last_name or ''
            full_name = f"{first} {last}".strip()
            if full_name:
                return full_name
            return user.username
        return 'N/A'
        

class MaintenancePaymentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    villa_number = serializers.CharField(source='resident.villa_number', read_only=True)
    total_due = serializers.SerializerMethodField()

    class Meta:
        model = MaintenancePayment
        fields = [
            'id',
            'username',
            'villa_number',
            'amount',
            'due',
            'payment_date',
            'month',
            'year',
            'status',
            'payment_method',
            'total_due',
        ]

    def get_username(self, obj):
        user = getattr(obj.resident, 'user', None)
        if user:
            first = user.first_name or ''
            last = user.last_name or ''
            full_name = f"{first} {last}".strip()
            if full_name:
                return full_name
            return user.username
        return 'N/A'

    def get_total_due(self, obj):
        """
        Returns the total due for all MaintenancePayments of the same resident.
        """
        return (
            MaintenancePayment.objects.filter(resident=obj.resident)
            .aggregate(total_due=models.Sum('due'))['total_due']
            or 0
        )
        


class LedgerEntrySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    villa_number = serializers.CharField(source="resident.villa_number", read_only=True)

    class Meta:
        model = LedgerEntry
        fields = [
            "id",
            "entry_type",
            "amount",
            "month",
            "year",
            "category",
            "payment_method",
            "note",
            "date",
            "created_at",
            "updated_at",
            "full_name",
            "villa_number",
        ]

    def get_full_name(self, obj):
        user = obj.resident.user
        if user.first_name or user.last_name:
            return f"{user.first_name} {user.last_name}".strip()
        return user.username


