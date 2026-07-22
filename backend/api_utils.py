from rest_framework import status
from rest_framework.response import Response


def require_authenticated_role(request, allowed_roles):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    if allowed_roles is None:
        return None

    user_role = str(getattr(user, "role", "")).upper()
    normalized_allowed_roles = {str(role).upper() for role in allowed_roles}

    if user_role not in normalized_allowed_roles:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    return None


def get_authenticated_student(request):
    from users.models import Student

    role_error = require_authenticated_role(request, {"STUDENT"})
    if role_error:
        return None, role_error

    try:
        student = Student.objects.get(user=request.user)
        return student, None
    except Student.DoesNotExist:
        return None, Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)


def get_authenticated_teacher(request):
    from users.models import Teacher

    role_error = require_authenticated_role(request, {"TEACHER"})
    if role_error:
        return None, role_error

    try:
        teacher = Teacher.objects.get(user=request.user)
        return teacher, None
    except Teacher.DoesNotExist:
        return None, Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)
