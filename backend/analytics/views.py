from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import Student, Teacher
from exams.models import Subject, Exam
from results.models import Result

@api_view(['GET'])
def dashboard_stats(request):
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_subjects = Subject.objects.count()
    total_exams = Exam.objects.count()
    total_results = Result.objects.count()

    results = Result.objects.all()
    pass_count = 0
    fail_count = 0

    for r in results:
        if r.total_questions > 0:
            percentage = (r.score / r.total_questions) * 100
            if percentage >= 40:
                pass_count += 1
            else:
                fail_count += 1
        else:
            fail_count += 1

    return Response({
        "students": total_students,
        "teachers": total_teachers,
        "subjects": total_subjects,
        "exams": total_exams,
        "results": total_results,
        "pass_count": pass_count,
        "fail_count": fail_count
    })

@api_view(['GET'])
def student_dashboard(request, student_id):
    results = Result.objects.filter(student_id=student_id)
    total_exams = results.count()
    
    total_percentage = 0
    recent_results = []

    for result in results:
        if result.total_questions > 0:
            percentage = (result.score / result.total_questions) * 100
            total_percentage += percentage
        else:
            total_percentage += 0

    average_score = (total_percentage / total_exams) if total_exams > 0 else 0

    try:
        latest_entries = results.order_by('-created_at')[:5]
    except Exception:
        latest_entries = results.order_by('-id')[:5]

    for result in latest_entries:
        pct = (result.score / result.total_questions) * 100 if result.total_questions > 0 else 0
        recent_results.append({
            "exam": result.exam.exam_name,
            "score": result.score,
            "total_questions": result.total_questions,
            "percentage": round(pct, 2)
        })

    return Response({
        "total_exams": total_exams,
        "average_score": round(average_score, 2),
        "recent_results": recent_results
    })