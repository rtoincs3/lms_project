from django.contrib import admin
from .models import TeacherProfile, TeacherMaterial, TimeTable, Attendance
from django import forms


# Register your models here.

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = "__all__"
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("id","full_name", "user", "teacher_role", "department", "joining_date")
    search_fields = ("full_name", "user__teacher_id")
    form = TeacherProfileForm

class TeacherMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", 'get_teacher_name', "get_department_name", 'upload_at')
    search_fields = ("title", "teacher__teacher_id")


    def get_teacher_name(self, obj):
        return obj.teacher.full_name
    
    get_teacher_name.short_description = "Teacher Name"

    def get_department_name(self, obj):
        return obj.department.name
    get_department_name.short_description = "Department Name"


class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('department', 'semester', 'teacher', 'subject_name', 'day', 'start_time', 'end_time')
    search_fields = ("subject_name", "teacher__full_name", "day")



class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'lecture', 'date', 'status')


admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(TeacherMaterial, TeacherMaterialAdmin)
admin.site.register(TimeTable, TimeTableAdmin)
admin.site.register(Attendance, AttendanceAdmin)