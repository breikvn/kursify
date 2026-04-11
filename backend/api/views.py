import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .models import ACTIVE_ENROLLMENT_STATUSES, Course, CourseEnrollment, Employee


def _employee_payload(employee: Employee) -> dict:
    return {
        "employee_id": employee.employee_id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "phone_number": employee.phone_number,
        "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
        "job_id": employee.job_id,
        "department_id": employee.department_id,
    }


def _course_payload(course: Course) -> dict:
    return {
        "course_id": course.course_id,
        "title": course.title,
        "description": course.description,
        "starts_at": course.starts_at.isoformat() if course.starts_at else None,
        "ends_at": course.ends_at.isoformat() if course.ends_at else None,
        "max_participants": course.max_participants,
        "location": course.location,
        "status": course.status,
        "active_enrollment_count": course.active_enrollment_count,
        "available_slots": course.available_slots,
    }


def _enrollment_payload(enrollment: CourseEnrollment) -> dict:
    return {
        "enrollment_id": enrollment.enrollment_id,
        "course_id": enrollment.course_id,
        "employee_id": enrollment.employee_id,
        "status": enrollment.status,
        "reserved_until": enrollment.reserved_until.isoformat() if enrollment.reserved_until else None,
        "confirmed_at": enrollment.confirmed_at.isoformat() if enrollment.confirmed_at else None,
        "created_at": enrollment.created_at.isoformat() if enrollment.created_at else None,
    }


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return None


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


@require_GET
def courses(request):
    queryset = Course.objects.all()
    status_filter = request.GET.get("status")
    if status_filter:
        queryset = queryset.filter(status=status_filter.upper())

    return JsonResponse({"results": [_course_payload(course) for course in queryset]})


@require_GET
def course_detail(request, course_id: int):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return JsonResponse({"detail": "Course not found."}, status=404)

    return JsonResponse(_course_payload(course))


@require_GET
def course_availability(request, course_id: int):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return JsonResponse({"detail": "Course not found."}, status=404)

    return JsonResponse(
        {
            "course_id": course.course_id,
            "max_participants": course.max_participants,
            "active_enrollment_count": course.active_enrollment_count,
            "available_slots": course.available_slots,
        }
    )


@require_GET
def employees(request):
    queryset = Employee.objects.all()
    return JsonResponse({"results": [_employee_payload(employee) for employee in queryset]})


@require_GET
def employee_detail(request, employee_id: int):
    try:
        employee = Employee.objects.get(pk=employee_id)
    except Employee.DoesNotExist:
        return JsonResponse({"detail": "Employee not found."}, status=404)

    return JsonResponse(_employee_payload(employee))


@csrf_exempt
def course_enroll(request, course_id: int):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Invalid JSON body."}, status=400)

    employee_id = payload.get("employee_id")
    if not employee_id:
        return JsonResponse({"detail": "employee_id is required."}, status=400)

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return JsonResponse({"detail": "Course not found."}, status=404)

    try:
        employee = Employee.objects.get(pk=employee_id)
    except Employee.DoesNotExist:
        return JsonResponse({"detail": "Employee not found."}, status=404)

    existing = CourseEnrollment.objects.filter(course=course, employee=employee).first()
    if existing and existing.status in ACTIVE_ENROLLMENT_STATUSES:
        return JsonResponse(
            {
                "detail": "Employee already has an active enrollment for this course.",
                "enrollment": _enrollment_payload(existing),
            },
            status=409,
        )

    if course.available_slots <= 0:
        return JsonResponse({"detail": "Course is full."}, status=409)

    if existing:
        existing.status = "PENDING"
        existing.reserved_until = CourseEnrollment.default_reservation_deadline()
        existing.confirmed_at = None
        existing.verification_token = None
        existing.save(update_fields=["status", "reserved_until", "confirmed_at", "verification_token"])
        enrollment = existing
    else:
        enrollment = CourseEnrollment(
            enrollment_id=None,
            course=course,
            employee=employee,
            status="PENDING",
            verification_token=None,
            reserved_until=CourseEnrollment.default_reservation_deadline(),
            confirmed_at=None,
            created_at=None,
        )
        enrollment.save()

    return JsonResponse(_enrollment_payload(enrollment), status=201)
