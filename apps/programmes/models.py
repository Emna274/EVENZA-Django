from django.db import models

from apps.core.models import Period
from apps.evenements.models import Event


class Program(Period):
    class Status(models.TextChoices):
        PLANNED = "Planifié", "Planifié"
        CONFIRMED = "Confirmé", "Confirmé"
        FINISHED = "Terminé", "Terminé"

    event = models.ForeignKey(Event, models.PROTECT, verbose_name="événement", related_name="sessions")
    title = models.CharField("titre de la session", max_length=160)
    description = models.TextField("description", blank=True)
    speaker = models.CharField("intervenant", max_length=160, blank=True)
    status = models.CharField("statut", max_length=20, choices=Status, default=Status.PLANNED)

    class Meta(Period.Meta):
        db_table = "gestion_program"
        ordering = ("start_at", "pk")
        verbose_name = "session de programme"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        self.check_event_period()


class Suggestion(Period):
    class Status(models.TextChoices):
        PENDING = "En attente", "En attente"
        APPROVED = "Validée", "Validée"
        REJECTED = "Rejetée", "Rejetée"

    event = models.ForeignKey(Event, models.PROTECT, verbose_name="événement", related_name="suggestions")
    title = models.CharField("titre proposé", max_length=160)
    status = models.CharField("statut", max_length=20, choices=Status, default=Status.PENDING, editable=False)

    class Meta(Period.Meta):
        db_table = "gestion_suggestion"
        ordering = ("start_at", "pk")
        verbose_name = "suggestion de programme"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        self.check_event_period()
