# students/models.py

from django.db import models
from django.contrib.auth import get_user_model
from users.models import Department

CustomUser = get_user_model()

def student_profile_upload_path(instance, filename):
    return f"student_profiles/{instance.user.roll_number}/{filename}"

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, blank=True, null=True)

    profile_picture = models.ImageField(upload_to=student_profile_upload_path, blank=True, null=True)
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.IntegerField()
    samester = models.IntegerField(null=True, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)

    # Add fields needed to create User
    roll_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128, default=1101)  # store temporary password here

    def save(self, *args, **kwargs):
        # If user not assigned yet, create it
        if not self.user:
            user = CustomUser.objects.create_user(
                username=self.roll_number,
                roll_number=self.roll_number,
                password=self.password,
                user_type='student'
            )
            self.user = user
        super(StudentProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name}"
