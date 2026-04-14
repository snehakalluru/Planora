from datetime import timedelta
from io import BytesIO

from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .management.commands.send_reminders import Command
from .models import StudyResource, Task


class TaskViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="Testpass123")
        self.other_user = User.objects.create_user(username="other", password="Testpass123")
        self.client.login(username="owner", password="Testpass123")

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_user_only_sees_their_own_tasks(self):
        own_task = Task.objects.create(
            user=self.user,
            title="My Task",
            deadline=timezone.now() + timedelta(days=1),
        )
        Task.objects.create(
            user=self.other_user,
            title="Other Task",
            deadline=timezone.now() + timedelta(days=1),
        )

        response = self.client.get(reverse("task_list"))

        self.assertContains(response, own_task.title)
        self.assertNotContains(response, "Other Task")

    def test_task_toggle_only_changes_current_users_task(self):
        task = Task.objects.create(
            user=self.user,
            title="Toggle Me",
            deadline=timezone.now() + timedelta(days=1),
        )

        response = self.client.post(reverse("task_toggle", args=[task.pk]), follow=True)
        task.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(task.status, Task.STATUS_COMPLETED)
        self.assertIsNotNone(task.completed_at)

    def test_dashboard_shows_alert_for_task_completed_after_deadline(self):
        task = Task.objects.create(
            user=self.user,
            title="Late Submission",
            deadline=timezone.now() - timedelta(hours=2),
        )
        task.status = Task.STATUS_COMPLETED
        task.save()

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "Completed After Deadline")
        self.assertContains(response, "Late Submission")

    def test_editing_deadline_resets_reminder_sent(self):
        task = Task.objects.create(
            user=self.user,
            title="Reminder Task",
            deadline=timezone.now() + timedelta(hours=10),
            reminder_sent=True,
        )

        task.deadline = timezone.now() + timedelta(days=2)
        task.save()
        task.refresh_from_db()

        self.assertFalse(task.reminder_sent)

    def test_chatbot_generates_plan_without_pdf(self):
        response = self.client.post(
            reverse("chatbot"),
            {
                "subject": "Physics",
                "topics": "Motion, Force, Energy",
                "difficulty": "Medium",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Exam Planner for Physics")
        self.assertContains(response, "Recent Planner Requests")

    def test_chatbot_accepts_pdf_upload_and_saves_resource(self):
        pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]/Contents 4 0 R>>endobj\n"
            b"4 0 obj<</Length 44>>stream\nBT /F1 12 Tf 72 120 Td (Algebra notes) Tj ET\nendstream endobj\n"
            b"xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000207 00000 n \n"
            b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n300\n%%EOF"
        )
        upload = SimpleUploadedFile("notes.pdf", pdf_content, content_type="application/pdf")

        response = self.client.post(
            reverse("chatbot"),
            {
                "subject": "Mathematics",
                "topics": "Algebra, Equations",
                "difficulty": "Easy",
                "file": upload,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(StudyResource.objects.filter(user=self.user).exists())


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="studyflow@example.com",
)
class ReminderCommandTests(TestCase):
    def test_send_reminders_sends_for_upcoming_pending_tasks(self):
        user = User.objects.create_user(
            username="mailer",
            password="Testpass123",
            email="mailer@example.com",
            first_name="Mailer",
        )
        task = Task.objects.create(
            user=user,
            title="Upcoming Deadline",
            deadline=timezone.now() + timedelta(hours=4),
            reminder_time=timezone.now() - timedelta(minutes=5),
        )

        Command().handle()
        task.refresh_from_db()

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(task.reminder_sent)
        self.assertIn("Upcoming Deadline", mail.outbox[0].subject)
