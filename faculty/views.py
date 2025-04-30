from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from users.models import CustomUser
from django.contrib.auth.decorators import login_required
from .models import TeacherProfile, TeacherMaterial, TimeTable, Attendance
from exam.models import Exam, Question, Option
from student.models import StudentProfile
from django.http import Http404
from django.contrib import messages
from django.utils.timezone import make_aware
from django.utils import timezone
from datetime import datetime, date


# Create your views here.


@login_required
def teacher_dashboard(request):
    teacher_info = None
    if request.user.is_authenticated:
        try:
            teacher_info = TeacherProfile.objects.get(user=request.user)
        except TeacherProfile.DoesNotExist:
            teacher_info = None
    return render(request, "faculty/teacher_dashboard.html", {'teacher_info': teacher_info})

@login_required
def teacher_profile(request):
    teacher_info = None
    
    # get teacher 
    if request.user.is_authenticated:
        try:
            teacher_info = TeacherProfile.objects.get(user=request.user)
        except TeacherProfile.DoesNotExist:
            teacher_info = None
    
    return render(request, "faculty/teacher_profile.html", {'teacher_info': teacher_info})


def teacher_login(request):
    if request.method == "POST":
        teacher_id = request.POST.get('teacher_id')
        password = request.POST.get('password')


        try:
            #  Find by teacher id
            user = CustomUser.objects.get(teacher_id=teacher_id, user_type='teacher')
        
        except CustomUser.DoesNotExist:
            user = None

        if user is not None:
            # authenticate user
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect("teacher_dashboard")
            else:
                return render(request,"faculty/teacher_login.html")
        else:
            return render(request,"faculty/teacher_login.html")
    return  render(request,"faculty/teacher_login.html")


def teacher_logout(request):

    logout(request)
    return redirect("teacher_login")


@login_required
def create_exam(request):
    # get teacher profile
    teacher = TeacherProfile.objects.get(user=request.user)

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get("description")
        samester = request.POST.get("semester")
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        duration_minutes = request.POST.get('duration_minutes')


        # Now create Exam
        exam = Exam.objects.create(
            title=title,
            description=description,
            teacher=teacher,
            department=teacher.department,
            samester=samester,
            start_time=start_time,
            end_time=end_time,
            duration_miniutes=duration_minutes,

        )

        return redirect('add_question', exam_id=exam.id)



    return render(request, "faculty/teacher_exam_create.html")
    

@login_required
def add_question(request, exam_id):
    # get the exam with exam_id


    exam = get_object_or_404(Exam, id=exam_id)

    # check if current teacher created exam or not
    if request.user !=exam.teacher.user:
        raise Http404("You are not authorized to add questions")
    
    if request.method == "POST":
        question_text = request.POST.get("question_text")
        marks = request.POST.get('marks')

        question = Question.objects.create(
            exam=exam,
            text=question_text,
            marks=marks
        )

        # now for options

        option_texts = request.POST.getlist('option_texts')
        correct_option = request.POST.get('correct_option')


        for idx, option_text in enumerate(option_texts):
            is_correct = (str(idx) == correct_option)

            Option.objects.create(
                question=question,
                text=option_text,
                is_correct=is_correct
            )

            return redirect('add_question', exam_id=exam.id)
        
        

    
    return render(request, "faculty/teacher_add_question.html")


@login_required
def manage_exam(request):
    exams = Exam.objects.all()

    return render(request, 'faculty/teacher_manage_exam.html', {'exams': exams})


@login_required
def update_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam).prefetch_related("Options")

    if request.method == "POST":
        try:
            #  ------------------- UPDATE EXAM INFO --------------------------------
            exam.title = request.POST.get('exam_title')
            exam.description = request.POST.get('description')
            exam.samester = request.POST.get('exam_samester')
            exam.duration_miniutes = request.POST.get('exam_duration')
            exam.start_time = request.POST.get('start_time')
            exam.end_time = request.POST.get('end_time')
            exam.save()
            messages.success(request, "Exam Info Update Succesfully")

        except Exception as e:
            messages.error(request, f"Error Occured {e}")

    context = {
        'exam': exam,
        'questions': questions
    }
    return render(request, "faculty/teacher_update_exam.html", context)


@login_required
def update_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == "POST":
        try:
            question.text = request.POST.get(f"q_text_{question.id}")
            question.marks = request.POST.get(f"q_marks_{question.id}")
            question.save()

            correct_option_id = request.POST.get(f"q_correct_{question.id}")
            for option in question.Options.all():
                option_text = request.POST.get(f"q_option_{question.id}_{option.id}")
                option.text = option_text
                option.is_correct = (str(option.id) == correct_option_id)
                option.save()
            
            messages.success(request, "Question and options updated successfully!")

        except Exception as e:
            messages.error(request, "Error Occured {e}")
    
    return redirect("update_exam", exam_id=question.exam_id)



@login_required
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == "POST":
        q_text = request.POST.get("question_text")
        marks = request.POST.get("marks")
        options = request.POST.getlist("options")
        correct_index = request.POST.get("correct_option")

        if not options or len(options) < 2:
            messages.error(request, "Please provide at least two options.")
            return redirect("update_exam", exam_id=exam.id)

        if correct_index is None:
            messages.error(request, "Please select the correct option.")
            return redirect("update_exam", exam_id=exam.id)

        correct_index = int(correct_index)

        question = Question.objects.create(
            exam=exam,
            text=q_text,
            marks=marks
        )

        for idx, opt_text in enumerate(options):
            Option.objects.create(
                question=question,
                text=opt_text.strip(),
                is_correct=(idx == correct_index)
            )

        messages.success(request, "Question Added Successfully")
        return redirect("update_exam", exam_id=exam.id)

    return redirect("update_exam", exam_id=exam.id)

@login_required
def delete_question(request, exam_id, question_id):
    # Retrieve the exam and question
    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id, exam=exam)

    # # Debugging to print user and teacher info
    # print(f"Exam Teacher: {exam.teacher}")
    # print(f"Logged-in User: {request.user}")
    # print(f"Exam Teacher ID: {exam.teacher.id}")
    # print(f"Logged-in User ID: {request.user.id}")
    print(f"exam teacher user -- {exam.teacher.user}")
    print(f"request user -- {request.user}")

    # Check if the current user is the teacher of the exam
    if exam.teacher.user != request.user:  # Compare user IDs
        messages.error(request, "You don't have permission to delete this question")
        return redirect("update_exam", exam_id=exam.id)

    # Delete the question and all related options (because of on_delete=models.CASCADE)
    question.delete()

    messages.success(request, "Question deleted successfully")
    return redirect("update_exam", exam_id=exam.id)


@login_required
def manage_material(request):
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    materials = TeacherMaterial.objects.filter(department=teacher_profile.department)

    if request.method == "POST":
        title = request.POST.get("material_title")
        file = request.FILES.get("material_file")

        # now upload
        if title and file:
            TeacherMaterial.objects.create(
                teacher=teacher_profile,
                department=teacher_profile.department,
                title=title,
                file=file
            )

            messages.success(request, "Material Create Succesfully")
            return redirect("manage_material")

    return render(request, "faculty/teacher_manage_materials.html", {'materials': materials})

@login_required
def delete_material(request, material_id):

    material = get_object_or_404(TeacherMaterial, id=material_id)

    # check if current user is a teacher of this material
    if material.teacher.user != request.user:   # compare user IDs
        messages.error(request, "You don't have permission to delete this question")
        return redirect("manage_material")
    
    # delete 
    material.delete()
    messages.success(request, "Material deleted successfully")
    return redirect("manage_material")



# ########################################################
#########################################################
@login_required
def manage_timetable_semester_list(request):
    teacher = get_object_or_404(TeacherProfile, user=request.user)

    if teacher.teacher_role not in ["Principal", "hod"]:
        return redirect("show_timetable")
    
    semester = TimeTable.objects.filter(department=teacher.department).values_list('semester', flat=True).distinct()

    return render(request, "faculty/teacher_manage_timetable_semester_list.html", {'semester': semester})



@login_required
def manage_timetable_by_semester(request, semester):
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    # List of days
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    department = teacher_profile.department
    user_role = teacher_profile.teacher_role

    # Ensure the semester is a valid value before continuing
    if not semester:
        messages.error(request, "Invalid semester provided!")
        return redirect("manage_timetable_semester_list")

    if request.method == "POST":
        timetable = TimeTable.objects.filter(semester=semester, teacher__department=department).order_by('day', 'start_time')

        for lecture in timetable:
            lecture.subject_name = request.POST.get(f"subject_name_{lecture.id}", lecture.subject_name)
            teacher_id = request.POST.get(f"teacher_{lecture.id}")
            if teacher_id:
                lecture.teacher_id = teacher_id
            lecture.semester = request.POST.get(f"semester_{lecture.id}", lecture.semester)
            lecture.start_time = request.POST.get(f"start_time_{lecture.id}", lecture.start_time)
            lecture.end_time = request.POST.get(f"end_time_{lecture.id}", lecture.end_time)
            lecture.save()

        day = request.POST.get("add_day")
        new_subject = request.POST.get(f"new_subject_{day}")
        new_teacher = request.POST.get(f"new_teacher_{day}")
        new_start_time = request.POST.get(f"new_start_time_{day}")
        new_end_time = request.POST.get(f"new_end_time_{day}")
        new_semester = request.POST.get(f"new_semester_{day}")

        if new_subject and new_teacher and new_start_time and new_end_time:
            TimeTable.objects.create(
                subject_name=new_subject,
                teacher_id=new_teacher,
                day=day,
                semester=new_semester,
                department=teacher_profile.department,
                start_time=new_start_time,
                end_time=new_end_time
            )

        messages.success(request, "Your Time Table updated successfully!")
        return redirect("manage_timetable_semester", semester=semester)

    # After POST or normal GET request
    timetable = TimeTable.objects.filter(semester=semester, teacher__department=department).order_by('day', 'start_time')
    teachers = TeacherProfile.objects.filter(department=department)

    return render(request, "faculty/teacher_manage_timetable.html", {'timetable': timetable, 
                                                                     'teachers': teachers, 
                                                                     'user_role': user_role,
                                                                     'days_of_week': days_of_week})

@login_required
def show_timetable(request):

    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    time_table = TimeTable.objects.filter(teacher=teacher_profile).order_by('day', 'start_time')

    return render(request, "faculty/teacher_show_timetable.html", {'time_table': time_table})



# ##############################################################################################
# ############################  ATTENDANCE  ####################################################
# ##############################################################################################
@login_required
def attendance_timetable(request):
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    time_table = TimeTable.objects.filter(teacher=teacher_profile).order_by('day', 'start_time')

    return render(request, "faculty/teacher_attendance_timetable.html", {'time_table': time_table,
                                                                         'now': timezone.localtime().now()})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .models import TimeTable, StudentProfile, Attendance

@login_required
def take_attendance(request, lecture_id):
    lecture = get_object_or_404(TimeTable, id=lecture_id)
    students = StudentProfile.objects.filter(
        samester=lecture.semester,
        department=lecture.department
    )

    today = date.today()
    student_attendance = []

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.id}", 'Present')
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                lecture=lecture,
                date=today,
                defaults={'status': status}
            )
            if not created:
                attendance.status = status
                attendance.save()
        messages.success(request, "Attendance submitted successfully.")
        return redirect("attendance_timetable")  # adjust this URL name as needed

    # Prepare list of tuples (student, status)
    for student in students:
        existing = Attendance.objects.filter(student=student, lecture=lecture, date=today).first()
        status = existing.status if existing else 'Present'
        student_attendance.append((student, status))

    return render(request, "faculty/teacher_take_attendance.html", {
        'lecture': lecture,
        'student_attendance': student_attendance,
        'today': today
    })

@login_required
def attendance_semester_list(request):
    teacher = request.user
    semesters = TimeTable.objects.filter(teacher__user=teacher).values_list('semester', flat=True).distinct()
    return render(request, "faculty/attendance_semester_list.html", {'semesters': semesters})
@login_required
def attendance_by_semester(request, semester):
    teacher = request.user
    
    # Get all records for this semester and teacher
    attendance_records = Attendance.objects.filter(
        lecture__teacher__user=teacher,
        lecture__semester=semester
    ).select_related('student', 'lecture').order_by('date', 'student__full_name')
    
    # Get unique dates 
    unique_dates = attendance_records.values_list('date', flat=True).distinct().order_by('date')
    
    # Selected date (default to first date if not specified)
    selected_date = request.GET.get('date')
    
    # If a date was selected, try to use it
    if selected_date:
        try:
            # If date is in YYYY-MM-DD format already, use it
            import datetime
            # Try to parse the date - this will work if it's already in YYYY-MM-DD format
            selected_date_obj = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
            current_records = attendance_records.filter(date=selected_date_obj)
        except ValueError:
            # If parsing fails, default to the first date
            if unique_dates:
                selected_date = unique_dates[0]
                current_records = attendance_records.filter(date=selected_date)
            else:
                current_records = []
    # No date selected, default to first date
    elif unique_dates:
        selected_date = unique_dates[0]
        current_records = attendance_records.filter(date=selected_date)
    else:
        current_records = []
    
    return render(request, "faculty/show_attendance.html", {
        'unique_dates': unique_dates,
        'selected_date': selected_date,
        'current_records': current_records,
        'semester': semester,
    })