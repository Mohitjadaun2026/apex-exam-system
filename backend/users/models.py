from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (

        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"


class Student(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    class_name = models.CharField(max_length=20)

    roll_number = models.CharField(max_length=20)

    xp = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email


class Teacher(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    subject = models.CharField(max_length=100)

    assigned_classes = models.CharField(max_length=100)

    def __str__(self):
        return self.user.email
    
