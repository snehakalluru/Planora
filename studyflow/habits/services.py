from collections import Counter, defaultdict
from datetime import timedelta

from django.db.models import Prefetch, Sum
from django.utils import timezone

from tasks.models import PlannerRequest

from .models import Habit, HabitBadge, HabitCheckIn, HabitProfile, MoodLog


BADGE_DEFINITIONS = [
    {
        "slug": "first-spark",
        "label": "First Spark",
        "description": "Completed the first habit check-in.",
        "icon": "✨",
    },
    {
        "slug": "focus-guardian",
        "label": "Focus Guardian",
        "description": "Activated focus mode on a habit.",
        "icon": "🎯",
    },
    {
        "slug": "streak-7",
        "label": "7-Day Flame",
        "description": "Held a streak for 7 days.",
        "icon": "🔥",
    },
    {
        "slug": "streak-21",
        "label": "21-Day Orbit",
        "description": "Held a streak for 21 days.",
        "icon": "🌌",
    },
    {
        "slug": "mood-cartographer",
        "label": "Mood Cartographer",
        "description": "Logged mood patterns across 5 days.",
        "icon": "🧠",
    },
    {
        "slug": "comeback-kid",
        "label": "Comeback Kid",
        "description": "Used recovery mode to stabilize momentum.",
        "icon": "🛟",
    },
]


def _profile_for(user):
    profile, _ = HabitProfile.objects.get_or_create(user=user)
    return profile


def _refresh_profile(profile):
    profile.level = max(1, (profile.xp // 120) + 1)
    profile.save(update_fields=["level", "xp", "resilience_score", "last_activity_on"])
    return profile


def _dates_from_checkins(checkins):
    return sorted([item.date for item in checkins if item.completed])


def _current_streak_from_dates(completed_dates):
    if not completed_dates:
        return 0
    streak = 1
    previous = completed_dates[-1]
    for current in reversed(completed_dates[:-1]):
        if (previous - current).days == 1:
            streak += 1
            previous = current
            continue
        break
    return streak


def _longest_streak_from_dates(completed_dates):
    if not completed_dates:
        return 0
    longest = 1
    current_run = 1
    for index in range(1, len(completed_dates)):
        if (completed_dates[index] - completed_dates[index - 1]).days == 1:
            current_run += 1
        else:
            longest = max(longest, current_run)
            current_run = 1
    return max(longest, current_run)


def _completion_ratio(checkins, window=14):
    today = timezone.localdate()
    window_start = today - timedelta(days=window - 1)
    filtered = [item for item in checkins if item.date >= window_start]
    if not filtered:
        return 0
    completed_count = sum(1 for item in filtered if item.completed)
    return int((completed_count / window) * 100)


def _mood_correlation_message(habit, recent_checkins, mood_map):
    completed_days = []
    missed_days = []
    for checkin in recent_checkins:
        mood = mood_map.get(checkin.date)
        if not mood:
            continue
        if checkin.completed:
            completed_days.append(mood.mood_score)
        else:
            missed_days.append(mood.mood_score)

    if completed_days and missed_days:
        completed_average = sum(completed_days) / len(completed_days)
        missed_average = sum(missed_days) / len(missed_days)
        if completed_average >= missed_average + 0.8:
            return f"Best follow-through appears on higher-mood days. Build {habit.title.lower()} right after an energy lift."
        if missed_average >= completed_average + 0.8:
            return "You still show up even on lower-mood days. That resilience pattern is rare and worth protecting."

    return ""


def _risk_score(habit, recent_checkins):
    today = timezone.localdate()
    if habit.last_completed_on:
        days_since = max(0, (today - habit.last_completed_on).days)
    else:
        days_since = 5
    completed_recent = sum(1 for item in recent_checkins[:7] if item.completed)
    today_done = any(item.date == today and item.completed for item in recent_checkins)
    risk = 24 + (days_since * 14) + ((7 - completed_recent) * 4) + (habit.difficulty_level * 4)
    risk -= min(24, habit.current_streak * 2)
    if today_done:
        risk -= 18
    if habit.focus_mode:
        risk -= 8
    return max(4, min(95, risk))


def _evolve_habit(habit):
    next_level = min(5, max(1, (habit.completions_count // 7) + 1))
    if next_level != habit.difficulty_level:
        habit.difficulty_level = next_level


def build_habit_insight(habit, recent_checkins, mood_map):
    mood_message = _mood_correlation_message(habit, recent_checkins, mood_map)
    if mood_message:
        return mood_message

    if habit.risk_score >= 75:
        return "Streak risk is high. Trigger a shorter version today before momentum slips."
    if habit.focus_mode and habit.current_streak >= 3:
        return "Focus mode is helping. Keep the environment identical to preserve your current rhythm."
    if habit.current_streak >= 10:
        return "Your streak is no longer fragile. This habit is becoming part of your identity loop."
    if habit.completions_count <= 2:
        return "Early stage habits respond best to a tiny win. Make the first two minutes automatic."
    return "Consistency is trending upward. Protect the cue and keep the action small enough to repeat tomorrow."


def refresh_habit_metrics(habit, recent_checkins=None, mood_logs=None, mood_map=None):
    if recent_checkins is None:
        recent_checkins = list(habit.checkins.order_by("-date", "-created_at")[:21])
    if mood_logs is None:
        mood_logs = list(MoodLog.objects.filter(user=habit.user).order_by("-date")[:14])
    if mood_map is None:
        mood_map = {item.date: item for item in mood_logs}

    ordered_checkins = sorted(recent_checkins, key=lambda item: item.date)
    completed_dates = _dates_from_checkins(ordered_checkins)
    habit.current_streak = _current_streak_from_dates(completed_dates)
    habit.longest_streak = max(habit.longest_streak, _longest_streak_from_dates(completed_dates))
    habit.completions_count = sum(1 for item in ordered_checkins if item.completed)
    habit.last_completed_on = completed_dates[-1] if completed_dates else None
    habit.consistency_score = _completion_ratio(recent_checkins)
    habit.momentum_score = min(100, max(0, int((habit.current_streak * 6) + (habit.consistency_score * 0.5))))
    habit.risk_score = _risk_score(habit, recent_checkins)
    _evolve_habit(habit)
    habit.insight = build_habit_insight(habit, recent_checkins, mood_map)
    habit.save(
        update_fields=[
            "current_streak",
            "longest_streak",
            "completions_count",
            "last_completed_on",
            "consistency_score",
            "momentum_score",
            "risk_score",
            "difficulty_level",
            "insight",
            "updated_at",
        ]
    )
    return habit


def _award_badges(user, habit=None):
    profile = _profile_for(user)
    mood_log_count = MoodLog.objects.filter(user=user).count()
    existing_slugs = set(HabitBadge.objects.filter(user=user).values_list("slug", flat=True))
    candidate_slugs = set()

    if HabitCheckIn.objects.filter(habit__user=user, completed=True).exists():
        candidate_slugs.add("first-spark")
    if Habit.objects.filter(user=user, focus_mode=True).exists():
        candidate_slugs.add("focus-guardian")
    if Habit.objects.filter(user=user, current_streak__gte=7).exists():
        candidate_slugs.add("streak-7")
    if Habit.objects.filter(user=user, current_streak__gte=21).exists():
        candidate_slugs.add("streak-21")
    if mood_log_count >= 5:
        candidate_slugs.add("mood-cartographer")
    if HabitCheckIn.objects.filter(habit__user=user, recovery_used=True).exists():
        candidate_slugs.add("comeback-kid")

    created_badges = []
    for definition in BADGE_DEFINITIONS:
        if definition["slug"] in candidate_slugs and definition["slug"] not in existing_slugs:
            created_badges.append(HabitBadge.objects.create(user=user, **definition))

    if created_badges:
        profile.resilience_score += len(created_badges) * 5
        _refresh_profile(profile)

    return created_badges


def _xp_for_checkin(habit, completed=True, recovery_used=False):
    if not completed:
        return 0
    base = 12 + (habit.difficulty_level * 4)
    if habit.focus_mode:
        base += 5
    if recovery_used:
        base = max(6, base - 6)
    if habit.current_streak >= 7:
        base += 6
    return base


def _habit_payload(habit, mood_map):
    today = timezone.localdate()
    today_checkin = next((item for item in habit.prefetched_checkins if item.date == today), None)
    return {
        "id": habit.id,
        "title": habit.title,
        "category": habit.category,
        "cue": habit.cue,
        "why": habit.why,
        "streak": habit.current_streak,
        "longest_streak": habit.longest_streak,
        "progress": habit.progress_percent,
        "momentum": habit.momentum_score,
        "risk": habit.risk_score,
        "risk_band": habit.risk_band,
        "difficulty": habit.difficulty_label,
        "difficulty_level": habit.difficulty_level,
        "focus_mode": habit.focus_mode,
        "recovery_mode": habit.recovery_mode,
        "insight": habit.insight,
        "today_done": bool(today_checkin and today_checkin.completed),
        "recovery_available": not bool(today_checkin and today_checkin.completed),
        "mood_hint": mood_map.get(today).get_mood_score_display() if mood_map.get(today) else "",
    }


def toggle_habit_completion(habit, completed=None):
    today = timezone.localdate()
    checkin, _ = HabitCheckIn.objects.get_or_create(habit=habit, date=today)
    target_state = (not checkin.completed) if completed is None else bool(completed)
    checkin.completed = target_state
    checkin.recovery_used = False if target_state else checkin.recovery_used
    checkin.save()
    refresh_habit_metrics(habit)
    checkin.xp_awarded = _xp_for_checkin(habit, completed=target_state)
    checkin.effort_score = min(5, max(2, habit.difficulty_level + 1))
    checkin.note = "Locked in for today." if target_state else "Completion reset."
    checkin.save()

    refresh_habit_metrics(habit)
    profile = _profile_for(habit.user)
    if target_state:
        total_xp = HabitCheckIn.objects.filter(habit__user=habit.user, completed=True).aggregate(total=Sum("xp_awarded"))["total"] or 0
        profile.xp = total_xp
        profile.last_activity_on = today
        _refresh_profile(profile)
    _award_badges(habit.user, habit=habit)
    return checkin


def set_focus_mode(habit, enabled):
    habit.focus_mode = bool(enabled)
    habit.save(update_fields=["focus_mode", "updated_at"])
    _award_badges(habit.user, habit=habit)
    refresh_habit_metrics(habit)
    return habit


def activate_recovery_mode(habit):
    today = timezone.localdate()
    missed_date = today - timedelta(days=1)
    checkin, _ = HabitCheckIn.objects.get_or_create(habit=habit, date=missed_date)
    checkin.completed = True
    checkin.recovery_used = True
    checkin.note = "Recovery mode stabilized the streak."
    checkin.xp_awarded = max(6, 10 + habit.difficulty_level)
    checkin.save()
    habit.recovery_mode = True
    habit.save(update_fields=["recovery_mode", "updated_at"])
    refresh_habit_metrics(habit)

    profile = _profile_for(habit.user)
    profile.xp = HabitCheckIn.objects.filter(habit__user=habit.user, completed=True).aggregate(total=Sum("xp_awarded"))["total"] or 0
    profile.resilience_score += 8
    profile.last_activity_on = today
    _refresh_profile(profile)
    _award_badges(habit.user, habit=habit)

    habit.recovery_mode = False
    habit.save(update_fields=["recovery_mode", "updated_at"])
    refresh_habit_metrics(habit)
    return checkin


def log_mood(user, mood_score, energy_score, stress_score, note=""):
    mood_log, _ = MoodLog.objects.update_or_create(
        user=user,
        date=timezone.localdate(),
        defaults={
            "mood_score": mood_score,
            "energy_score": energy_score,
            "stress_score": stress_score,
            "note": note.strip(),
        },
    )
    for habit in Habit.objects.filter(user=user, is_archived=False):
        refresh_habit_metrics(habit)
    _award_badges(user)
    return mood_log


def planner_based_habit_suggestions(user):
    requests = list(PlannerRequest.objects.filter(user=user).order_by("-created_at")[:5])
    if not requests:
        return [
            {
                "title": "2-minute daily reset",
                "category": Habit.CATEGORY_ROUTINE,
                "cue": "Right before opening StudyFlow",
                "why": "A quick reset lowers friction before a full study session.",
            }
        ]

    topic_counter = Counter()
    suggestions = []
    existing_titles = set(Habit.objects.filter(user=user).values_list("title", flat=True))

    for request in requests:
        parts = [part.strip() for part in request.topics.replace("\n", ",").split(",") if part.strip()]
        topic_counter.update(parts[:6])

    for topic, _ in topic_counter.most_common(4):
        title = f"{topic} active recall"
        if title in existing_titles:
            continue
        suggestions.append(
            {
                "title": title,
                "category": Habit.CATEGORY_STUDY,
                "cue": f"Right after your {topic} planner block",
                "why": f"Recent exam-planner activity shows {topic} is a live priority.",
            }
        )

    if not suggestions:
        suggestions.append(
            {
                "title": "Night-before review pulse",
                "category": Habit.CATEGORY_STUDY,
                "cue": "After dinner",
                "why": "A light review habit protects memory consolidation before the next study day.",
            }
        )
    return suggestions[:4]


def build_dashboard_context(user):
    recent_checkins = Prefetch(
        "checkins",
        queryset=HabitCheckIn.objects.order_by("-date", "-created_at")[:21],
        to_attr="prefetched_checkins",
    )
    habits = list(
        Habit.objects.filter(user=user, is_archived=False)
        .prefetch_related(recent_checkins)
        .order_by("-momentum_score", "-current_streak", "title")
    )
    moods = list(MoodLog.objects.filter(user=user).order_by("-date")[:14])
    mood_map = {item.date: item for item in moods}
    profile = _profile_for(user)

    habit_cards = []
    for habit in habits:
        refresh_habit_metrics(habit, recent_checkins=habit.prefetched_checkins, mood_logs=moods, mood_map=mood_map)
        habit.prefetched_checkins = list(habit.checkins.order_by("-date", "-created_at")[:21])
        habit_cards.append(_habit_payload(habit, mood_map))

    total_habits = len(habit_cards)
    completed_today = sum(1 for item in habit_cards if item["today_done"])
    best_streak = max((item["streak"] for item in habit_cards), default=0)
    average_risk = int(sum(item["risk"] for item in habit_cards) / total_habits) if total_habits else 0
    mood_average = round(sum(item.mood_score for item in moods[:7]) / len(moods[:7]), 1) if moods[:7] else 0
    focus_cards = [item for item in habit_cards if item["focus_mode"]]
    recovery_cards = [item for item in habit_cards if item["risk"] >= 60][:3]
    badges = list(HabitBadge.objects.filter(user=user)[:6])

    return {
        "habit_cards": habit_cards,
        "profile": _refresh_profile(profile),
        "total_habits": total_habits,
        "completed_today": completed_today,
        "best_streak": best_streak,
        "average_risk": average_risk,
        "mood_average": mood_average,
        "focus_cards": focus_cards,
        "recovery_cards": recovery_cards,
        "badges": badges,
        "badges_count": HabitBadge.objects.filter(user=user).count(),
        "planner_suggestions": planner_based_habit_suggestions(user),
        "today_mood": mood_map.get(timezone.localdate()),
    }


def dashboard_forms(today_mood=None):
    from .forms import HabitForm, MoodLogForm

    return HabitForm(), MoodLogForm(instance=today_mood)


def habit_response_payload(habit):
    mood_map = {
        item.date: item for item in MoodLog.objects.filter(user=habit.user).order_by("-date")[:14]
    }
    habit.prefetched_checkins = list(habit.checkins.order_by("-date", "-created_at")[:21])
    refresh_habit_metrics(habit, recent_checkins=habit.prefetched_checkins, mood_map=mood_map)
    profile = _refresh_profile(_profile_for(habit.user))
    return {
        "habit": _habit_payload(habit, mood_map),
        "profile": {
            "xp": profile.xp,
            "level": profile.level,
            "progress": profile.progress_to_next_level,
            "resilience_score": profile.resilience_score,
        },
    }
