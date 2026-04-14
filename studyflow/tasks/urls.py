from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("chatbot/", views.chatbot_view, name="chatbot"),
    path("list/", views.task_list_view, name="task_list"),
    path("add/", views.task_create_view, name="task_add"),
    path("<int:pk>/edit/", views.task_update_view, name="task_edit"),
    path("<int:pk>/delete/", views.task_delete_view, name="task_delete"),
    path("<int:pk>/toggle/", views.task_toggle_status_view, name="task_toggle"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("notifications/subscribe/", views.subscribe_notifications_view, name="notifications_subscribe"),
    path("notifications/unsubscribe/", views.unsubscribe_notifications_view, name="notifications_unsubscribe"),
]
