from django.contrib import messages
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from apps.accounts.services import notify
from apps.core.access import SECTIONS, is_admin
from apps.core.audit import record_activity, save_status
from apps.evenements.models import Event
from apps.utilisateurs.models import Role

from .models import Participant


def participant_status_changed(record):
    notify(record.user_id, f"Inscription à « {record.event} » · {record.status}.")


def complaint_status_changed(record):
    notify(record.participant.user_id, f"Réclamation « {record.subject} » · {record.status}.")


def choices(user, record):
    if not (is_admin(user) or user.role == Role.ORGANIZER):
        return []
    actions = []
    if record.status == Participant.Status.WAITLIST:
        actions.append(("promote", "Attribuer une place"))
    if record.event.start_at > timezone.now() and record.event.status != Event.Status.CANCELLED:
        if record.status == Participant.Status.INVITED:
            actions.append(("invite", "Envoyer l’invitation"))
        if record.status in (Participant.Status.INVITED, Participant.Status.WAITLIST, Participant.Status.REGISTERED):
            actions.append(("remind", "Envoyer un rappel"))
    return actions


def send_participant_email(request, record, operation):
    if record.status == Participant.Status.INVITED:
        token = signing.dumps({"pk": record.pk, "email": record.email}, salt="evenza-invitation")
        url = request.build_absolute_uri(reverse("invitation", args=[token]))
    else:
        url = request.build_absolute_uri(SECTIONS["participants"].url("detail", record.pk))
    subject = "Invitation" if operation == "invite" else "Rappel"
    send_mail(f"Évenza · {subject}", f"{record.name},\n\n{record.event}\n{url}", None, [record.email])


def perform(request, record, operation):
    section = SECTIONS["participants"]
    if operation in {"invite", "remind"}:
        send_participant_email(request, record, operation)
        messages.success(request, "Le message a été transmis au service de messagerie.")
        record_activity(request.user, section, record.pk, "Envoi d’un message")
    else:
        previous = record.status
        record.status = Participant.Status.REGISTERED
        if record.event.start_at <= timezone.now():
            raise ValidationError("L’événement a déjà commencé.")
        save_status(request, section, record, previous, participant_status_changed)
