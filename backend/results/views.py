from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Result
from exams.models import Exam
from users.models import Student, Teacher


@api_view(['POST'])
def save_result(request):

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

    percentage = (
        score / total_questions
    ) * 100

    correct_answers = score

    wrong_answers = (
        total_questions - score
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
    })


@api_view(['GET'])
def all_results(request):
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
def student_results(request, student_id):
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
def teacher_results(request, teacher_id):
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        
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
        return Response({"error": "Teacher Not Found"}, status=404)