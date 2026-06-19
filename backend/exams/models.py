from django.db import models


class Subject(models.Model):

    name = models.CharField(max_length=100)

    class_name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} - {self.class_name}"


class Question(models.Model):

    DIFFICULTY_CHOICES = (
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    )

    class_name = models.CharField(max_length=20)

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    question_text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_answer = models.CharField(max_length=255)

    marks = models.IntegerField(default=1)

    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='Easy'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:50]
    

class Exam(models.Model):

    EXAM_TYPES = (
        ('UNIT_TEST', 'Unit Test'),
        ('MID_TERM', 'Mid Term'),
        ('FINAL_EXAM', 'Final Exam')
    )

    exam_name = models.CharField(max_length=255)

    class_name = models.CharField(max_length=20)

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPES,
        default='UNIT_TEST'
    )

    duration = models.IntegerField(
        help_text="Total Exam Duration in Minutes"
    )

    question_timer = models.IntegerField(
        help_text="Time Per Question in Seconds"
    )

    total_marks = models.IntegerField()

    passing_marks = models.IntegerField()

    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.exam_name
    

class ExamQuestion(models.Model):

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.exam.exam_name} - {self.question.id}"