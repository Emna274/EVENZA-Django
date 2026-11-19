from django.contrib import messages

from apps.core.access import SECTIONS
from apps.core.audit import record_activity, record_changes

from .models import Program, Suggestion


def choices(user, record):
    if record.status == Suggestion.Status.PENDING:
        return [("approve", "Valider la suggestion"), ("reject", "Rejeter la suggestion")]
    return []


def perform(request, record, operation):
    previous = record.status
    session = None
    if operation == "approve":
        session = Program(event=record.event, title=record.title, start_at=record.start_at,
                          end_at=record.end_at, status=Program.Status.CONFIRMED)
        session.full_clean()
        record.status = Suggestion.Status.APPROVED
    else:
        record.status = Suggestion.Status.REJECTED
    record.full_clean()
    if session:
        session.save()
        record_activity(request.user, SECTIONS["programs"], session.pk, "Création")
    record.save(update_fields=["status"])
    record_changes(request.user, SECTIONS["suggestions"], record, "Modification", previous)
    messages.success(request, "L’action a été enregistrée.")
