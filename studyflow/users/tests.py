from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class UserAuthTests(TestCase):
    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Ammu",
                "last_name": "Student",
                "username": "ammu",
                "email": "ammu@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="ammu").exists())

    def test_login_page_renders(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log in to your StudyFlow workspace")
