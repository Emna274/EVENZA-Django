from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Period(models.Model):
    start_at = models.DateTimeField("début")
    end_at = models.DateTimeField("fin")

    class Meta:
        abstract = True
        constraints = [models.CheckConstraint(condition=Q(end_at__gt=F("start_at")),
                                               name="gestion_%(class)s_period")]

    def clean(self):
        super().clean()
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValidationError({"end_at": "La fin doit être postérieure au début."})

    def check_event_period(self):
        if self.event_id and self.start_at and self.end_at:
            if self.start_at < self.event.start_at or self.end_at > self.event.end_at:
                raise ValidationError("Le créneau doit être compris dans les dates de l’événement.")
