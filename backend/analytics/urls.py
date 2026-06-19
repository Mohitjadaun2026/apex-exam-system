from django.urls import path
from .views import dashboard_stats, student_dashboard

urlpatterns = [

    path(
        'dashboard-stats/',
        dashboard_stats
    ),
  path(
        'results/student-dashboard/<int:student_id>/',
        student_dashboard
    ),
    path(
        'student-dashboard/<int:student_id>/',
        student_dashboard
    ),
]