from apps.accounts.services import notify
from apps.core.access import SECTIONS, is_admin
from apps.core.audit import save_status
from apps.utilisateurs.models import Role

from .models import Reservation


def reservation_status_changed(record):
    recipient = (record.event.organizer_id if record.status in
                 (Reservation.Status.ACCEPTED, Reservation.Status.REJECTED) else
                 record.service.provider.user_id)
    notify(recipient, f"Réservation « {record.service} » · {record.status}.")


def choices(user, record):
    if (is_admin(user) or user.role == Role.ORGANIZER) and record.status in (
            Reservation.Status.PENDING, Reservation.Status.ACCEPTED):
        return [("cancel", "Annuler la réservation")]
    return []


def perform(request, record, operation):
    previous = record.status
    record.status = Reservation.Status.CANCELLED
    save_status(request, SECTIONS["reservations"], record, previous, reservation_status_changed)
