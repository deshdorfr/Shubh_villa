from django.contrib.auth.models import User
from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class ResidentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    villa_number = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.username} - Flat {self.villa_number}"
