from django.urls import path

from . import views


urlpatterns = [
    path("health", views.health, name="health"),
    path("auth/login", views.login, name="login"),
    path("auth/logout", views.logout, name="logout"),
    path("auth/me", views.me, name="me"),
    path("courses", views.courses, name="courses"),
    path("courses/<int:course_id>", views.course_detail, name="course-detail"),
    path("courses/<int:course_id>/availability", views.course_availability, name="course-availability"),
    path("courses/<int:course_id>/enroll", views.course_enroll, name="course-enroll"),
    path("courses/<int:course_id>/unenroll", views.course_unenroll, name="course-unenroll"),
    path("users", views.users, name="users"),
    path("employees", views.employees, name="employees"),
    path("employees/<int:employee_id>", views.employee_detail, name="employee-detail"),
]
