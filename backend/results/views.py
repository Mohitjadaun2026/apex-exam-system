from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Result
from exams.models import Exam
from users.models import Student, Teacher
from api_utils import require_authenticated_role, get_authenticated_student, get_authenticated_teacher


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_result(request):

    role_error = require_authenticated_role(request, {"ADMIN", "TEACHER"})
    if role_error:
        return role_error

    student = Student.objects.get(
        id=request.data.get("student_id")
    )

    exam = Exam.objects.get(
        id=request.data.get("exam_id")
    )

    score = int(
        request.data.get("score")
    )

    total_questions = int(
        request.data.get(
            "total_questions"
        )
    )

    if total_questions <= 0:
        return Response({"error": "Total questions must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

    if score < 0:
        return Response({"error": "Score cannot be negative"}, status=status.HTTP_400_BAD_REQUEST)

    percentage = (
        score / total_questions
    ) * 100

    correct_answers = score

    wrong_answers = (
        total_questions - correct_answers
    )

    status = (
        "PASS"
        if percentage >= 40
        else "FAIL"
    )

    Result.objects.create(

        student=student,

        exam=exam,

        total_questions=
        total_questions,

        correct_answers=
        correct_answers,

        wrong_answers=
        wrong_answers,

        score=score,

        percentage=
        percentage,

        status=status

    )

    return Response({
        "message":
        "Result Saved"
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_results(request):
    role_error = require_authenticated_role(request, {"ADMIN", "TEACHER"})
    if role_error:
        return role_error

    # .select_related() use karna taaki database query fast ho
    results = Result.objects.select_related('student', 'exam', 'exam__subject').all()

    data = []
    for result in results:
        data.append({
            "id": result.id,
            "student": result.student.user.email,
            "exam": result.exam.exam_name,
            "score": result.score,
            "percentage": result.percentage,
            "status": result.status,
            # Yahan subject fetch karo:
            "subject_name": result.exam.subject.name if result.exam.subject else "N/A"
        })
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_results(request, student_id):
    student, error_response = get_authenticated_student(request)
    if error_response:
        return error_response

    if str(student.id) != str(student_id):
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    # Sirf us student ke results fetch karo
    results = Result.objects.filter(student_id=student_id).select_related('exam', 'exam__subject')
    
    data = []
    for result in results:
        data.append({
            "id": result.id,
            "exam": result.exam.exam_name,
            "score": result.score,
            "percentage": result.percentage,
            "status": result.status,
            "date": result.created_at,
            "subject_name": result.exam.subject.name if result.exam.subject else "N/A"
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_results(request, teacher_id):
    try:
        teacher, error_response = get_authenticated_teacher(request)
        if error_response:
            return error_response

        if str(teacher.id) != str(teacher_id):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        # Filter karke results lao
        results = Result.objects.filter(
            exam__class_name=teacher.assigned_classes,
            exam__subject__name=teacher.subject
        )

        data = []
        for result in results:
            data.append({
                "id": result.id,
                "student": result.student.user.email,
                "exam": result.exam.exam_name,
                "score": result.score,
                "percentage": result.percentage,
                "status": result.status,
                # YEH LINE ZAROORI HAI:
                "subject_name": result.exam.subject.name if result.exam.subject else "N/A"
            })
            
        return Response(data)

    except Teacher.DoesNotExist:
        return Response({"error": "Teacher Not Found"}, status=status.HTTP_404_NOT_FOUND)