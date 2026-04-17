from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView

from tasks.views import service_worker_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("serviceworker.js", service_worker_view, name="service_worker"),
    path("habits/", include("habits.urls")),
    path("users/", include("users.urls")),
    path("tasks/", include("tasks.urls")),
    path("webpush/", include("webpush.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
