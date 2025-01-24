from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    is_company = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    email = models.CharField(max_length=100, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # Ensure that a user cannot be both a company and a customer
        if self.is_company and self.is_customer:
            raise ValueError(
                'A user cannot be both a company and a customer')
        # Ensure that either is_company or is_customer is True
        if not (self.is_company or self.is_customer):
            raise ValueError(
                'Either is_company or is_customer must be True')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
        


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    
    date_of_birth = models.DateField()
    def __str__(self):
        return f'{self.user.id} - {self.user.username} - {self.date_of_birth} customer'


class Company(models.Model):
    FIELD_CHOICES = [
        ('Air Conditioner', 'Air Conditioner'),
        ('All in One', 'All in One'),
        ('Carpentry', 'Carpentry'),
        ('Electricity', 'Electricity'),
        ('Gardening', 'Gardening'),
        ('Home Machines', 'Home Machines'),
        ('House Keeping', 'House Keeping'),
        ('Interior Design', 'Interior Design'),
        ('Locks', 'Locks'),
        ('Painting', 'Painting'),
        ('Plumbing', 'Plumbing'),
        ('Water Heaters', 'Water Heaters'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True
    )
    field = models.CharField(max_length=70, choices=FIELD_CHOICES, blank=False, null=False)
    rating = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(0)], default=0
    )

    def __str__(self):
        return f"{self.user.id} - {self.user.username} (Company - {self.field})"