from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.access import is_admin
from apps.core.forms import RecordForm, StyledForm
from apps.evenements.models import Event
from apps.utilisateurs.models import Role

from .models import Participant


def participant_statuses(record):
    status = Participant.Status
    transitions = {
        status.INVITED: (status.CONFIRMED, status.DECLINED),
        status.REGISTERED: (status.CONFIRMED, status.CANCELLED),
        status.CONFIRMED: (status.CANCELLED,),
        status.WAITLIST: (status.CANCELLED,),
    }
    return (record.status, *transitions.get(record.status, ()))


class ParticipantForm(RecordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and not is_admin(self.actor) and self.actor.role == Role.PARTICIPANT:
            record = self.instance
            statuses = participant_statuses(record) if record.event.start_at > timezone.now() else (record.status,)
            self.fields["status"].choices = [(status, status) for status in statuses]
            if record.event.end_at > timezone.now() or record.event.status == Event.Status.CANCELLED:
                self.fields.pop("rating")
                self.fields.pop("feedback")

    def clean(self):
        data = super().clean()
        if self.actor.role == Role.PARTICIPANT and not is_admin(self.actor):
            self.prepare_participation(data)
        return data

    def prepare_participation(self, data):
        now = timezone.now()
        if not self.instance.pk:
            self.instance.user = self.actor
            self.instance.name = self.actor.name
            self.instance.email = self.actor.email
            event = data.get("event")
            if event and event.registrations.filter(status__in=Participant.OCCUPIED).count() >= event.capacity:
                self.instance.status = Participant.Status.WAITLIST
            return

        status = data.get("status", self.instance.status)
        changed_status = status != self.instance.status
        if changed_status and (status not in participant_statuses(self.instance) or
                               self.instance.event.start_at <= now or
                               self.instance.event.status == Event.Status.CANCELLED):
            self.add_error("status", "Cette réponse n’est plus disponible.")
        if ({"rating", "feedback"} & set(self.changed_data) and
                (self.instance.event.end_at > now or self.instance.event.status == Event.Status.CANCELLED)):
            self.add_error(None, "Vous pourrez laisser un avis après l’événement.")


def record_form(section, actor, record=None):
    fields = section.fields.split()
    if actor.role == Role.PARTICIPANT and not is_admin(actor):
        if section.key == "participants":
            fields = ["status", "preference", "rating", "feedback"] if record else ["event", "preference"]
        elif section.key == "complaints":
            fields = ["participant", "subject", "message"]
    form = ParticipantForm if section.key == "participants" else RecordForm
    return forms.modelform_factory(section.model, form=form, fields=fields)


class DocumentForm(StyledForm, forms.Form):
    document = forms.FileField(
        label="Document",
        help_text="PDF, PNG ou JPEG, jusqu’à 5 Mo.",
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.png,.jpg,.jpeg"}),
    )

    def clean_document(self):
        from pathlib import PurePath

        file = self.cleaned_data["document"]
        if file.size > 5 * 1024 * 1024 or len(file.name) > 190:
            raise ValidationError("Le fichier dépasse la taille ou la longueur de nom autorisée.")
        formats = {
            ".pdf": ("application/pdf", b"%PDF-"),
            ".png": ("image/png", b"\x89PNG\r\n\x1a\n"),
            ".jpg": ("image/jpeg", b"\xff\xd8\xff"),
            ".jpeg": ("image/jpeg", b"\xff\xd8\xff"),
        }
        entry = formats.get(PurePath(file.name).suffix.lower())
        if not entry or not file.read(8).startswith(entry[1]):
            raise ValidationError("Choisissez un fichier PDF, PNG ou JPEG valide.")
        file.seek(0)
        self.mime = entry[0]
        return file
