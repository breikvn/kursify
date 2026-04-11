from django.test import SimpleTestCase
from django.urls import reverse


class ApiUrlTests(SimpleTestCase):
    def test_health_endpoint_is_registered(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
