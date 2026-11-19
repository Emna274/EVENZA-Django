from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

from apps.core.models import Period
from apps.utilisateurs.models import Role


class Event(Period):
    class Status(models.TextChoices):
        DRAFT = "Brouillon", "Brouillon"
        PREPARATION = "En préparation", "En préparation"
        CONFIRMED = "Confirmé", "Confirmé"
        FINISHED = "Terminé", "Terminé"
        CANCELLED = "Annulé", "Annulé"

    class Type(models.TextChoices):
        WEDDING = "Mariage", "Mariage"
        BUSINESS = "Entreprise", "Entreprise"
        PRIVATE = "Privé", "Privé"
        CONFERENCE = "Conférence", "Conférence"
        OTHER = "Autre", "Autre"

    title = models.CharField("nom de l’événement", max_length=160)
    description = models.TextField("description", blank=True)
    location = models.CharField("lieu", max_length=255)
    type = models.CharField("type", max_length=20, choices=Type, default=Type.OTHER)
    capacity = models.PositiveIntegerField("capacité", validators=[MinValueValidator(1)])
    budget = models.DecimalField("budget (TND)", max_digits=12, decimal_places=2, default=0,
                                 validators=[MinValueValidator(0)])
    status = models.CharField("statut", max_length=20, choices=Status, default=Status.DRAFT)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, verbose_name="client", related_name="client_events",
                               blank=True, null=True, limit_choices_to={"role": Role.CLIENT})
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, verbose_name="organisateur", related_name="organized_events",
                                  blank=True, null=True, limit_choices_to={"role": Role.ORGANIZER})
    validator = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, verbose_name="validateur", related_name="validated_events",
                                  blank=True, null=True, limit_choices_to={"role": Role.ADMIN})
    created_at = models.DateTimeField("date de création", auto_now_add=True)

    class Meta(Period.Meta):
        db_table = "gestion_event"
        ordering = ("start_at", "pk")
        verbose_name = "événement"
        indexes = [models.Index(fields=["start_at", "status"], name="gestion_eve_start_a_177e82_idx")]
        constraints = Period.Meta.constraints + [
            models.CheckConstraint(condition=Q(capacity__gt=0, budget__gte=0), name="event_capacity_budget"),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        from apps.participants.models import Participant
        from apps.programmes.models import Suggestion
        from apps.ressources.models import Allocation, Resource, peak_quantity

        super().clean()
        if not self.pk:
            return
        if self.capacity is not None and self.registrations.filter(status__in=Participant.OCCUPIED).count() > self.capacity:
            raise ValidationError({"capacity": "La capacité est inférieure au nombre de places déjà occupées."})
        if self.start_at and self.end_at:
            outside = Q(start_at__lt=self.start_at) | Q(end_at__gt=self.end_at)
            if (self.sessions.filter(outside).exists() or
                    self.suggestions.filter(outside, status=Suggestion.Status.PENDING).exists() or
                    self.allocations.filter(outside, status=Allocation.Status.ASSIGNED).exists()):
                raise ValidationError("Des sessions, suggestions en attente ou affectations actives se trouvent hors de ces dates.")
            registrations = self.registrations.filter(status__in=Participant.OCCUPIED)
            overlaps = Participant.objects.filter(
                event__start_at__lt=self.end_at, event__end_at__gt=self.start_at,
                status__in=Participant.OCCUPIED,
            ).exclude(event=self).exclude(event__status=self.Status.CANCELLED)
            if self.status != self.Status.CANCELLED and (
                overlaps.filter(email__in=registrations.values("email")).exists() or
                overlaps.filter(user__in=registrations.exclude(user=None).values("user")).exists()
            ):
                raise ValidationError("Ce créneau entre en conflit avec une autre inscription des participants.")
            if self.status != self.Status.CANCELLED and Event.objects.filter(pk=self.pk, status=self.Status.CANCELLED).exists():
                for resource in Resource.objects.filter(allocations__event=self,
                                                        allocations__status=Allocation.Status.ASSIGNED).distinct():
                    allocations = resource.allocations.filter(status=Allocation.Status.ASSIGNED).filter(
                        Q(event=self) | ~Q(event__status=self.Status.CANCELLED),
                    )
                    if (resource.status != Resource.Status.AVAILABLE or
                            peak_quantity(allocations.values_list("start_at", "end_at", "quantity")) > resource.quantity):
                        raise ValidationError("Une ressource de cet événement est indisponible sur le créneau.")
