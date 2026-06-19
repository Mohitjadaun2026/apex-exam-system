from django.urls import path

from .views import (
    get_subjects,
    add_subject,
    delete_subject,
    get_questions,
    add_question,
    delete_question,
    get_exams,
    create_exam,
    delete_exam,
    toggle_exam_status,
    assign_question,
    get_exam_questions,
    available_exams,
    teacher_exams,
    submit_exam  # Yahan import add kiya hai
)

urlpatterns = [

    # SUBJECTS
    path('subjects/', get_subjects),
    path('add-subject/', add_subject),
    path('delete-subject/<int:subject_id>/', delete_subject),

    # QUESTIONS
    path('questions/', get_questions),
    path('add-question/', add_question),
    path('delete-question/<int:question_id>/', delete_question),

    # EXAMS
    path('exams/', get_exams),
    path('create-exam/', create_exam),
    path('delete-exam/<int:exam_id>/', delete_exam),
    path('toggle-exam/<int:exam_id>/', toggle_exam_status),
    path('assign-question/', assign_question),
    path('exam-questions/<int:exam_id>/', get_exam_questions),
    path('available-exams/<int:student_id>/', available_exams),
    path('teacher-exams/<int:teacher_id>/', teacher_exams),
    
    # SUBMISSION (Yeh naya path add kiya)
    path('submit/', submit_exam),
]