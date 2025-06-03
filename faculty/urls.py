from django.urls import path
from . import views

app_name = "faculty"

urlpatterns = [
    path("", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacherlogin/", views.teacher_login, name="teacher_login"),
    path("teacherlogout/", views.teacher_logout, name="teacher_logout"),
    path("teacher-profile/", views.teacher_profile, name="teacher_profile"),
    path("createexam/", views.create_exam, name="create_exam"),
    path("manageexam/", views.manage_exam, name="manage_exam"),
    path("add-question/<int:exam_id>", views.add_question, name="add_question"),
    path("manageexam/<int:exam_id>", views.update_exam, name="update_exam"),
    path("manage-question/<int:question_id>", views.update_question, name="update_question"),
    path("exam/<int:exam_id>/add-question", views.add_question, name="add_question"),
    path("exam/<int:exam_id>/delete-question/<int:question_id>", views.delete_question, name="delete_question"),
    path("manage_material/", views.manage_material, name="manage_material"),
    path("material-delete/<int:material_id>", views.delete_material, name="delete_material"),
    path("manage-timetable/", views.manage_timetable_semester_list, name="manage_timetable"),
    path("manage-timetable/<int:semester>", views.manage_timetable_by_semester, name="manage_timetable_semester"),
    path("show-timetable/", views.show_timetable, name="show_timetable"),
    path("attendance-timetable/", views.attendance_timetable, name="attendance_timetable"),
    path("take-attendance/<int:lecture_id>/", views.take_attendance, name="take_attendance"),
    path('attendance/', views.attendance_semester_list, name='attendance_semester_list'),
    path('attendance/<int:semester>/', views.attendance_by_semester, name='show_attendance'),

]