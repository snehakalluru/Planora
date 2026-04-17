from django.urls import path

from . import views


urlpatterns = [
    path("", views.habit_dashboard_view, name="habits_dashboard"),
    path("create/", views.habit_create_view, name="habit_create"),
    path("<int:pk>/toggle/", views.habit_toggle_view, name="habit_toggle"),
    path("<int:pk>/focus-mode/", views.focus_mode_view, name="habit_focus_mode"),
    path("<int:pk>/recovery-mode/", views.recovery_mode_view, name="habit_recovery_mode"),
    path("mood/log/", views.mood_log_view, name="habit_mood_log"),
]
