from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.models import Student
from .models import ExamQuestion, Question, Subject, Exam
from users.models import Teacher
from results.models import Result # Ensure karo ye import ho
from api_utils import (
    get_authenticated_student,
    require_authenticated_role,
)


def normalize_class_label(value):
    normalized = "".join(ch for ch in str(value or "").strip().lower() if ch.isalnum())
    digits = "".join(ch for ch in normalized if ch.isdigit())
    if digits:
        return digits.lstrip("0") or "0"
    return normalized

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_exam(request):
    try:
        exam_id = request.data.get('exam_id')
        user_answers = request.data.get('answers', {}) # {'question_id': 'selected_option'}

        student, error_response = get_authenticated_student(request)
        if error_response:
            return error_response

        exam = Exam.objects.filter(id=exam_id).select_related('subject').first()
        if not exam:
            return Response({"error": "Exam Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if not exam.is_active:
            return Response({"error": "Exam is not active"}, status=status.HTTP_403_FORBIDDEN)

        if str(student.class_name).strip().lower() != str(exam.class_name).strip().lower():
            return Response({"error": "This exam is not assigned to your class"}, status=status.HTTP_403_FORBIDDEN)

        if Result.objects.filter(student=student, exam=exam).exists():
            return Response({"error": "Exam already submitted"}, status=status.HTTP_409_CONFLICT)
        
        score = 0
        correct_answers = 0
        total_questions = 0
        
        # Sabhi questions jo exam se jude hain unhe fetch karo
        exam_questions = ExamQuestion.objects.filter(exam=exam)
        total_questions = exam_questions.count()
        total_possible_marks = 0

        for eq in exam_questions:
            q = eq.question
            q_id_str = str(q.id)
            total_possible_marks += int(q.marks or 0)
            
            # Agar student ne jawab diya hai
            if q_id_str in user_answers:
                selected_answer = str(user_answers[q_id_str]).strip().upper()
                correct_answer = str(q.correct_answer).strip().upper()

                if selected_answer == correct_answer:
                    score += q.marks
                    correct_answers += 1
        
        if total_questions == 0:
            return Response({"error": "No questions assigned to this exam"}, status=status.HTTP_400_BAD_REQUEST)

        # Percentage is based on the actual assigned marks so complete correctness shows 100%
        percentage = (score / total_possible_marks) * 100 if total_possible_marks > 0 else 0

        configured_passing_marks = int(getattr(exam, "passing_marks", 0) or 0)
        if 0 < configured_passing_marks <= total_possible_marks:
            passed = score >= configured_passing_marks
        else:
            passed = percentage >= 40

        status_value = "PASS" if passed else "FAIL"

        # Result save karo
        with transaction.atomic():
            Result.objects.create(
                student=student,
                exam=exam,
                score=score,
                total_questions=total_questions,
                correct_answers=correct_answers,
                wrong_answers=total_questions - correct_answers,
                percentage=percentage,
                status=status_value
            )

        return Response({"message": "Exam submitted successfully", "score": score, "percentage": percentage, "status": status_value})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subjects(request):

    role_error = require_authenticated_role(request, {"ADMIN", "TEACHER"})
    if role_error:
        return role_error

    subjects = Subject.objects.all().order_by(
        'class_name',
        'name'
    )

    data = []

    for subject in subjects:

        data.append({

            "id": subject.id,

            "name": subject.name,

            "class_name": subject.class_name

        })

    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_subject(request):

    role_error = require_authenticated_role(request, {"ADMIN"})
    if role_error:
        return role_error

    name = request.data.get(
        "name"
    )

    class_name = request.data.get(
        "class_name"
    )

    if not name or not class_name:

        return Response({

            "error":
            "All fields are required"

        }, status=400)

    already_exists = Subject.objects.filter(

        name=name,

        class_name=class_name

    ).exists()

    if already_exists:

        return Response({

            "error":
            "Subject already exists"

        }, status=400)

    subject = Subject.objects.create(

        name=name,

        class_name=class_name

    )

    return Response({

        "message":
        "Subject Added Successfully",

        "subject_id":
        subject.id

    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_subject(request, subject_id):

    role_error = require_authenticated_role(request, {"ADMIN"})
    if role_error:
        return role_error

    try:

        subject = Subject.objects.get(
            id=subject_id
        )

        subject.delete()

        return Response({

            "message":
            "Subject Deleted Successfully"

        })

    except Subject.DoesNotExist:

        return Response({

            "error":
            "Subject Not Found"

        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questions(request):

    role_error = require_authenticated_role(request, {"ADMIN", "TEACHER"})
    if role_error:
        return role_error

    questions = Question.objects.all().order_by(
        '-created_at'
    )

    data = []

    for q in questions:

        data.append({

            "id": q.id,

            "subject_name": q.subject.name,

            "class_name": q.class_name,

            "question_text": q.question_text,

            "option_a": q.option_a,

            "option_b": q.option_b,

            "option_c": q.option_c,

            "option_d": q.option_d,

            "correct_answer": q.correct_answer,

            "marks": q.marks,

            "difficulty_level": q.difficulty_level

        })

    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_question(request):

    role_error = require_authenticated_role(request, {"ADMIN", "TEACHER"})
    if role_error:
        return role_error

    try:

        subject = Subject.objects.get(
            id=request.data.get("subject_id")
        )

        question_text = str(request.data.get("question_text") or "").strip()
        option_a = str(request.data.get("option_a") or "").strip()
        option_b = str(request.data.get("option_b") or "").strip()
        option_c = str(request.data.get("option_c") or "").strip()
        option_d = str(request.data.get("option_d") or "").strip()
        correct_answer = str(request.data.get("correct_answer") or "").strip().upper()
        difficulty_level = str(request.data.get("difficulty_level") or "Easy").strip()
        marks = int(request.data.get("marks") or 0)

        if not question_text or not option_a or not option_b or not option_c or not option_d:
            return Response({"error": "All question fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if correct_answer not in {"A", "B", "C", "D"}:
            return Response({"error": "Correct answer must be one of A, B, C, D"}, status=status.HTTP_400_BAD_REQUEST)

        if marks <= 0:
            return Response({"error": "Marks must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        Question.objects.create(

            class_name=request.data.get(
                "class_name"
            ),

            subject=subject,

            question_text=request.data.get(
                "question_text"
            ).strip(),

            option_a=request.data.get(
                "option_a"
            ).strip(),

            option_b=request.data.get(
                "option_b"
            ).strip(),

            option_c=request.data.get(
                "option_c"
            ).strip(),

            option_d=request.data.get(
                "option_d"
            ).strip(),

            correct_answer=correct_answer,

            marks=marks,

            difficulty_level=difficulty_level

        )

        return Response({

            "message":
            "Question Added Successfully"

        })

    except Subject.DoesNotExist:

        return Response({

            "error":
            "Subject Not Found"

        }, status=404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_question(request, question_id):

    role_error = require_authenticated_role(request, {"ADMIN", "TEACHER"})
    if role_error:
        return role_error

    try:

        question = Question.objects.get(
            id=question_id
        )

        question.delete()

        return Response({

            "message":
            "Question Deleted Successfully"

        })

    except Question.DoesNotExist:

        return Response({

            "error":
            "Question Not Found"

        }, status=status.HTTP_404_NOT_FOUND)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exams(request):

    role_error = require_authenticated_role(request, {"ADMIN", "TEACHER"})
    if role_error:
        return role_error

    exams = Exam.objects.all().order_by(
        '-created_at'
    )

    data = []

    for exam in exams:

        data.append({

            "id": exam.id,

            "exam_name": exam.exam_name,

            "class_name": exam.class_name,

            "subject_name": exam.subject.name,

            "duration": exam.duration,

            "question_timer": exam.question_timer,

            "total_marks": exam.total_marks,

            "passing_marks": exam.passing_marks,

            "is_active": exam.is_active

        })

    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exam(request):

    role_error = require_authenticated_role(request, {"ADMIN"})
    if role_error:
        return role_error

    try:

        subject = Subject.objects.get(
            id=request.data.get(
                "subject_id"
            )
        )

        exam_name = str(request.data.get("exam_name") or "").strip()
        class_name = str(request.data.get("class_name") or "").strip()
        duration = int(request.data.get("duration") or 0)
        question_timer = int(request.data.get("question_timer") or 0)
        total_marks = int(request.data.get("total_marks") or 0)
        passing_marks = int(request.data.get("passing_marks") or 0)

        if not exam_name or not class_name:
            return Response({"error": "Exam name and class are required"}, status=status.HTTP_400_BAD_REQUEST)

        if duration <= 0 or question_timer <= 0 or total_marks <= 0:
            return Response({"error": "Duration, question timer, and total marks must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        if passing_marks <= 0 or passing_marks > total_marks:
            return Response({"error": "Passing marks must be greater than zero and less than or equal to total marks"}, status=status.HTTP_400_BAD_REQUEST)

        exam = Exam.objects.create(

            exam_name=exam_name,

            class_name=class_name,

            subject=subject,

            duration=duration,

            question_timer=question_timer,

            total_marks=total_marks,

            passing_marks=passing_marks,

            is_active=True

        )

        return Response({

            "message":
            "Exam Created Successfully",

            "exam_id":
            exam.id

        })

    except Subject.DoesNotExist:

        return Response({

            "error":
            "Subject Not Found"

        }, status=404)
    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_exam(request, exam_id):

    role_error = require_authenticated_role(request, {"ADMIN"})
    if role_error:
        return role_error

    try:

        exam = Exam.objects.get(
            id=exam_id
        )

        exam.delete()

        return Response({

            "message":
            "Exam Deleted Successfully"

        })

    except Exam.DoesNotExist:

        return Response({

            "error":
            "Exam Not Found"

        }, status=status.HTTP_404_NOT_FOUND)
    

    











@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_question(request):

    role_error = require_authenticated_role(request, {"ADMIN", "TEACHER"})
    if role_error:
        return role_error

    try:
        exam = Exam.objects.get(id=request.data.get("exam_id"))
        question = Question.objects.get(id=request.data.get("question_id"))

        if ExamQuestion.objects.filter(exam=exam, question=question).exists():
            return Response({"error": "Question already assigned to this exam"}, status=status.HTTP_409_CONFLICT)

        ExamQuestion.objects.create(
            exam=exam,
            question=question
        )
        return Response({
            "message": "Question Assigned"
        }, status=status.HTTP_201_CREATED)
    except Exam.DoesNotExist:
        return Response({"error": "Exam Not Found"}, status=status.HTTP_404_NOT_FOUND)
    except Question.DoesNotExist:
        return Response({"error": "Question Not Found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam_questions(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    exam_questions = ExamQuestion.objects.filter(
        exam_id=exam_id
    )

    user_role = str(getattr(request.user, "role", "")).upper()
    if user_role == "STUDENT":
        student, error_response = get_authenticated_student(request)
        if error_response:
            return error_response

        if normalize_class_label(student.class_name) != normalize_class_label(exam.class_name):
            return Response({"error": "This exam is not assigned to your class"}, status=status.HTTP_403_FORBIDDEN)

        if not exam.is_active:
            return Response({"error": "Exam is not active"}, status=status.HTTP_403_FORBIDDEN)

    data = []
    for eq in exam_questions:
        q = eq.question
        data.append({
            "id": q.id,
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
        })
    return Response({
        "questions": data,
        "duration": exam.duration,
        "question_timer": exam.question_timer,
        "passing_marks": exam.passing_marks,
        "total_marks": exam.total_marks,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_exams(request, student_id):
    try:
        student, error_response = get_authenticated_student(request)
        if error_response:
            return error_response

        if str(student.id) != str(student_id):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        std_class = normalize_class_label(student.class_name)
        
        # 1. Is class ke saare exams fetch karo
        exams = [
            exam for exam in Exam.objects.filter(is_active=True).select_related("subject")
            if normalize_class_label(exam.class_name) == std_class
        ]
        
        # 2. Is student ne jo exams de diye hain, unki ids ki list nikalo
        attempted_exam_ids = Result.objects.filter(
            student_id=student_id
        ).values_list('exam_id', flat=True)
        attempted_exam_ids = set(attempted_exam_ids)
        
        data = []
        for exam in exams:
            data.append({
                "id": exam.id,
                "exam_name": exam.exam_name,
                "subject": exam.subject.name,
                "duration": exam.duration,
                # Agar list mein id hai toh True, nahi toh False
                "has_attempted": exam.id in attempted_exam_ids
            })
        return Response(data)
        
    except Student.DoesNotExist:
        return Response({
            "error": "Student Not Found"
        }, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_exam_status(request, exam_id):
    try:
        role_error = require_authenticated_role(request, {"ADMIN"})
        if role_error:
            return role_error

        exam = Exam.objects.get(id=exam_id)
        exam.is_active = not exam.is_active
        exam.save()
        return Response({
            "message": f"Exam status updated to {exam.is_active}",
            "is_active": exam.is_active
        })
    except Exam.DoesNotExist:
        return Response({
            "error": "Exam Not Found"
        }, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_exams(request, teacher_id):

    try:
        teacher = Teacher.objects.get(id=teacher_id)

        role_error = require_authenticated_role(request, {"TEACHER"})
        if role_error:
            return role_error

        if str(teacher.user_id) != str(request.user.id):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        exams = Exam.objects.filter(

            class_name__iexact=teacher.assigned_classes,

            subject__name__iexact=teacher.subject

        ).order_by('-created_at')

        data = []

        for exam in exams:

            data.append({

                "id": exam.id,

                "exam_name": exam.exam_name,

                "subject_name": exam.subject.name,

                "class_name": exam.class_name,

                "duration": exam.duration,

                "total_marks": exam.total_marks,

                "is_active": exam.is_active

            })

        return Response(data)

    except Teacher.DoesNotExist:

        return Response({

            "error": "Teacher Not Found"

        }, status=status.HTTP_404_NOT_FOUND)