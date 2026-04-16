import json
import logging
from collections import OrderedDict
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .chatbot import generate_exam_plan
from .file_utils import extract_text_from_pdf
from .forms import DailyTimetableTaskForm, ExamPlannerForm, TaskForm
from .management.commands.send_reminders import send_due_reminders
from .models import DailyTimetableTask, NotificationSubscription, PlannerRequest, StudyResource, Task

logger = logging.getLogger(__name__)


def _clear_stale_planner_messages(request):
    preserved_messages = []
    stale_fragments = (
        "Gemini could not generate",
        "Gemini API request failed",
        "Gemini",
    )

    for message in messages.get_messages(request):
        message_text = str(message)
        if any(fragment in message_text for fragment in stale_fragments):
            logger.info("Cleared stale planner message: %s", message_text)
            continue
        preserved_messages.append((message.level, message_text, message.extra_tags))

    for level, message_text, extra_tags in preserved_messages:
        messages.add_message(request, level, message_text, extra_tags=extra_tags)


@login_required
def planner_history(request):
    requests = PlannerRequest.objects.filter(user=request.user)
    return render(request, "tasks/planner_history.html", {"requests": requests})


@login_required
def planner_detail(request, pk):
    planner_request = get_object_or_404(PlannerRequest, pk=pk, user=request.user)
    return render(request, "tasks/planner_detail.html", {"planner_request": planner_request})


@login_required
@require_POST
def delete_planner_request(request, pk):
    planner_request = get_object_or_404(PlannerRequest, pk=pk, user=request.user)
    planner_request.delete()
    messages.success(request, "Planner request deleted.")
    return redirect(reverse("planner_history"))


def _get_filtered_tasks(request):
    tasks = Task.objects.filter(user=request.user)
    priority = request.GET.get("priority", "")
    status = request.GET.get("status", "")

    if priority:
        tasks = tasks.filter(priority=priority)
    if status:
        tasks = tasks.filter(status=status)

    return tasks, priority, status


@login_required
def dashboard_view(request):
    send_due_reminders()
    tasks, selected_priority, selected_status = _get_filtered_tasks(request)
    user_tasks = Task.objects.filter(user=request.user)
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(status=Task.STATUS_COMPLETED).count()
    pending_tasks = user_tasks.filter(status=Task.STATUS_PENDING).count()
    progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    now = timezone.now()
    upcoming_deadlines = user_tasks.filter(
        status=Task.STATUS_PENDING,
        deadline__gte=now,
        deadline__lte=now + timedelta(days=3),
    ).order_by("deadline")

    overdue_tasks = user_tasks.filter(status=Task.STATUS_PENDING, deadline__lt=now).order_by("deadline")
    due_today_tasks = user_tasks.filter(
        status=Task.STATUS_PENDING,
        deadline__date=timezone.localdate(),
    ).order_by("deadline")
    late_completed_tasks = user_tasks.filter(
        status=Task.STATUS_COMPLETED,
        completed_at__isnull=False,
        completed_at__gt=timezone.now() - timedelta(days=14),
    ).order_by("-completed_at")
    reminder_ready_tasks = user_tasks.filter(
        status=Task.STATUS_PENDING,
        reminder_sent=False,
        reminder_time__isnull=False,
        reminder_time__lte=now + timedelta(hours=12),
    ).order_by("reminder_time")
    active_subscription = request.user.notification_subscriptions.filter(is_active=True).exists()

    task_summary = user_tasks.aggregate(
        high_priority=Count("id", filter=Q(priority=Task.PRIORITY_HIGH)),
        medium_priority=Count("id", filter=Q(priority=Task.PRIORITY_MEDIUM)),
        low_priority=Count("id", filter=Q(priority=Task.PRIORITY_LOW)),
    )

    context = {
        "tasks": tasks[:8],
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "progress_percentage": progress_percentage,
        "upcoming_deadlines": upcoming_deadlines,
        "selected_priority": selected_priority,
        "selected_status": selected_status,
        "priority_choices": Task.PRIORITY_CHOICES,
        "status_choices": Task.STATUS_CHOICES,
        "task_summary": task_summary,
        "overdue_tasks": overdue_tasks[:5],
        "due_today_tasks": due_today_tasks[:5],
        "late_completed_tasks": [task for task in late_completed_tasks[:5] if task.was_completed_late],
        "reminder_ready_tasks": reminder_ready_tasks[:5],
        "notifications_enabled": active_subscription,
        "vapid_public_key": settings.WEBPUSH_SETTINGS.get("VAPID_PUBLIC_KEY", ""),
    }
    return render(request, "tasks/dashboard.html", context)


@login_required
def task_list_view(request):
    tasks, selected_priority, selected_status = _get_filtered_tasks(request)
    context = {
        "tasks": tasks,
        "selected_priority": selected_priority,
        "selected_status": selected_status,
        "priority_choices": Task.PRIORITY_CHOICES,
        "status_choices": Task.STATUS_CHOICES,
    }
    return render(request, "tasks/task_list.html", context)


@login_required
def task_create_view(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task created successfully.")
            return redirect("task_list")
    else:
        form = TaskForm()

    return render(request, "tasks/task_form.html", {"form": form, "page_title": "Add Task"})


@login_required
def task_update_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)

    return render(request, "tasks/task_form.html", {"form": form, "page_title": "Edit Task"})


@login_required
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect("task_list")

    return render(request, "tasks/task_confirm_delete.html", {"task": task})


@login_required
@require_POST
def task_toggle_status_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.status = Task.STATUS_COMPLETED if task.status == Task.STATUS_PENDING else Task.STATUS_PENDING
    task.save()
    messages.success(request, f'Task "{task.title}" marked as {task.status.lower()}.')
    return redirect(request.META.get("HTTP_REFERER", "task_list"))


@login_required
def timetable_view(request):
    timetable_tasks = DailyTimetableTask.objects.filter(user=request.user).order_by("start_time", "end_time")
    return render(request, "tasks/timetable.html", {"timetable_tasks": timetable_tasks})


@login_required
def timetable_task_create_view(request):
    if request.method == "POST":
        form = DailyTimetableTaskForm(request.POST)
        if form.is_valid():
            timetable_task = form.save(commit=False)
            timetable_task.user = request.user
            timetable_task.save()
            messages.success(request, "Timetable task added successfully.")
            return redirect("timetable")
    else:
        form = DailyTimetableTaskForm()

    return render(
        request,
        "tasks/timetable_form.html",
        {"form": form, "page_title": "Add Timetable Task"},
    )


@login_required
def timetable_task_update_view(request, pk):
    timetable_task = get_object_or_404(DailyTimetableTask, pk=pk, user=request.user)

    if request.method == "POST":
        form = DailyTimetableTaskForm(request.POST, instance=timetable_task)
        if form.is_valid():
            form.save()
            messages.success(request, "Timetable task updated successfully.")
            return redirect("timetable")
    else:
        form = DailyTimetableTaskForm(instance=timetable_task)

    return render(
        request,
        "tasks/timetable_form.html",
        {"form": form, "page_title": "Edit Timetable Task", "timetable_task": timetable_task},
    )


@login_required
def timetable_task_delete_view(request, pk):
    timetable_task = get_object_or_404(DailyTimetableTask, pk=pk, user=request.user)

    if request.method == "POST":
        timetable_task.delete()
        messages.success(request, "Timetable task deleted successfully.")
        return redirect("timetable")

    return render(request, "tasks/timetable_confirm_delete.html", {"timetable_task": timetable_task})


@login_required
@require_POST
def timetable_task_toggle_completed_view(request, pk):
    timetable_task = get_object_or_404(DailyTimetableTask, pk=pk, user=request.user)
    timetable_task.completed = not timetable_task.completed
    timetable_task.save(update_fields=["completed", "updated_at"])
    status_label = "completed" if timetable_task.completed else "pending"
    messages.success(request, f'Timetable task "{timetable_task.title}" marked as {status_label}.')
    return redirect(request.META.get("HTTP_REFERER", "timetable"))


@login_required
def calendar_view(request):
    tasks = Task.objects.filter(user=request.user).order_by("deadline")
    grouped_tasks = OrderedDict()

    for task in tasks:
        grouped_tasks.setdefault(task.deadline.date(), []).append(task)

    return render(request, "tasks/calendar.html", {"grouped_tasks": grouped_tasks})


@login_required
def chatbot_view(request):
    logger.info("VIEW EXECUTED: tasks.views.chatbot_view")
    _clear_stale_planner_messages(request)

    plan = ""
    uploaded_resource = None
    active_planner_request = None

    if request.method == "POST":
        form = ExamPlannerForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            topics = form.cleaned_data["topics"]
            difficulty = form.cleaned_data["difficulty"]
            uploaded_file = form.cleaned_data.get("file")
            resource_text = ""

            if uploaded_file:
                uploaded_resource = StudyResource.objects.create(user=request.user, file=uploaded_file)
                try:
                    resource_text = extract_text_from_pdf(uploaded_resource.file)
                except Exception as exc:
                    messages.warning(request, f"PDF processing failed: {exc}")
                    resource_text = ""

            try:
                logger.info("Exam planner request routed to OpenRouter.")
                plan = generate_exam_plan(subject, topics, difficulty, resource_text)
                logger.info("OpenRouter response passed to template: %s", plan[:500])
            except Exception as exc:
                logger.exception("OpenRouter exam planner request failed: %s", exc)
                messages.error(request, "Unable to generate plan. Please try again.")
                plan = ""

            if plan:
                active_planner_request = PlannerRequest.objects.create(
                    user=request.user,
                    subject=subject,
                    topics=topics,
                    difficulty=difficulty,
                    response=plan,
                )
                messages.success(request, "Your AI exam planner has been generated.")
    else:
        form = ExamPlannerForm()

    if not plan:
        plan = ""

    requests = PlannerRequest.objects.filter(user=request.user)
    if active_planner_request:
        requests = requests.exclude(pk=active_planner_request.pk)
    requests = requests.order_by("-created_at")[:5]
    timetable_tasks = DailyTimetableTask.objects.filter(user=request.user).order_by("start_time", "end_time")
    context = {
        "form": form,
        "plan": plan,
        "uploaded_resource": uploaded_resource,
        "active_planner_request": active_planner_request,
        "chat_history": [],
        "requests": requests,
        "timetable_tasks": timetable_tasks,
    }
    return render(request, "tasks/chatbot.html", context)


@login_required
@require_POST
def subscribe_notifications_view(request):
    payload = json.loads(request.body.decode("utf-8"))
    subscription, _ = NotificationSubscription.objects.update_or_create(
        endpoint=payload["endpoint"],
        defaults={
            "user": request.user,
            "p256dh": payload["keys"]["p256dh"],
            "auth": payload["keys"]["auth"],
            "is_active": True,
        },
    )
    return JsonResponse({"status": "subscribed", "subscription_id": subscription.pk})


@login_required
@require_POST
def unsubscribe_notifications_view(request):
    NotificationSubscription.objects.filter(user=request.user, is_active=True).update(is_active=False)
    return JsonResponse({"status": "unsubscribed"})


def service_worker_view(request):
    content = render_to_string(
        "serviceworker.js",
        {
            "site_origin": request.build_absolute_uri("/").rstrip("/"),
        },
    )
    return HttpResponse(content, content_type="application/javascript")
