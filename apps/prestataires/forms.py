from django import forms
from django.db.models import Q

from apps.core.access import is_admin
from apps.core.forms import RecordForm
from apps.utilisateurs.models import Role

from .models import Provider, Reservation, Service


class ReservationForm(RecordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if is_admin(self.actor):
            return
        if self.actor.role == Role.PROVIDER:
            statuses = [self.instance.status]
            if self.instance.status == Reservation.Status.PENDING:
                statuses += [Reservation.Status.ACCEPTED, Reservation.Status.REJECTED]
            self.fields["status"].choices = [(status, status) for status in statuses]
        if self.actor.role == Role.ORGANIZER and "service" in self.fields:
            current = Q(pk=self.instance.service_id) if self.instance.pk else Q(pk__isnull=True)
            self.fields["service"].queryset = self.fields["service"].queryset.filter(
                Q(status=Service.Status.ACTIVE) & ~Q(provider__status=Provider.Status.INACTIVE) | current
            )


def record_form(section, actor, record=None):
    fields = section.fields.split()
    if not is_admin(actor):
        if actor.role == Role.PROVIDER and section.key == "providers":
            fields = ["phone", "availability"]
        elif actor.role == Role.PROVIDER and section.key == "reservations":
            fields = ["status"]
        elif actor.role == Role.ORGANIZER and section.key == "reservations":
            if record and record.status == Reservation.Status.ACCEPTED:
                fields = ["rating", "comment"]
            else:
                fields = [field for field in fields if field not in {"status", "rating", "comment"}]
    form = ReservationForm if section.key == "reservations" else RecordForm
    return forms.modelform_factory(section.model, form=form, fields=fields)
