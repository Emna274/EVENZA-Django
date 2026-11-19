from django.contrib import messages

from apps.dashboard.models import Activity


def record_activity(actor, section, pk, action):
    Activity.objects.create(user=actor, entity=section.key, record_id=pk, action=action)


def record_changes(actor, section, record, action, previous_status=None, status_changed=None):
    record_activity(actor, section, record.pk, action)
    if status_changed and previous_status != getattr(record, "status", None):
        status_changed(record)


def save_status(request, section, record, previous, status_changed=None):
    record.full_clean()
    record.save(update_fields=["status"])
    record_changes(request.user, section, record, "Modification", previous, status_changed)
    messages.success(request, "L’action a été enregistrée.")
