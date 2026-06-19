from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q, Avg
from users.models import Student, Teacher
from exams.models import Exam
from results.models import Result
from django.db import models  # Yeh import zaroori hai
from django.db.models import Count, Q, Avg # Yeh bhi verify kar lo

@api_view(['GET'])
def dashboard_stats(request):
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_subjects = Exam.objects.values('subject').distinct().count()
    total_exams = Exam.objects.count()
    total_results = Result.objects.count()

    stats = Result.objects.aggregate(
        pass_count=Count('id', filter=Q(percentage__gte=40)),
        fail_count=Count('id', filter=Q(percentage__lt=40) | Q(total_questions=0))
    )

    return Response({
        "students": total_students,
        "teachers": total_teachers,
        "subjects": total_subjects,
        "exams": total_exams,
        "results": total_results,
        "pass_count": stats['pass_count'],
        "fail_count": stats['fail_count']
    })


@api_view(['GET'])
def student_dashboard(request, student_id):
    # 1. Pehle results fetch karo
    results = Result.objects.filter(student_id=student_id).select_related('exam', 'exam__subject')
    
    # 2. Variables define karo (YAHI MISSING THA)
    total_exams = results.count()
    
    # Avg percentage calculate karo (agar results hain toh, warna 0)
    avg_score = results.aggregate(avg_perc=models.Avg('percentage'))['avg_perc'] or 0
    avg_score = round(avg_score, 2)

    # 3. Response data return karo
    data = {
        "total_exams": total_exams,
        "average_score": avg_score,
        "recent_results": [
            {
                "exam": res.exam.exam_name,
                "subject_name": res.exam.subject.name if res.exam.subject else "N/A",
                "percentage": res.percentage,
                "status": res.status
            } for res in results
        ]
    }
    return Response(data)


@api_view(['GET'])
def teacher_dashboard(request, teacher_id):
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        
        results = Result.objects.filter(
            exam__class_name=teacher.assigned_classes,
            exam__subject__name=teacher.subject
        ).select_related('student__user', 'exam')

        total_results = results.count()

        counts = results.aggregate(
            pass_c=Count('id', filter=Q(percentage__gte=40)),
            fail_c=Count('id', filter=Q(percentage__lt=40))
        )

        total_exams = Exam.objects.filter(
            class_name=teacher.assigned_classes,
            subject__name=teacher.subject
        ).count()

        top_performers = [
            {"student": r.student.user.email, "percentage": round(r.percentage, 2)}
            for r in results.filter(percentage__gte=75).order_by('-percentage')[:5]
        ]

        weak_students = [
            {"student": r.student.user.email, "percentage": round(r.percentage, 2)}
            for r in results.filter(percentage__lt=40).order_by('percentage')[:5]
        ]

        recent_results = [
            {
                "student": r.student.user.email,
                "exam": r.exam.exam_name,
                "score": r.score,
                "status": r.status
            }
            for r in results.order_by('-id')[:10]
        ]

        unit_tests = []
        mid_terms = []
        final_exams = []

        for r in results:
            raw_exam_type = getattr(r.exam, 'exam_type', 'Unit Test')
            exam_type_lower = str(raw_exam_type).strip().lower()
            exam_name_lower = str(r.exam.exam_name).strip().lower()

            exam_data = {
                "student": r.student.user.email,
                "exam": r.exam.exam_name,
                "score": f"{r.score}/{r.total_questions}",
                "percentage": round(r.percentage, 2)
            }

            if 'unit' in exam_type_lower or 'unit' in exam_name_lower:
                unit_tests.append(exam_data)
            elif 'mid' in exam_type_lower or 'term' in exam_type_lower or 'mid' in exam_name_lower:
                mid_terms.append(exam_data)
            elif 'final' in exam_type_lower or 'final' in exam_name_lower:
                final_exams.append(exam_data)
            else:
                unit_tests.append(exam_data)

        return Response({
            "total_exams": total_exams,
            "students_appeared": total_results,
            "pass_count": counts['pass_c'],
            "fail_count": counts['fail_c'],
            "top_performers": top_performers,
            "weak_students": weak_students,
            "recent_results": recent_results,
            "unit_tests": unit_tests,
            "mid_terms": mid_terms,
            "final_exams": final_exams
        })

    except Teacher.DoesNotExist:
        return Response({"error": "Teacher Not Found"}, status=404)