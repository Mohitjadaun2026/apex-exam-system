from django.contrib import admin
from .models import (
    Subject,
    Question,
    Exam,
    ExamQuestion
)

admin.site.register(Subject)
admin.site.register(Question)
admin.site.register(Exam)
admin.site.register(ExamQuestion)