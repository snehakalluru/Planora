import json

from django.conf import settings
from pywebpush import WebPushException, webpush

from .models import NotificationSubscription


def send_push_notification(user, payload):
    subscriptions = NotificationSubscription.objects.filter(user=user, is_active=True)
    vapid_private_key = settings.WEBPUSH_SETTINGS.get("VAPID_PRIVATE_KEY")
    vapid_admin_email = settings.WEBPUSH_SETTINGS.get("VAPID_ADMIN_EMAIL")

    if not vapid_private_key or not vapid_admin_email:
        return 0

    delivered_count = 0
    for subscription in subscriptions:
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth,
            },
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims={"sub": f"mailto:{vapid_admin_email}"},
            )
            delivered_count += 1
        except WebPushException:
            subscription.is_active = False
            subscription.save(update_fields=["is_active"])

    return delivered_count
