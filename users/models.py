from django.db import models
from django.contrib.auth.models import AbstractUser
from users.managers import CustomUserManager
# Create your models here.

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.TextField(max_length=15, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =  []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
