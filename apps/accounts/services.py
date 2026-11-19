from .models import Notification


def notify(user_id, message):
    if user_id:
        Notification.objects.create(user_id=user_id, message=message)
