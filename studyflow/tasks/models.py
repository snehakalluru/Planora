from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
# PlannerRequest model for chatbot history
class PlannerRequest(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="planner_requests")
    subject = models.CharField(max_length=150)
    topics = models.TextField()
    difficulty = models.CharField(max_length=20)
    response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.difficulty}) - {self.created_at:%Y-%m-%d %H:%M}"
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Task(models.Model):
    PRIORITY_HIGH = "High"
    PRIORITY_MEDIUM = "Medium"
    PRIORITY_LOW = "Low"

    STATUS_PENDING = "Pending"
    STATUS_COMPLETED = "Completed"

    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, "High"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_LOW, "Low"),
    ]

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    reminder_time = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["deadline", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def save(self, *args, **kwargs):
        if not self.reminder_time and self.deadline:
            self.reminder_time = self.deadline - timedelta(hours=2)
        if self.pk:
            previous_task = Task.objects.filter(pk=self.pk).only(
                "deadline", "reminder_time", "status", "completed_at"
            ).first()
            if previous_task and previous_task.deadline != self.deadline:
                self.reminder_sent = False
            if previous_task and previous_task.reminder_time != self.reminder_time:
                self.reminder_sent = False
            if previous_task and previous_task.status == self.STATUS_COMPLETED and self.status == self.STATUS_PENDING:
                self.reminder_sent = False
                self.completed_at = None
            if previous_task and previous_task.status != self.STATUS_COMPLETED and self.status == self.STATUS_COMPLETED:
                self.completed_at = self.completed_at or timezone.now()
        elif self.status == self.STATUS_COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.status == self.STATUS_PENDING and self.deadline < timezone.now()

    @property
    def is_due_soon(self):
        now = timezone.now()
        return self.status == self.STATUS_PENDING and now <= self.deadline <= now + timedelta(days=3)

    @property
    def reminder_due(self):
        return bool(self.reminder_time and self.reminder_time <= timezone.now() and not self.reminder_sent)

    @property
    def was_completed_late(self):
        return bool(
            self.status == self.STATUS_COMPLETED
            and self.completed_at
            and self.deadline
            and self.completed_at > self.deadline
        )


class StudyResource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="study_resources")
    file = models.FileField(upload_to="study_resources/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.user.username} resource {self.file.name}"


class DailyTimetableTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_timetable_tasks")
    title = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time", "end_time", "created_at"]

    def __str__(self):
        return f"{self.title} ({self.user.username})"
