from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import Student
from .models import ExamQuestion, Question, Subject, Exam
from users.models import Teacher


@api_view(['GET'])
def get_subjects(request):

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
def add_subject(request):

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
def delete_subject(request, subject_id):

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

        }, status=404)

@api_view(['GET'])
def get_questions(request):

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
def add_question(request):

    try:

        subject = Subject.objects.get(
            id=request.data.get("subject_id")
        )

        Question.objects.create(

            class_name=request.data.get(
                "class_name"
            ),

            subject=subject,

            question_text=request.data.get(
                "question_text"
            ),

            option_a=request.data.get(
                "option_a"
            ),

            option_b=request.data.get(
                "option_b"
            ),

            option_c=request.data.get(
                "option_c"
            ),

            option_d=request.data.get(
                "option_d"
            ),

            correct_answer=request.data.get(
                "correct_answer"
            ),

            marks=request.data.get(
                "marks"
            ),

            difficulty_level=request.data.get(
                "difficulty_level"
            )

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
def delete_question(request, question_id):

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

        }, status=404)






@api_view(['GET'])
def get_exams(request):

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
def create_exam(request):

    try:

        subject = Subject.objects.get(
            id=request.data.get(
                "subject_id"
            )
        )

        exam = Exam.objects.create(

            exam_name=request.data.get(
                "exam_name"
            ),

            class_name=request.data.get(
                "class_name"
            ),

            subject=subject,

            duration=request.data.get(
                "duration"
            ),

            question_timer=request.data.get(
                "question_timer"
            ),

            total_marks=request.data.get(
                "total_marks"
            ),

            passing_marks=request.data.get(
                "passing_marks"
            )

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
def delete_exam(request, exam_id):

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

        }, status=404)
    

    











@api_view(['POST'])
def assign_question(request):
    exam = Exam.objects.get(
        id=request.data.get("exam_id")
    )
    question = Question.objects.get(
        id=request.data.get("question_id")
    )
    ExamQuestion.objects.create(
        exam=exam,
        question=question
    )
    return Response({
        "message": "Question Assigned"
    })

@api_view(['GET'])
def get_exam_questions(request, exam_id):
    exam_questions = ExamQuestion.objects.filter(
        exam_id=exam_id
    )
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
            "correct_answer": q.correct_answer
        })
    return Response(data)

try:
    from results.models import Result
except ImportError:
    from apps.results.models import Result # Agar aapka apps folder alag hai

@api_view(['GET'])
def available_exams(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        std_class = str(student.class_name).strip()
        
        # 1. Is class ke saare exams fetch karo
        exams = Exam.objects.filter(class_name__icontains=std_class)
        
        # 2. Is student ne jo exams de diye hain, unki ids ki list nikalo
        attempted_exam_ids = Result.objects.filter(
            student_id=student_id
        ).values_list('exam_id', flat=True)
        
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
        }, status=404)
    
@api_view(['POST'])
def toggle_exam_status(request, exam_id):
    try:
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
        }, status=404)
    
@api_view(['GET'])
def teacher_exams(request, teacher_id):

    try:

        teacher = Teacher.objects.get(
            id=teacher_id
        )

        exams = Exam.objects.filter(

            class_name=teacher.assigned_classes,

            subject__name=teacher.subject

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

        }, status=404)