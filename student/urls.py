from django.urls import path
from . import views


urlpatterns = [
    path("", views.student_dashboard, name="student_dashboard"),
    path("login/", views.student_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path("profile/", views.student_profile, name="student_profile"),
    path("available-exams", views.available_exams, name="available_exams"),
    path("start-exam/<int:exam_id>", views.start_exam, name="start_exam"),
    path("student_material/", views.student_material, name="student_material"),
    path("time-table/", views.time_table, name="time_table"),
]
