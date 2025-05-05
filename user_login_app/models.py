from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.http import HttpRequest


class UserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password, confirm_password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")
        if len(username) < 3 or len(username) > 30:
            raise ValueError("Username must be between 3 and 30 characters in length.")
        if len(password) < 8 or len(password) > 128:
            raise ValueError("Password must be a minimum of 8 characters in length and no more than 128.")
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        if self.model.objects.filter(email=email).exists():
            raise ValueError("Email is already in use.")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields  # <-- This works now because of the new argument
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            confirm_password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    password = models.CharField(max_length=128)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'  # <-- If you want username login, otherwise leave as 'email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name',]

    def __str__(self):
        return self.username  # <-- You had `return self.email`, but now it's username-based
    

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    blocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blocked: {self.ip_address}"
    
def is_banned(request):
    ip = request.META.get('REMOTE_ADDR')
    return BlockedIP.objects.filter(ip_address=ip).exists()


