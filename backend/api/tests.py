from django.test import SimpleTestCase
from django.urls import reverse


class ApiUrlTests(SimpleTestCase):
    def test_health_endpoint_is_registered(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)

    def test_login_endpoint_is_registered(self):
        match = reverse("login")
        self.assertEqual(match, "/api/auth/login")

    def test_course_unenroll_endpoint_is_registered(self):
        match = reverse("course-unenroll", kwargs={"course_id": 1})
        self.assertEqual(match, "/api/courses/1/unenroll")

    def test_users_endpoint_is_registered(self):
        match = reverse("users")
        self.assertEqual(match, "/api/users")
