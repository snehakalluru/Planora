from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import HabitForm, MoodLogForm
from .models import Habit
from .services import (
    activate_recovery_mode,
    build_dashboard_context,
    dashboard_forms,
    habit_response_payload,
    log_mood,
    set_focus_mode,
    toggle_habit_completion,
)


@login_required
def habit_dashboard_view(request):
    context = build_dashboard_context(request.user)
    habit_form, mood_form = dashboard_forms(context.get("today_mood"))
    context["habit_form"] = habit_form
    context["mood_form"] = mood_form
    return render(request, "habits/dashboard.html", context)


@login_required
@require_POST
def habit_create_view(request):
    form = HabitForm(request.POST)
    if form.is_valid():
        habit = form.save(commit=False)
        habit.user = request.user
        habit.save()
        messages.success(request, "Habit engine activated. Your streak, risk, and momentum models are now live.")
    else:
        messages.error(request, "Please correct the habit form and try again.")
    return redirect("habits_dashboard")


@login_required
@require_POST
def habit_toggle_view(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user, is_archived=False)
    checkin = toggle_habit_completion(habit)
    payload = habit_response_payload(habit)
    payload["message"] = "Habit completed for today." if checkin.completed else "Today's completion was reset."
    return JsonResponse(payload)


@login_required
@require_POST
def focus_mode_view(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user, is_archived=False)
    enabled = request.POST.get("enabled", "").lower() == "true"
    set_focus_mode(habit, enabled)
    payload = habit_response_payload(habit)
    payload["message"] = "Focus mode locked in." if enabled else "Focus mode released."
    return JsonResponse(payload)


@login_required
@require_POST
def recovery_mode_view(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user, is_archived=False)
    activate_recovery_mode(habit)
    payload = habit_response_payload(habit)
    payload["message"] = "Recovery mode stabilized your streak."
    return JsonResponse(payload)


@login_required
@require_POST
def mood_log_view(request):
    form = MoodLogForm(request.POST)
    if form.is_valid():
        mood_log = log_mood(
            user=request.user,
            mood_score=form.cleaned_data["mood_score"],
            energy_score=form.cleaned_data["energy_score"],
            stress_score=form.cleaned_data["stress_score"],
            note=form.cleaned_data["note"],
        )
        return JsonResponse(
            {
                "status": "ok",
                "message": "Mood logged for today.",
                "mood": mood_log.get_mood_score_display(),
            }
        )
    return JsonResponse({"status": "error", "errors": form.errors}, status=400)
