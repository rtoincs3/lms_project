from .models import TeacherProfile


# this function is used for teacher profile available all html file that in teacher
def teacher_context(request):
    if request.user.is_authenticated and hasattr(request.user, "teacherprofile"):
        return {"teacher": request.user.teacherprofile}
    return {}