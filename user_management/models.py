from django.db import models
from django.contrib.auth.hashers import make_password 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email,password):
        user = self.model(email=email,password=make_password(password))
        user.save()
        return user

    def create_superuser(self, email,password):
        user = self.create_user(email=email,password=password)
        user.is_superuser = True
        user.is_staff = True
        user.auth_method = "MANUAL"
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # field used for login
    REQUIRED_FIELDS = []  # fields required when creating superuser

    def __str__(self):
        return self.email
    
    class Meta:
        app_label = 'user_management'
