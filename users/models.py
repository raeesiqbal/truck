from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


ACCOUNT_TYPE = (
    ("school", "School"),
    ("grocery store", "Grocery Store"),
    ("volunteer", "Volunteer"),
)

ACCOUNT_Status = (
    ("approved", "Approved"),
    ("pending", "Pending"),
    ("rejected", "Rejected"),
)

 
class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    username = None
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"
