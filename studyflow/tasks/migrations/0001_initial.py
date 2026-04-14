from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("deadline", models.DateTimeField()),
                ("priority", models.CharField(choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low")], default="Medium", max_length=10)),
                ("status", models.CharField(choices=[("Pending", "Pending"), ("Completed", "Completed")], default="Pending", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("reminder_sent", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tasks", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["deadline", "-created_at"],
            },
        ),
    ]
