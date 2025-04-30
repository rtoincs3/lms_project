from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin')
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    roll_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    teacher_id = models.CharField(max_length=20, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        if self.user_type == 'student' and self.roll_number:
            self.username = self.roll_number
        elif self.user_type == 'teacher' and self.teacher_id:
            self.username = self.teacher_id
        super().save(*args, **kwargs)


    def __str__(self):
        return self.username
    


#  Department for students and teacher
class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name