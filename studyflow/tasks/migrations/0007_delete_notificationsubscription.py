from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0006_dailytimetabletask"),
    ]

    operations = [
        migrations.DeleteModel(
            name="NotificationSubscription",
        ),
    ]
