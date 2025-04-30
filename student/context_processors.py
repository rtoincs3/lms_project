from .models import StudentProfile

#  this function is use for all student info available in all html file of student
def student_context(request):
    if request.user.is_authenticated and hasattr(request.user, 'studentprofile'):
        return {'student': request.user.studentprofile}
    return {}