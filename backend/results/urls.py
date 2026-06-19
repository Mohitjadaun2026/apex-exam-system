from django.urls import path
from .views import save_result, all_results, student_results, teacher_results

urlpatterns = [

    path(
        'save-result/',
        save_result
    ),

    path(
        'all-results/',
        all_results
    ),

    path(
        'student-results/<int:student_id>/',
        student_results
    ),

    path(
        'teacher-results/<int:teacher_id>/',
        teacher_results
    ),

]