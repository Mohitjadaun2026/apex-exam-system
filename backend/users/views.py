from django.contrib.auth.hashers import check_password, make_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Student, Teacher
from users.models import User
from api_utils import require_authenticated_role


@api_view(['POST'])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = User.objects.get(email=email)

        if not check_password(password, user.password):
            return Response(
                {"error": "Invalid Password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        response_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "id": user.id,
            "email": user.email,
            "role": user.role.lower(),
        }

        if user.role == "STUDENT":
            try:
                student = Student.objects.get(user=user)
                response_data["student_id"] = student.id
            except Student.DoesNotExist:
                response_data["student_id"] = None

        elif user.role == "TEACHER":
            try:
                teacher = Teacher.objects.get(user=user)
                response_data["teacher_id"] = teacher.id
            except Teacher.DoesNotExist:
                response_data["teacher_id"] = None

        return Response(response_data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(
            {"error": "User Not Found"},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_students(request):
    role_error = require_authenticated_role(request, {"ADMIN"})
    if role_error:
        return role_error

    students = Student.objects.all()
    data = []
    for student in students:
        data.append({
            "id": student.id,
            "email": student.user.email,
            "class_name": student.class_name,
            "roll_number": student.roll_number
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_student(request):
    role_error = require_authenticated_role(request, {"ADMIN"})
    if role_error:
        return role_error

    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password") or ""
    class_name = (request.data.get("class_name") or "").strip()
    roll_number = (request.data.get("roll_number") or "").strip()

    if not email or not password or not class_name or not roll_number:
        return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email__iexact=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create(
        email=email,
        username=email,
        role="STUDENT",
        password=make_password(password)
    )

    student = Student.objects.create(
        user=user,
        class_name=class_name,
        roll_number=roll_number
    )

    return Response({
        "message": "Student Created",
        "user_id": user.id,
        "student_id": student.id,
        "email": user.email,
        "role": user.role
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_student(request, student_id):
    try:
        role_error = require_authenticated_role(request, {"ADMIN"})
        if role_error:
            return role_error

        student = Student.objects.get(id=student_id)
        student.user.delete()
        return Response({
            "message": "Student Deleted"
        })
    except Student.DoesNotExist:
        return Response({
            "error": "Student Not Found"
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teachers(request):
    role_error = require_authenticated_role(request, {"ADMIN"})
    if role_error:
        return role_error

    teachers = Teacher.objects.all()
    data = []
    for teacher in teachers:
        data.append({
            "id": teacher.id,
            "email": teacher.user.email,
            "subject": teacher.subject,
            "assigned_classes": teacher.assigned_classes
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_teacher(request):
    role_error = require_authenticated_role(request, {"ADMIN"})
    if role_error:
        return role_error

    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password") or ""
    subject = (request.data.get("subject") or "").strip()
    assigned_classes = (request.data.get("assigned_classes") or "").strip()

    if not email or not password or not subject or not assigned_classes:
        return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email__iexact=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create(
        email=email,
        username=email,
        role="TEACHER",
        password=make_password(password)
    )

    Teacher.objects.create(
        user=user,
        subject=subject,
        assigned_classes=assigned_classes
    )

    return Response({
        "message": "Teacher Created"
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_teacher(request, teacher_id):
    try:
        role_error = require_authenticated_role(request, {"ADMIN"})
        if role_error:
            return role_error

        teacher = Teacher.objects.get(id=teacher_id)
        teacher.user.delete()
        return Response({
            "message": "Teacher Deleted"
        })
    except Teacher.DoesNotExist:
        return Response({
            "error": "Teacher Not Found"
        }, status=status.HTTP_404_NOT_FOUND)