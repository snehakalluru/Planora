from django.contrib import admin

from .models import Habit, HabitBadge, HabitCheckIn, HabitProfile, MoodLog


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "current_streak", "momentum_score", "risk_score", "focus_mode")
    list_filter = ("category", "focus_mode", "is_archived")
    search_fields = ("title", "user__username", "cue")


@admin.register(HabitCheckIn)
class HabitCheckInAdmin(admin.ModelAdmin):
    list_display = ("habit", "date", "completed", "xp_awarded", "recovery_used")
    list_filter = ("completed", "recovery_used", "date")
    search_fields = ("habit__title", "habit__user__username")


admin.site.register(HabitProfile)
admin.site.register(HabitBadge)
admin.site.register(MoodLog)
