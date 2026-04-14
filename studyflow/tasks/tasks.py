from celery import shared_task

from .management.commands.send_reminders import send_due_reminders


@shared_task
def send_due_task_reminders():
    return send_due_reminders()
