from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class HabitProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="habit_profile")
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    resilience_score = models.PositiveIntegerField(default=0)
    last_activity_on = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"Habit profile for {self.user.username}"

    @property
    def next_level_xp(self):
        return self.level * 120

    @property
    def progress_to_next_level(self):
        previous_threshold = (self.level - 1) * 120
        span = max(120, self.next_level_xp - previous_threshold)
        return min(100, int(((self.xp - previous_threshold) / span) * 100))


class MoodLog(models.Model):
    MOOD_LOW = 1
    MOOD_STEADY = 2
    MOOD_GOOD = 3
    MOOD_GREAT = 4
    MOOD_PEAK = 5

    MOOD_CHOICES = [
        (MOOD_LOW, "Low"),
        (MOOD_STEADY, "Steady"),
        (MOOD_GOOD, "Good"),
        (MOOD_GREAT, "Great"),
        (MOOD_PEAK, "Peak"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habit_mood_logs")
    date = models.DateField(default=timezone.localdate)
    mood_score = models.PositiveSmallIntegerField(choices=MOOD_CHOICES, default=MOOD_GOOD)
    energy_score = models.PositiveSmallIntegerField(default=3)
    stress_score = models.PositiveSmallIntegerField(default=3)
    note = models.CharField(max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user.username} mood on {self.date}"


class Habit(models.Model):
    CATEGORY_STUDY = "Study"
    CATEGORY_HEALTH = "Health"
    CATEGORY_MINDSET = "Mindset"
    CATEGORY_ROUTINE = "Routine"

    CATEGORY_CHOICES = [
        (CATEGORY_STUDY, "Study"),
        (CATEGORY_HEALTH, "Health"),
        (CATEGORY_MINDSET, "Mindset"),
        (CATEGORY_ROUTINE, "Routine"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    title = models.CharField(max_length=140)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_STUDY)
    cue = models.CharField(max_length=160, blank=True)
    why = models.CharField(max_length=220, blank=True)
    target_minutes = models.PositiveIntegerField(default=20)
    difficulty_level = models.PositiveSmallIntegerField(default=1)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    completions_count = models.PositiveIntegerField(default=0)
    momentum_score = models.PositiveSmallIntegerField(default=0)
    risk_score = models.PositiveSmallIntegerField(default=0)
    consistency_score = models.PositiveSmallIntegerField(default=0)
    insight = models.CharField(max_length=220, blank=True)
    last_completed_on = models.DateField(blank=True, null=True)
    focus_mode = models.BooleanField(default=False)
    recovery_mode = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-momentum_score", "-current_streak", "title"]
        indexes = [
            models.Index(fields=["user", "is_archived"]),
            models.Index(fields=["user", "risk_score"]),
        ]
        unique_together = ("user", "title")

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def progress_percent(self):
        return min(100, self.consistency_score)

    @property
    def risk_band(self):
        if self.risk_score >= 75:
            return "Critical"
        if self.risk_score >= 50:
            return "Watch"
        return "Stable"

    @property
    def difficulty_label(self):
        labels = {
            1: "Spark",
            2: "Build",
            3: "Rise",
            4: "Elite",
            5: "Mastery",
        }
        return labels.get(self.difficulty_level, "Rise")


class HabitCheckIn(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="checkins")
    date = models.DateField(default=timezone.localdate)
    completed = models.BooleanField(default=False)
    effort_score = models.PositiveSmallIntegerField(default=3)
    xp_awarded = models.PositiveIntegerField(default=0)
    recovery_used = models.BooleanField(default=False)
    note = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        unique_together = ("habit", "date")
        indexes = [
            models.Index(fields=["habit", "date"]),
            models.Index(fields=["habit", "completed"]),
        ]

    def __str__(self):
        return f"{self.habit.title} on {self.date}"


class HabitBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habit_badges")
    slug = models.SlugField(max_length=60)
    label = models.CharField(max_length=80)
    description = models.CharField(max_length=180)
    icon = models.CharField(max_length=8, default="🏅")
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-unlocked_at"]
        unique_together = ("user", "slug")

    def __str__(self):
        return f"{self.label} for {self.user.username}"

