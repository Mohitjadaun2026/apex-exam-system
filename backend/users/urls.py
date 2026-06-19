from django.urls import path
from .views import delete_student, get_students
from .views import add_student
from .views import login_user
from .views import (
    get_teachers,
    add_teacher,
    delete_teacher
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path(
        'login/',
        login_user
    ),
    path('refresh/', TokenRefreshView.as_view()),
    path(
    'students/',
    get_students
),
path(
    'add-student/',
    add_student
),
path(
    'delete-student/<int:student_id>/',
    delete_student
),
path(
    'teachers/',
    get_teachers
),

path(
    'add-teacher/',
    add_teacher
),

path(
    'delete-teacher/<int:teacher_id>/',
    delete_teacher
),

]