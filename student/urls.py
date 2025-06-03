from django.urls import path
from . import views

app_name = "student"

urlpatterns = [
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("", views.student_login, name='login'),
    path('student/logout/', views.user_logout, name='logout'),
    path("student/profile/", views.student_profile, name="student_profile"),
    path("student/available-exams", views.available_exams, name="available_exams"),
    path("student/start-exam/<int:exam_id>", views.start_exam, name="start_exam"),
    path("student/student_material/", views.student_material, name="student_material"),
    path("student/time-table/", views.time_table, name="time_table"),
    path("student/show-attendance/", views.student_show_attendance, name="student_show_attendance"),
    path("student/attendance-percentage/", views.attendance_percentage, name="attendance_percentage"),
]
