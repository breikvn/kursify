import json
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.mail import send_mail

from .models import Course, Employee


def _reservation_deadline_text(reserved_until) -> str:
    if reserved_until is None:
        return "innerhalb von 24 Stunden"
    return reserved_until.astimezone().strftime("%d.%m.%Y um %H:%M Uhr")


def _course_schedule_text(course: Course) -> str:
    starts_at = course.starts_at.astimezone().strftime("%d.%m.%Y %H:%M")
    ends_at = course.ends_at.astimezone().strftime("%d.%m.%Y %H:%M")
    return f"{starts_at} bis {ends_at}"


def _generate_with_ollama(prompt: str) -> str | None:
    model = getattr(settings, "OLLAMA_EMAIL_MODEL", "").strip()
    base_url = getattr(settings, "OLLAMA_BASE_URL", "").strip()
    if not model or not base_url:
        return None

    request = Request(
        f"{base_url.rstrip('/')}/api/generate",
        data=json.dumps(
            {
                "model": model,
                "stream": False,
                "prompt": prompt,
            }
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None

    content = (payload.get("response") or "").strip()
    return content or None


def build_confirmation_email(course: Course, employee: Employee, confirmation_link: str, reserved_until) -> tuple[str, str]:
    deadline_text = _reservation_deadline_text(reserved_until)
    prompt = (
        "Schreibe eine kurze, professionelle deutsche E-Mail zur Kursbestaetigung. "
        "Kein Betreff, nur den Mailtext. "
        f"Empfaenger: {employee.first_name or ''} {employee.last_name}. "
        f"Kurs: {course.title}. "
        f"Zeitfenster: {_course_schedule_text(course)}. "
        f"Ort: {course.location or 'wird noch bekanntgegeben'}. "
        f"Bestaetigungsfrist: {deadline_text}. "
        f"Bestaetigungslink: {confirmation_link}. "
        "Erklaere klar, dass die Reservierung bei fehlender Bestaetigung automatisch verfaellt."
    )
    body = _generate_with_ollama(prompt)

    if body is None:
        body = (
            f"Hallo {(employee.first_name or employee.last_name).strip()},\n\n"
            f"du hast den Kurs \"{course.title}\" ausgewaehlt.\n"
            f"Termin: {_course_schedule_text(course)}\n"
            f"Ort: {course.location or 'wird noch bekanntgegeben'}\n\n"
            f"Bitte bestaetige deine Teilnahme bis spaetestens {deadline_text} ueber diesen Link:\n"
            f"{confirmation_link}\n\n"
            "Wenn du nicht rechtzeitig bestaetigst, wird dein reservierter Platz automatisch wieder freigegeben.\n\n"
            "Viele Gruesse\n"
            "Kursify"
        )

    subject = f"Kursbestaetigung fuer {course.title}"
    return subject, body


def send_confirmation_email(course: Course, employee: Employee, confirmation_link: str, reserved_until) -> None:
    if settings.EMAIL_BACKEND.endswith("smtp.EmailBackend") and not settings.EMAIL_HOST:
        raise RuntimeError("SMTP email backend configured without EMAIL_HOST.")

    subject, body = build_confirmation_email(course, employee, confirmation_link, reserved_until)
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[employee.email],
        fail_silently=False,
    )
