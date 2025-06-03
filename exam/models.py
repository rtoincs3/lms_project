from django.db import models
from faculty.models import TeacherProfile
from users.models import Department   #department Only
from student.models import StudentProfile
from django.db.models import Sum



# Create your models here.

class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)

    '''Data integrity - -Department
        Suppose a teacher is moved to another department, or their profile changes —
        If you save department directly inside Exam, the exam stays safe and doesn't break.
    '''
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    samester = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_miniutes = models.PositiveIntegerField(help_text="Exam Duration in Miniutes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="question")
    text = models.TextField()
    marks = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return f"Q: {self.text}"
    

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="Options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class StudentExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="student_results")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="exam_results")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="student_answer")
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True)

    #  true if student selected correct answer
    is_correct = models.BooleanField(default=False)

    # mark obtained for this question
    mark_obtains = models.PositiveIntegerField(default=0)

    # time when answer submited
    submitted_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        # ensure one student can give only one answer per question
        unique_together = ('student', 'question', 'exam')
    
    def __str__(self):
        return f"{self.student} | {self.exam} | Question: {self.question.id}"
    
    
class StudentExamSummary(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    total_marks = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    has_attempted = models.BooleanField(default=False)

    # Track individual answers (if needed)
    exam_results = models.ManyToManyField(StudentExamResult, related_name='exam_summary', blank=True)

    def __str__(self):
        return f"{self.student} - {self.exam}"

    def calculate_summary(self):
        # Automatically calculate the number of correct answers and total marks
        correct_answers = self.exam_results.filter(is_correct=True).count()
        total_marks = self.exam_results.filter(is_correct=True).aggregate(Sum('mark_obtains'))['mark_obtains__sum'] or 0
        self.total_questions = self.exam_results.count()
        self.total_marks = total_marks
        self.save()

    class Meta:
        verbose_name = 'Student Exam Summary'
        verbose_name_plural = 'Student Exam Summaries'



# ##################################################
##################################################
TARGET_CHOICES = [
    ('student', 'Student'),
    ('faculty', 'Faculty'),
    ('both', 'Both')
    ]

class Notification(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    target_user = models.CharField(max_length=10, choices=TARGET_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title
