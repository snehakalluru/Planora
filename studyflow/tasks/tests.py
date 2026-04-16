from datetime import timedelta
from io import BytesIO
from unittest.mock import Mock, patch

import requests
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from . import chatbot
from .management.commands.send_reminders import Command
from .models import DailyTimetableTask, PlannerRequest, StudyResource, Task


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

    @patch("tasks.views.generate_exam_plan")
    def test_chatbot_generates_plan_without_pdf(self, mock_generate_exam_plan):
        mock_generate_exam_plan.return_value = (
            "IMPORTANT TOPICS\n"
            "- Motion\n"
            "\n"
            "EXAM-LEVEL QUESTIONS\n"
            "- Explain Newton's laws with an example."
        )

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
        self.assertContains(response, "IMPORTANT TOPICS")
        self.assertContains(response, "Explain Newton&#x27;s laws with an example.")
        self.assertContains(response, "Recent Planner Requests")
        mock_generate_exam_plan.assert_called_once_with(
            "Physics",
            "Motion, Force, Energy",
            "Medium",
            "",
        )

    @patch("tasks.views.generate_exam_plan")
    def test_chatbot_accepts_pdf_upload_and_saves_resource(self, mock_generate_exam_plan):
        mock_generate_exam_plan.return_value = "REVISION NOTES\n- Algebra identities"
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
        self.assertContains(response, "REVISION NOTES")

    @patch("tasks.views.generate_exam_plan")
    def test_chatbot_shows_latest_generated_plan_in_response_panel(self, mock_generate_exam_plan):
        PlannerRequest.objects.create(
            user=self.user,
            subject="Chemistry",
            topics="Atoms, Bonds",
            difficulty="Easy",
            response="OLD PLAN",
        )
        mock_generate_exam_plan.return_value = "NEW PLAN"

        response = self.client.post(
            reverse("chatbot"),
            {
                "subject": "Physics",
                "topics": "Motion, Force",
                "difficulty": "Medium",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NEW PLAN")
        self.assertContains(response, "Physics")
        requests = list(response.context["requests"])
        self.assertTrue(all(req.response != "NEW PLAN" for req in requests))

    def test_chatbot_get_shows_empty_state_without_fresh_plan(self):
        response = self.client.get(reverse("chatbot"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No planner generated yet")
        self.assertEqual(response.context["plan"], "")
        self.assertIsNone(response.context["active_planner_request"])

    def test_chatbot_page_includes_timetable_section(self):
        DailyTimetableTask.objects.create(
            user=self.user,
            title="Morning Revision",
            start_time="07:00",
            end_time="08:00",
            description="Review formulas",
        )

        response = self.client.get(reverse("chatbot"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Daily Timetable")
        self.assertContains(response, "Morning Revision")

    @patch("tasks.views.generate_exam_plan")
    def test_chatbot_does_not_call_api_when_form_is_invalid(self, mock_generate_exam_plan):
        response = self.client.post(
            reverse("chatbot"),
            {
                "subject": "",
                "topics": "",
                "difficulty": "Medium",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        mock_generate_exam_plan.assert_not_called()

    @patch("tasks.views.generate_exam_plan")
    def test_chatbot_shows_api_failure_message_without_crashing(self, mock_generate_exam_plan):
        mock_generate_exam_plan.side_effect = RuntimeError("Unable to generate plan. Please try again.")

        response = self.client.post(
            reverse("chatbot"),
            {
                "subject": "Physics",
                "topics": "Motion",
                "difficulty": "Medium",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unable to generate plan. Please try again.")
        self.assertContains(response, "No planner generated yet")
        self.assertFalse(
            PlannerRequest.objects.filter(user=self.user, subject="Physics", topics="Motion").exists()
        )


class ChatbotServiceTests(TestCase):
    @patch.object(chatbot, "OPENROUTER_API_KEY", "")
    def test_call_openrouter_requires_api_key(self):
        with self.assertRaisesMessage(RuntimeError, "Unable to generate plan. Please try again."):
            chatbot._call_openrouter("test prompt")

    @patch("tasks.chatbot.requests.post")
    @patch.object(chatbot, "OPENROUTER_API_KEY", "test-key")
    def test_call_openrouter_raises_runtime_error_on_http_failure(self, mock_post):
        mock_post.side_effect = requests.RequestException("boom")

        with self.assertRaisesMessage(RuntimeError, "Unable to generate plan. Please try again."):
            chatbot._call_openrouter("test prompt")

    @patch("tasks.chatbot.requests.post")
    @patch.object(chatbot, "OPENROUTER_API_KEY", "test-key")
    def test_call_openrouter_raises_runtime_error_on_missing_content(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"choices": [{"message": {}}]}
        mock_post.return_value = mock_response

        with self.assertRaisesMessage(RuntimeError, "Unable to generate plan. Please try again."):
            chatbot._call_openrouter("test prompt")

    @patch("tasks.chatbot.requests.post")
    @patch.object(chatbot, "OPENROUTER_API_KEY", "test-key")
    def test_call_openrouter_returns_response_text(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Generated plan text"}}]
        }
        mock_post.return_value = mock_response

        self.assertEqual(chatbot._call_openrouter("test prompt"), "Generated plan text")

    @patch("tasks.chatbot.requests.post")
    @patch.object(chatbot, "OPENROUTER_API_KEY", "test-key")
    def test_call_openrouter_supports_list_content(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "text", "text": "Part one"},
                            {"type": "text", "text": "Part two"},
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        self.assertEqual(chatbot._call_openrouter("test prompt"), "Part one\nPart two")


class DailyTimetableViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="planner", password="Testpass123")
        self.other_user = User.objects.create_user(username="otherplanner", password="Testpass123")
        self.client.login(username="planner", password="Testpass123")

    def test_timetable_lists_only_current_users_tasks_in_time_order(self):
        DailyTimetableTask.objects.create(
            user=self.user,
            title="Practice coding",
            start_time="14:00",
            end_time="15:00",
        )
        early_task = DailyTimetableTask.objects.create(
            user=self.user,
            title="Wake up",
            start_time="06:00",
            end_time="06:30",
        )
        DailyTimetableTask.objects.create(
            user=self.other_user,
            title="Other user task",
            start_time="08:00",
            end_time="09:00",
        )

        response = self.client.get(reverse("timetable"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wake up")
        self.assertNotContains(response, "Other user task")
        tasks = list(response.context["timetable_tasks"])
        self.assertEqual(tasks[0], early_task)

    def test_timetable_create_saves_task(self):
        response = self.client.post(
            reverse("timetable_task_add"),
            {
                "title": "Study DBMS",
                "start_time": "07:00",
                "end_time": "09:00",
                "description": "Normalization and transactions",
                "completed": "",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(DailyTimetableTask.objects.filter(user=self.user, title="Study DBMS").exists())
        self.assertContains(response, "Timetable task added successfully.")

    def test_timetable_edit_updates_task(self):
        task = DailyTimetableTask.objects.create(
            user=self.user,
            title="Break",
            start_time="10:00",
            end_time="10:30",
        )

        response = self.client.post(
            reverse("timetable_task_edit", args=[task.pk]),
            {
                "title": "Short Break",
                "start_time": "10:15",
                "end_time": "10:45",
                "description": "Tea time",
                "completed": "on",
            },
            follow=True,
        )
        task.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(task.title, "Short Break")
        self.assertTrue(task.completed)

    def test_timetable_delete_removes_task(self):
        task = DailyTimetableTask.objects.create(
            user=self.user,
            title="Delete me",
            start_time="11:00",
            end_time="12:00",
        )

        response = self.client.post(reverse("timetable_task_delete", args=[task.pk]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(DailyTimetableTask.objects.filter(pk=task.pk).exists())

    def test_timetable_toggle_changes_completed_state(self):
        task = DailyTimetableTask.objects.create(
            user=self.user,
            title="Complete me",
            start_time="13:00",
            end_time="14:00",
        )

        response = self.client.post(reverse("timetable_task_toggle", args=[task.pk]), follow=True)
        task.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(task.completed)

    def test_timetable_form_validates_end_time_after_start_time(self):
        response = self.client.post(
            reverse("timetable_task_add"),
            {
                "title": "Invalid slot",
                "start_time": "15:00",
                "end_time": "14:00",
                "description": "",
                "completed": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "End time must be later than start time.")

    def test_timetable_form_requires_title_and_times(self):
        response = self.client.post(
            reverse("timetable_task_add"),
            {
                "title": "",
                "start_time": "",
                "end_time": "",
                "description": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.", count=3)


class ExamPlannerFormTests(TestCase):
    def test_exam_planner_form_allows_missing_file(self):
        from .forms import ExamPlannerForm

        form = ExamPlannerForm(
            data={
                "subject": "Maths",
                "topics": "Algebra, Calculus",
                "difficulty": "Easy",
            }
        )

        self.assertTrue(form.is_valid())

    def test_exam_planner_form_rejects_non_pdf_upload(self):
        from .forms import ExamPlannerForm

        upload = SimpleUploadedFile("notes.txt", b"text", content_type="text/plain")
        form = ExamPlannerForm(
            data={
                "subject": "Maths",
                "topics": "Algebra, Calculus",
                "difficulty": "Easy",
            },
            files={"file": upload},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("Only PDF files are allowed.", form.errors["file"])


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
