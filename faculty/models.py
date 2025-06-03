from django.db import models
from django.contrib.auth import get_user_model
from users.models import Department
from student.models import StudentProfile

# Create your models here.

CustomUser = get_user_model()

ROLE_CHOICES = (
    ('faculty', 'Faculty'),
    ('hod', 'HOD'),
    ('principal', 'Principal'),
)

def teacher_profile_upload_path(instance, filename):
    return f"teacher_profile/{instance.teacher_id}/{filename}"

class TeacherProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, blank=True, null=True)

    profile_picture = models.ImageField(upload_to=teacher_profile_upload_path, blank=True, null=True)

    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    information = models.TextField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    subject_specialization = models.CharField(max_length=100, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True)
    email = models.EmailField(null=True, blank=True, default="default@clg.com")
    experience_year = models.IntegerField(default=0)

    teacher_role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    # all fields to create teacher profile
    teacher_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128, default=3398)

    def save(self, *args, **kwargs):
        # if not user create user
        if not self.user:
            user = CustomUser.objects.create_user(
                username=self.teacher_id,
                teacher_id = self.teacher_id,
                password=self.password,
                user_type='teacher'
            )

            self.user = user
        super(TeacherProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name}"




def material_upload_path(instance, filename):
    return f"teacher_materials/{instance.teacher.teacher_id}/{filename}"


class TeacherMaterial(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=material_upload_path)
    upload_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # automatically set department if not 
        if not self.department:
            self.department = self.teacher.department
        super(TeacherMaterial, self).save(*args, **kwargs)





#  for time table
DAYS_OF_WEEK = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
]

class TimeTable(models.Model):
    department =  models.ForeignKey(Department, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)

    semester = models.IntegerField()
    subject_name = models.CharField(max_length=100)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.subject_name




# #######################################################################
# #######################################################################


class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture = models.ForeignKey(TimeTable, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=(('Present', 'Present'), ('Absent', 'Absent')))

    class Meta:
        unique_together = ('student', 'lecture', 'date')  # Optional but recommended

    def __str__(self):
        return self.student.full_name