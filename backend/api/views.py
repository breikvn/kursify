from __future__ import annotations

import json
import secrets
from datetime import datetime

from django.db.models import Q
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .enrollment_notifications import send_confirmation_email
from .models import ACTIVE_ENROLLMENT_STATUSES, AppUser, Course, CourseEnrollment, Employee


def _employee_payload(employee: Employee | None) -> dict | None:
    if employee is None:
        return None

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


def _user_payload(user: AppUser, include_token: bool = False) -> dict:
    payload = {
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role,
        "display_name": user.display_name,
        "employee": _employee_payload(user.employee),
    }
    if include_token:
        payload["token"] = user.auth_token
    return payload


def _current_enrollments_for(user: AppUser | None) -> dict[int, CourseEnrollment]:
    if user is None or user.employee is None:
        return {}

    enrollments = CourseEnrollment.objects.filter(
        employee=user.employee,
        status__in=ACTIVE_ENROLLMENT_STATUSES,
    )
    return {enrollment.course_id: enrollment for enrollment in enrollments}


def _course_payload(course: Course, enrollment_by_course_id: dict[int, CourseEnrollment] | None = None) -> dict:
    enrollment = (enrollment_by_course_id or {}).get(course.course_id)
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
        "selected": enrollment is not None,
        "enrollment_status": enrollment.status if enrollment else None,
        "reserved_until": enrollment.reserved_until.isoformat() if enrollment and enrollment.reserved_until else None,
        "confirmed_at": enrollment.confirmed_at.isoformat() if enrollment and enrollment.confirmed_at else None,
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


def _json_error(detail: str, status: int):
    return JsonResponse({"detail": detail}, status=status)


def _authorization_token(request) -> str | None:
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return None


def _current_user(request) -> AppUser | None:
    token = _authorization_token(request)
    if not token:
        return None
    return AppUser.objects.select_related("employee").filter(auth_token=token).first()


def _require_auth(request):
    user = _current_user(request)
    if user is None:
        return None, _json_error("Authentication required.", 401)
    return user, None


def _require_admin(request):
    user, error = _require_auth(request)
    if error:
        return None, error
    if user.role != "ADMIN":
        return None, _json_error("Admin access required.", 403)
    return user, None


def _require_student(request):
    user, error = _require_auth(request)
    if error:
        return None, error
    if user.role != "STUDENT" or user.employee is None:
        return None, _json_error("Student access required.", 403)
    return user, None


def _parse_datetime(value: str | None):
    if not value:
        return None

    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _cleanup_expired_reservations(course: Course | None = None):
    filters = Q(status="PENDING", reserved_until__isnull=False, reserved_until__lt=timezone.now())
    if course is not None:
        filters &= Q(course=course)

    CourseEnrollment.objects.filter(filters).update(
        status="CANCELLED",
        verification_token=None,
        reserved_until=None,
    )


def _confirmation_link(request, token: str) -> str:
    return request.build_absolute_uri(f"/api/enrollments/confirm?token={token}")


def _confirmation_response(title: str, detail: str, status: int = 200) -> HttpResponse:
    return HttpResponse(
        (
            "<!doctype html><html lang='de'><head><meta charset='utf-8'>"
            f"<title>{title}</title>"
            "<style>body{font-family:Arial,sans-serif;background:#f4f1ea;color:#16303b;"
            "padding:40px}main{max-width:640px;margin:0 auto;background:#fff;border-radius:18px;"
            "padding:28px;box-shadow:0 12px 32px rgba(20,45,56,.08)}h1{margin-top:0}</style>"
            f"</head><body><main><h1>{title}</h1><p>{detail}</p></main></body></html>"
        ),
        status=status,
        content_type="text/html; charset=utf-8",
    )


@csrf_exempt
def health(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    return JsonResponse({"status": "ok"})


@csrf_exempt
def login(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    payload = _parse_json_body(request)
    if payload is None:
        return _json_error("Invalid JSON body.", 400)

    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    if not username or not password:
        return _json_error("username and password are required.", 400)

    user = AppUser.objects.select_related("employee").filter(username=username).first()
    if user is None or user.password != password:
        return _json_error("Invalid username or password.", 401)

    user.auth_token = secrets.token_urlsafe(32)
    user.save(update_fields=["auth_token"])
    return JsonResponse(_user_payload(user, include_token=True))


@csrf_exempt
def logout(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    user, error = _require_auth(request)
    if error:
        return error

    user.auth_token = None
    user.save(update_fields=["auth_token"])
    return JsonResponse({"detail": "Logged out."})


@csrf_exempt
def me(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    user, error = _require_auth(request)
    if error:
        return error

    return JsonResponse(_user_payload(user))


@csrf_exempt
def courses(request):
    if request.method == "GET":
        current_user, error = _require_auth(request)
        if error:
            return error

        _cleanup_expired_reservations()
        queryset = Course.objects.all()
        status_filter = request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())

        enrollment_by_course_id = _current_enrollments_for(current_user)
        return JsonResponse({"results": [_course_payload(course, enrollment_by_course_id) for course in queryset]})

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    _, error = _require_admin(request)
    if error:
        return error

    payload = _parse_json_body(request)
    if payload is None:
        return _json_error("Invalid JSON body.", 400)

    title = (payload.get("title") or "").strip()
    starts_at = _parse_datetime(payload.get("starts_at"))
    ends_at = _parse_datetime(payload.get("ends_at"))
    max_participants = payload.get("max_participants")

    if not title or starts_at is None or ends_at is None or max_participants is None:
        return _json_error("title, starts_at, ends_at and max_participants are required.", 400)

    if ends_at <= starts_at:
        return _json_error("ends_at must be after starts_at.", 400)

    try:
        max_participants = int(max_participants)
    except (TypeError, ValueError):
        return _json_error("max_participants must be a number.", 400)

    course = Course(
        course_id=None,
        title=title,
        description=(payload.get("description") or "").strip() or None,
        starts_at=starts_at,
        ends_at=ends_at,
        max_participants=max_participants,
        location=(payload.get("location") or "").strip() or None,
        status=(payload.get("status") or "OPEN").upper(),
    )
    course.save()
    return JsonResponse(_course_payload(course), status=201)


@csrf_exempt
def course_detail(request, course_id: int):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return _json_error("Course not found.", 404)

    _cleanup_expired_reservations(course)
    current_user = _current_user(request)
    enrollment_by_course_id = _current_enrollments_for(current_user)
    return JsonResponse(_course_payload(course, enrollment_by_course_id))


@csrf_exempt
def course_availability(request, course_id: int):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return _json_error("Course not found.", 404)

    _cleanup_expired_reservations(course)
    return JsonResponse(
        {
            "course_id": course.course_id,
            "max_participants": course.max_participants,
            "active_enrollment_count": course.active_enrollment_count,
            "available_slots": course.available_slots,
        }
    )


@csrf_exempt
def users(request):
    if request.method == "GET":
        _, error = _require_admin(request)
        if error:
            return error

        queryset = AppUser.objects.select_related("employee").all()
        return JsonResponse({"results": [_user_payload(user) for user in queryset]})

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    _, error = _require_admin(request)
    if error:
        return error

    payload = _parse_json_body(request)
    if payload is None:
        return _json_error("Invalid JSON body.", 400)

    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    role = (payload.get("role") or "STUDENT").upper()

    if not username or not password:
        return _json_error("username and password are required.", 400)

    if role not in {"ADMIN", "STUDENT"}:
        return _json_error("role must be ADMIN or STUDENT.", 400)

    if AppUser.objects.filter(username=username).exists():
        return _json_error("Username already exists.", 409)

    try:
        with transaction.atomic():
            employee = None
            if role == "STUDENT":
                first_name = (payload.get("first_name") or "").strip() or None
                last_name = (payload.get("last_name") or "").strip()
                email = (payload.get("email") or "").strip()

                if not last_name or not email:
                    return _json_error("Student users require last_name and email.", 400)

                employee = Employee(
                    employee_id=None,
                    first_name=first_name,
                    last_name=last_name,
                    email=email[:25],
                    phone_number=(payload.get("phone_number") or "").strip() or None,
                    hire_date=timezone.localdate(),
                    job_id=(payload.get("job_id") or "IT_PROG").strip() or "IT_PROG",
                    salary=payload.get("salary") or 4500,
                    department_id=payload.get("department_id") or 60,
                )
                employee.save()

            display_name = (payload.get("display_name") or "").strip() or username
            if employee is not None:
                display_name = f"{employee.first_name or ''} {employee.last_name}".strip()

            user = AppUser(
                user_id=None,
                username=username,
                password=password,
                role=role,
                display_name=display_name,
                auth_token=None,
                employee=employee,
                created_at=None,
            )
            user.save()
    except IntegrityError:
        return _json_error("Could not create user.", 400)

    return JsonResponse(_user_payload(user), status=201)


@csrf_exempt
def employees(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    _, error = _require_admin(request)
    if error:
        return error

    queryset = Employee.objects.all()
    return JsonResponse({"results": [_employee_payload(employee) for employee in queryset]})


@csrf_exempt
def employee_detail(request, employee_id: int):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    _, error = _require_admin(request)
    if error:
        return error

    try:
        employee = Employee.objects.get(pk=employee_id)
    except Employee.DoesNotExist:
        return _json_error("Employee not found.", 404)

    return JsonResponse(_employee_payload(employee))


@csrf_exempt
def course_enroll(request, course_id: int):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    current_user, error = _require_student(request)
    if error:
        return error

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return _json_error("Course not found.", 404)

    _cleanup_expired_reservations(course)
    existing = CourseEnrollment.objects.filter(course=course, employee=current_user.employee).first()
    if existing and existing.status in ACTIVE_ENROLLMENT_STATUSES:
        return JsonResponse(
            {
                "detail": "Employee already has an active enrollment for this course.",
                "enrollment": _enrollment_payload(existing),
            },
            status=409,
        )

    if course.available_slots <= 0:
        return _json_error("Course is full.", 409)

    token = secrets.token_urlsafe(32)
    reserved_until = CourseEnrollment.default_reservation_deadline()

    try:
        with transaction.atomic():
            if existing:
                existing.status = "PENDING"
                existing.reserved_until = reserved_until
                existing.confirmed_at = None
                existing.verification_token = token
                existing.save(update_fields=["status", "reserved_until", "confirmed_at", "verification_token"])
                enrollment = existing
            else:
                enrollment = CourseEnrollment(
                    enrollment_id=None,
                    course=course,
                    employee=current_user.employee,
                    status="PENDING",
                    verification_token=token,
                    reserved_until=reserved_until,
                    confirmed_at=None,
                    created_at=None,
                )
                enrollment.save()

            send_confirmation_email(
                course=course,
                employee=current_user.employee,
                confirmation_link=_confirmation_link(request, token),
                reserved_until=reserved_until,
            )
    except Exception:
        return _json_error("Confirmation email could not be sent.", 502)

    return JsonResponse(
        {
            "detail": "Reservation created. Please confirm via email within 24 hours.",
            "enrollment": _enrollment_payload(enrollment),
        },
        status=201,
    )


@csrf_exempt
def course_unenroll(request, course_id: int):
    if request.method not in {"POST", "DELETE"}:
        return HttpResponseNotAllowed(["POST", "DELETE"])

    current_user, error = _require_student(request)
    if error:
        return error

    _cleanup_expired_reservations()
    enrollment = CourseEnrollment.objects.filter(
        course_id=course_id,
        employee=current_user.employee,
        status__in=ACTIVE_ENROLLMENT_STATUSES,
    ).first()
    if enrollment is None:
        return _json_error("Active enrollment not found.", 404)

    enrollment.status = "CANCELLED"
    enrollment.reserved_until = None
    enrollment.verification_token = None
    enrollment.confirmed_at = None
    enrollment.save(update_fields=["status", "reserved_until", "verification_token", "confirmed_at"])
    return JsonResponse(_enrollment_payload(enrollment))


@csrf_exempt
def confirm_enrollment(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    token = (request.GET.get("token") or "").strip()
    if not token:
        return _confirmation_response("Ungueltiger Link", "Der Bestaetigungslink enthaelt kein Token.", status=400)

    enrollment = (
        CourseEnrollment.objects.select_related("course", "employee")
        .filter(verification_token=token)
        .first()
    )
    if enrollment is None:
        return _confirmation_response(
            "Link nicht gueltig",
            "Diese Reservierung wurde bereits bestaetigt, storniert oder ist nicht mehr vorhanden.",
            status=404,
        )

    if enrollment.status != "PENDING":
        return _confirmation_response(
            "Reservierung nicht offen",
            "Diese Reservierung ist nicht mehr im bestaetigbaren Status.",
            status=409,
        )

    if enrollment.reserved_until and enrollment.reserved_until < timezone.now():
        enrollment.status = "CANCELLED"
        enrollment.reserved_until = None
        enrollment.verification_token = None
        enrollment.confirmed_at = None
        enrollment.save(update_fields=["status", "reserved_until", "verification_token", "confirmed_at"])
        return _confirmation_response(
            "Frist abgelaufen",
            "Die 24-Stunden-Frist ist abgelaufen. Der reservierte Platz wurde wieder freigegeben.",
            status=410,
        )

    enrollment.status = "CONFIRMED"
    enrollment.confirmed_at = timezone.now()
    enrollment.reserved_until = None
    enrollment.verification_token = None
    enrollment.save(update_fields=["status", "confirmed_at", "reserved_until", "verification_token"])
    return _confirmation_response(
        "Teilnahme bestaetigt",
        f"Dein Platz fuer den Kurs \"{enrollment.course.title}\" ist jetzt verbindlich bestaetigt.",
    )
