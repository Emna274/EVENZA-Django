from django import forms

from apps.core.access import is_admin
from apps.core.forms import LocalDateTime, RecordForm
from apps.utilisateurs.models import Role

from .models import Event


class EventForm(RecordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.actor.role == Role.ORGANIZER and not is_admin(self.actor):
            if self.instance.status != Event.Status.CONFIRMED:
                self.fields["status"].choices = [
                    choice for choice in self.fields["status"].choices if choice[0] != Event.Status.CONFIRMED
                ]

    def clean(self):
        data = super().clean()
        if not is_admin(self.actor):
            if self.actor.role == Role.ORGANIZER:
                self.instance.organizer = self.actor
            elif self.actor.role == Role.CLIENT:
                self.instance.client = self.actor
        return data


def record_form(section, actor, record=None):
    fields = section.fields.split()
    if not is_admin(actor):
        if actor.role == Role.ORGANIZER:
            fields = [field for field in fields if field not in {"organizer", "validator"}]
        elif actor.role == Role.CLIENT:
            fields = ["title", "description", "start_at", "end_at", "location", "type", "capacity", "budget"]
    return forms.modelform_factory(
        Event, form=EventForm, fields=fields, widgets={"start_at": LocalDateTime(), "end_at": LocalDateTime()},
    )
