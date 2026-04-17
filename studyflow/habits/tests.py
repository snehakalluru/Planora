from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from tasks.models import PlannerRequest

from .models import Habit, HabitBadge, HabitCheckIn, MoodLog
from .services import activate_recovery_mode, planner_based_habit_suggestions, refresh_habit_metrics, toggle_habit_completion


class HabitSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="habit-user", password="secret123")
        self.client.login(username="habit-user", password="secret123")

    def test_dashboard_renders_habit_system(self):
        response = self.client.get(reverse("habits_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Habit Ritual Lab")

    def test_toggle_completion_awards_xp_and_badge(self):
        habit = Habit.objects.create(user=self.user, title="Deep Revision")
        checkin = toggle_habit_completion(habit)
        habit.refresh_from_db()
        self.user.refresh_from_db()

        self.assertTrue(checkin.completed)
        self.assertEqual(habit.current_streak, 1)
        self.assertGreater(self.user.habit_profile.xp, 0)
        self.assertTrue(HabitBadge.objects.filter(user=self.user, slug="first-spark").exists())

    def test_recovery_mode_restores_recent_gap(self):
        habit = Habit.objects.create(user=self.user, title="Morning Recall")
        two_days_ago = timezone.localdate() - timedelta(days=2)
        HabitCheckIn.objects.create(habit=habit, date=two_days_ago, completed=True, xp_awarded=10)
        refresh_habit_metrics(habit)

        activate_recovery_mode(habit)
        habit.refresh_from_db()

        self.assertTrue(HabitCheckIn.objects.get(habit=habit, date=timezone.localdate() - timedelta(days=1)).completed)
        self.assertGreaterEqual(habit.current_streak, 2)

    def test_mood_logging_and_planner_suggestions_work(self):
        PlannerRequest.objects.create(
            user=self.user,
            subject="Physics",
            topics="Motion, Force, Energy",
            difficulty="Medium",
            response="Study plan",
        )
        MoodLog.objects.create(user=self.user, mood_score=4, energy_score=5, stress_score=2)

        suggestions = planner_based_habit_suggestions(self.user)

        self.assertTrue(any("active recall" in item["title"] for item in suggestions))
        response = self.client.post(
            reverse("habit_mood_log"),
            {"mood_score": 5, "energy_score": 4, "stress_score": 2, "note": "Ready"},
        )
        self.assertEqual(response.status_code, 200)
