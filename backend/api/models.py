from datetime import timedelta

from django.db import connection, models
from django.utils import timezone


ACTIVE_ENROLLMENT_STATUSES = ("PENDING", "CONFIRMED")
USER_ROLES = ("ADMIN", "STUDENT")


class Employee(models.Model):
    employee_id = models.IntegerField(primary_key=True, db_column="EMPLOYEE_ID")
    first_name = models.CharField(max_length=20, db_column="FIRST_NAME", blank=True, null=True)
    last_name = models.CharField(max_length=25, db_column="LAST_NAME")
    email = models.CharField(max_length=25, db_column="EMAIL")
    phone_number = models.CharField(max_length=20, db_column="PHONE_NUMBER", blank=True, null=True)
    hire_date = models.DateField(db_column="HIRE_DATE")
    job_id = models.CharField(max_length=10, db_column="JOB_ID")
    salary = models.DecimalField(max_digits=8, decimal_places=2, db_column="SALARY", blank=True, null=True)
    department_id = models.IntegerField(db_column="DEPARTMENT_ID", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "EMPLOYEES"
        ordering = ["employee_id"]

    def save(self, *args, **kwargs):
        if self.employee_id is None:
            with connection.cursor() as cursor:
                cursor.execute("SELECT EMPLOYEES_SEQ.NEXTVAL FROM DUAL")
                self.employee_id = cursor.fetchone()[0]

        super().save(*args, **kwargs)


class Course(models.Model):
    course_id = models.IntegerField(primary_key=True, db_column="COURSE_ID")
    title = models.CharField(max_length=150, db_column="TITLE")
    description = models.CharField(max_length=1000, db_column="DESCRIPTION", blank=True, null=True)
    starts_at = models.DateTimeField(db_column="STARTS_AT")
    ends_at = models.DateTimeField(db_column="ENDS_AT")
    max_participants = models.IntegerField(db_column="MAX_PARTICIPANTS")
    location = models.CharField(max_length=150, db_column="LOCATION", blank=True, null=True)
    status = models.CharField(max_length=20, db_column="STATUS")

    class Meta:
        managed = False
        db_table = "COURSES"
        ordering = ["starts_at", "course_id"]

    def save(self, *args, **kwargs):
        if self.course_id is None:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COURSES_SEQ.NEXTVAL FROM DUAL")
                self.course_id = cursor.fetchone()[0]

        super().save(*args, **kwargs)

    @property
    def active_enrollment_count(self) -> int:
        return self.enrollments.filter(status__in=ACTIVE_ENROLLMENT_STATUSES).count()

    @property
    def available_slots(self) -> int:
        return max(self.max_participants - self.active_enrollment_count, 0)


class CourseEnrollment(models.Model):
    enrollment_id = models.IntegerField(primary_key=True, db_column="ENROLLMENT_ID")
    course = models.ForeignKey(
        Course,
        on_delete=models.DO_NOTHING,
        db_column="COURSE_ID",
        related_name="enrollments",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.DO_NOTHING,
        db_column="EMPLOYEE_ID",
        related_name="course_enrollments",
    )
    status = models.CharField(max_length=20, db_column="STATUS")
    verification_token = models.CharField(
        max_length=255,
        db_column="VERIFICATION_TOKEN",
        blank=True,
        null=True,
    )
    reserved_until = models.DateTimeField(db_column="RESERVED_UNTIL", blank=True, null=True)
    confirmed_at = models.DateTimeField(db_column="CONFIRMED_AT", blank=True, null=True)
    created_at = models.DateTimeField(db_column="CREATED_AT")

    class Meta:
        managed = False
        db_table = "COURSE_ENROLLMENTS"
        ordering = ["-created_at", "-enrollment_id"]

    def save(self, *args, **kwargs):
        if self.enrollment_id is None:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COURSE_ENROLLMENTS_SEQ.NEXTVAL FROM DUAL")
                self.enrollment_id = cursor.fetchone()[0]

        if self.created_at is None:
            self.created_at = timezone.now()

        super().save(*args, **kwargs)

    @classmethod
    def default_reservation_deadline(cls):
        return timezone.now() + timedelta(hours=24)


class AppUser(models.Model):
    user_id = models.IntegerField(primary_key=True, db_column="USER_ID")
    username = models.CharField(max_length=50, db_column="USERNAME")
    password = models.CharField(max_length=255, db_column="PASSWORD")
    role = models.CharField(max_length=20, db_column="ROLE")
    display_name = models.CharField(max_length=100, db_column="DISPLAY_NAME", blank=True, null=True)
    auth_token = models.CharField(max_length=255, db_column="AUTH_TOKEN", blank=True, null=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.DO_NOTHING,
        db_column="EMPLOYEE_ID",
        related_name="app_users",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(db_column="CREATED_AT")

    class Meta:
        managed = False
        db_table = "APP_USERS"
        ordering = ["user_id"]

    def save(self, *args, **kwargs):
        if self.user_id is None:
            with connection.cursor() as cursor:
                cursor.execute("SELECT APP_USERS_SEQ.NEXTVAL FROM DUAL")
                self.user_id = cursor.fetchone()[0]

        if self.created_at is None:
            self.created_at = timezone.now()

        super().save(*args, **kwargs)
