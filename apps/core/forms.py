from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils import timezone

from apps.evenements.models import Event
from apps.participants.models import Participant
from apps.prestataires.models import Provider
from apps.utilisateurs.models import Role

from .access import BY_MODEL, is_admin, scoped


class LocalDateTime(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self):
        super().__init__(format="%Y-%m-%dT%H:%M", attrs={"step": 60})


class StyledForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if widget.is_hidden:
                continue
            if isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(widget, forms.Select):
                css_class = "form-select"
            else:
                css_class = "form-control"
            widget.attrs["class"] = css_class
            if isinstance(widget, forms.Textarea):
                widget.attrs["rows"] = 3


class RecordForm(StyledForm, forms.ModelForm):
    def __init__(self, *args, actor, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField) and field.queryset.model in BY_MODEL:
                model = field.queryset.model
                if not is_admin(actor) and model is Event:
                    field.queryset = scoped(actor, BY_MODEL[model])
                    if actor.role == Role.PARTICIPANT:
                        field.queryset = field.queryset.filter(status=Event.Status.CONFIRMED,
                                                               start_at__gt=timezone.now())
                if not is_admin(actor) and model is Participant:
                    field.queryset = scoped(actor, BY_MODEL[model])
                if not is_admin(actor) and model is Provider:
                    field.queryset = scoped(actor, BY_MODEL[model])

    def add_error(self, field, error):
        if field is None and isinstance(error, ValidationError) and hasattr(error, "error_dict"):
            visible_errors = {}
            for name, errors in error.error_dict.items():
                target = name if name in self.fields else NON_FIELD_ERRORS
                visible_errors.setdefault(target, []).extend(errors)
            error = ValidationError(visible_errors)
        super().add_error(field, error)


def record_form(section, actor, record=None):
    fields = section.fields.split()
    widgets = {field: LocalDateTime() for field in ("start_at", "end_at") if field in fields}
    return forms.modelform_factory(section.model, form=RecordForm, fields=fields, widgets=widgets)
