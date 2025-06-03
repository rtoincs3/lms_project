from django.shortcuts import render, redirect, get_object_or_404
from users.models import CustomUser
from .models import StudentProfile
from faculty.models import TeacherMaterial, TimeTable, Attendance
from exam.models import Exam
from exam.models import Question, Option, StudentExamResult, StudentExamSummary, Notification
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.db import transaction
from datetime import datetime
from collections import defaultdict


# Create your views here.
@login_required(login_url='login')
def student_dashboard(request):
    student_profile = StudentProfile.objects.get(user=request.user)
    materials = TeacherMaterial.objects.all()
    exam_count = Exam.objects.filter(
        department=student_profile.department,
        samester=student_profile.samester
    )

    # calculate attendance percentage
    attendance = Attendance.objects.filter(student=student_profile)
    total_lectures = attendance.count()
    present_lectures = attendance.filter(status__iexact="Present").count()

    attendance_percentage = (
        (present_lectures / total_lectures) * 100 if total_lectures else 0
    )

    student_info = None
    if request.user.is_authenticated:
        try:
            student_info = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            student_info = None


     # Get today's timetable
    today = datetime.now().date()
    day_name = today.strftime('%A')  # Get the current day name (Monday, Tuesday, etc.)
    
    # Get timetable for today
    today_timetable = TimeTable.objects.filter(
        semester=student_profile.samester,
        department=student_profile.department,
        day=day_name
    ).order_by('start_time')

    #  Notifications
    notifications = Notification.objects.filter(target_user__in=['student', 'both']).order_by('-created_at')
    
    return render(request, "student/student_dashboard.html", {'student_info': student_info,
                                                              'materials': materials,
                                                              'exam_count':exam_count,
                                                              'attendance_percentage': round(attendance_percentage, 1),
                                                              'total_lecture': total_lectures,
                                                              'notifications': notifications,
                                                              'today_timetable': today_timetable,
                                                              'today_date': today,
                                                              'day_name': day_name})

# ###########################################
@login_required(login_url='login')
def student_profile(request):
    student_info = None

    if request.user.is_authenticated:
        try:
            student_info = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            student_info = None

    return render(request, "student/student_profile.html", {'student_info': student_info})


def student_login(request):
    if request.method == "POST":
        roll_number = request.POST.get('roll_number')
        password = request.POST.get("password")

        try:
            # try to find user by roll number
            user = CustomUser.objects.get(roll_number=roll_number, user_type='student')

        except CustomUser.DoesNotExist:
            user = None
        

        if user is not None:
            # authentication user
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('student:student_dashboard')
            else:
                return render(request, 'student/student_login.html')
        else:
            return render(request, 'student/student_login.html')
        

    return render(request, 'student/student_login.html')


def user_logout(request):

    logout(request)
    return redirect('student:login')  # after logout, redirect to login page


@login_required
def available_exams(request):
    #  get student profil einformation
    student = StudentProfile.objects.get(user=request.user)
    

    #  get currnt time zone to filter out exam
    current_time = timezone.now()
    
    # get exam based of department samester and start and end time
    exams =  Exam.objects.filter(
        department=student.department,
        samester=student.samester,
        start_time__lte=current_time,
        end_time__gte=current_time
    ).annotate(total_marks = Sum('question__marks'))
    return render(request, "student/student_available_exam.html", {'exams': exams})


@login_required
def start_exam(request, exam_id):
    # Fetch the exam
    exam = get_object_or_404(Exam, id=exam_id)
    student = get_object_or_404(StudentProfile, user=request.user)
    questions = Question.objects.filter(exam=exam).prefetch_related('Options')

    # # Check if student has already given the exam
    # summary = StudentExamSummary.objects.filter(student=student, exam=exam).first()
    # if summary and summary.total_marks >= 0:
    #     # If student has already completed the exam, redirect to available exams
    #     messages.info(request, "You have already completed the exam")
    #     return redirect("available_exams")

    current_time = timezone.now()
    if current_time < exam.start_time or current_time > exam.end_time:
        return redirect("student:available_exams")

    # Check if the exam time has started
    session_key = f"exam_start_time_{exam.id}_{student.id}"
    if session_key not in request.session:
        request.session[session_key] = timezone.now().isoformat()  # Save exam start time

    

    if request.method == "POST":
        total_marks = 0
        total_questions = 0
        exam_results = []

        # Loop over all the questions
        for question in questions:
            selected_option_id = request.POST.get(f"q_correct_{question.id}")
            try:
                selected_option = Option.objects.get(id=selected_option_id)
                is_correct = selected_option.is_correct
                mark_obtains = question.marks if is_correct else 0
            except (Option.DoesNotExist, TypeError):
                selected_option = None
                is_correct = False
                mark_obtains = 0

            # Save result per question
            exam_result = StudentExamResult.objects.update_or_create(
                student=student,
                exam=exam,
                question=question,
                defaults={
                    'selected_option': selected_option,
                    'is_correct': is_correct,
                    'mark_obtains': mark_obtains,
                }
            )

            # Collect exam results for the summary
            exam_results.append(exam_result[0])
            total_marks += mark_obtains
            if is_correct:
                total_questions += 1

        # # Create or update the Student Exam Summary
        # summary, created = StudentExamSummary.objects.update_or_create(
        #     student=student,
        #     exam=exam,
        #     defaults={
        #         'total_marks': total_marks,
        #         'total_questions': total_questions,
        #     }
        # )

        # # Add the exam results to the summary
        # summary.exam_results.set(exam_results)

        # # Calculate the summary totals (marks and questions)
        # summary.calculate_summary()
        # summary.has_attempted = False
        # summary.save()

        messages.success(request, f"Exam submitted successfully! Your total marks: {total_marks}")
        return redirect('student:available_exams')

    # Passing remaining time to the template
    return render(request, "student/student_start_exam.html", {'exam': exam, 
                                                               'questions': questions, 
                                                               })



# #################################################
##################################################
@login_required
def student_material(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    materials = TeacherMaterial.objects.filter(department=student_profile.department)

    return render(request, "student/student_material.html", {'materials': materials})


@login_required
def time_table(request):
    from datetime import datetime, timedelta
    import calendar
    
    # Get the current date
    today = datetime.now().date()
    
    # Get the current day of the week (0 is Monday, 6 is Sunday)
    current_weekday = today.weekday()
    
    # Calculate the date of Monday of this week
    monday_date = today - timedelta(days=current_weekday)
    
    # Create a dictionary mapping day names to their dates for this week
    week_dates = {}
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    for i, day in enumerate(day_names):
        date = monday_date + timedelta(days=i)
        week_dates[day] = date
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    time_table = TimeTable.objects.filter(
        semester=student_profile.samester,
        department=student_profile.department
    ).order_by('day', 'start_time')
    
    # Group the timetable by day
    grouped_timetable = {}
    for day in day_names:
        day_timetable = time_table.filter(day=day)
        grouped_timetable[day] = {
            'lectures': day_timetable,
            'date': week_dates[day]
        }
    
    return render(request, "student/student_timetable.html", {
        'grouped_timetable': grouped_timetable,
        'week_dates': week_dates
    })


@login_required
def student_show_attendance(request):
    student_profile = StudentProfile.objects.get(user=request.user)
    attendance_records = Attendance.objects.filter(student=student_profile).select_related('lecture').order_by("-date")

    # get unique attendace date
    unique_dates = attendance_records.values_list('date', flat=True).distinct().order_by('date')

    # handle date selection from dropdown
    selected_date_str = request.GET.get('date')
    selected_date_obj = None

    if selected_date_str:
        try:
            selected_date_obj = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    if not selected_date_obj and unique_dates:
        selected_date_obj = unique_dates[0]

    
    # filter records by selected date
    if selected_date_obj:
        filter_records = attendance_records.filter(date=selected_date_obj)
    else:
        filter_records = []

    return render(request, "student/student_attendance.html", {'attendance_records': filter_records,
                                                               'unique_dates': unique_dates,
                                                               'selected_date': selected_date_obj})



@login_required
def attendance_percentage(request):
    student_profile = StudentProfile.objects.get(user=request.user)
    attendance_qs = Attendance.objects.filter(student=student_profile)

    # Using defaultdict to collect counts
    subject_totals = defaultdict(lambda: {'present': 0, 'total': 0})

    for record in attendance_qs:
        subject = record.lecture.subject_name
        subject_totals[subject]['total'] += 1
        if record.status == 'Present':
            subject_totals[subject]['present'] += 1

    # Build the final list
    results = []
    for subject, data in subject_totals.items():
        total = data['total']
        present = data['present']
        percentage = (present / total) * 100 if total > 0 else 0
        results.append({
            'subject': subject,
            'present': present,
            'total': total,
            'percentage': round(percentage, 2)
        })

    return render(request, "student/student_attendance_percentage.html", {'results': results})
