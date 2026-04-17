from django.contrib import admin

from .models import DailyTimetableTask, StudyResource, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "deadline", "reminder_time", "priority", "status", "created_at")
    list_filter = ("priority", "status", "created_at", "reminder_sent")
    search_fields = ("title", "description", "user__username", "user__email")


@admin.register(StudyResource)
class StudyResourceAdmin(admin.ModelAdmin):
    list_display = ("user", "file", "uploaded_at")
    search_fields = ("user__username", "user__email", "file")


@admin.register(DailyTimetableTask)
class DailyTimetableTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "start_time", "end_time", "completed", "updated_at")
    list_filter = ("completed", "created_at", "updated_at")
    search_fields = ("title", "description", "user__username", "user__email")
