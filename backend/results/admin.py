from django.contrib import admin
from .models import Result, StudentAnswer


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'student',
        'exam',
        'score',
        'percentage',
        'status',
        'created_at'
    )


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'student',
        'exam',
        'question',
        'selected_answer',
        'is_correct'
    )