from django.contrib import admin
from .models import StudentProfile
from django import forms


# Register your models here.

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = "__all__"
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
        }

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id','full_name', 'user', 'department', 'samester', 'admission_date')
    search_fields = ('full_name', 'user__roll_number')
    form = StudentProfileForm

admin.site.register(StudentProfile, StudentProfileAdmin)