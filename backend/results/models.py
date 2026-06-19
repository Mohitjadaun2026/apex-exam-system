from django.db import models
from users.models import Student
from exams.models import Exam, Question


class StudentAnswer(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_answer = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    is_correct = models.BooleanField(
        default=False
    )

    answered_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.student.user.email} - "
            f"{self.question.id}"
        )


class Result(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    total_questions = models.IntegerField(
        default=0
    )

    correct_answers = models.IntegerField(
        default=0
    )

    wrong_answers = models.IntegerField(
        default=0
    )

    score = models.IntegerField(
        default=0
    )

    percentage = models.FloatField(
        default=0
    )

    grade = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        default="FAIL"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.student.user.email} - "
            f"{self.exam.exam_name}"
        )