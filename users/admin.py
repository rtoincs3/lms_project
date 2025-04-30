from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # show in admin list view
    list_display = ('username', 'email', 'user_type', 'roll_number', 'teacher_id', 'is_staff')

    # add our custom field here
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'roll_number', 'teacher_id')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'roll_number', 'teacher_id')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department)