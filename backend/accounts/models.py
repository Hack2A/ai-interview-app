from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .utils import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)

    is_onboard = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    objects = UserManager()

    def __str__(self):
        return self.email
