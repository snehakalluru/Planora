import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Task
from tasks.notification_utils import send_push_notification

logger = logging.getLogger(__name__)


def send_due_reminders():
    now = timezone.now()
    reminder_window = now + timedelta(hours=24)

    tasks = Task.objects.filter(
        status=Task.STATUS_PENDING,
        reminder_sent=False,
        deadline__gte=now,
        deadline__lte=reminder_window,
    ).exclude(user__email="")

    delivered_count = 0
    for task in tasks:
        reminder_due = task.reminder_time or (task.deadline - timedelta(hours=2))
        if reminder_due > now:
            continue

        subject = f"StudyFlow Reminder: {task.title}"
        message = (
            f"Hello {task.user.first_name or task.user.username},\n\n"
            f"This is a reminder that your task '{task.title}' is due on "
            f"{timezone.localtime(task.deadline).strftime('%d %b %Y, %I:%M %p')}.\n\n"
            f"Priority: {task.priority}\n"
            f"Status: {task.status}\n\n"
            f"Description:\n{task.description or 'No description provided.'}\n\n"
            "Please log in to StudyFlow and take action."
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.user.email],
                fail_silently=False,
            )
        except Exception as exc:
            logger.warning(
                "Reminder email failed for task %s and user %s: %s",
                task.pk,
                task.user.email,
                exc,
            )

        send_push_notification(
            task.user,
            {
                "title": "StudyFlow Reminder",
                "body": f"{task.title} is due at {timezone.localtime(task.deadline).strftime('%I:%M %p')}",
                "url": "/tasks/",
            },
        )

        task.reminder_sent = True
        task.save(update_fields=["reminder_sent"])
        delivered_count += 1

    return delivered_count


class Command(BaseCommand):
    help = "Send email and browser reminders for tasks due within the next 24 hours."

    def handle(self, *args, **options):
        delivered_count = send_due_reminders()

        if not delivered_count:
            self.stdout.write(self.style.WARNING("No reminders to send."))
            return

        self.stdout.write(self.style.SUCCESS(f"Sent {delivered_count} reminder(s)."))
