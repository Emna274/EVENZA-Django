from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.models import Period
from apps.evenements.models import Event


class Resource(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "Disponible", "Disponible"
        MAINTENANCE = "Maintenance", "Maintenance"
        UNAVAILABLE = "Indisponible", "Indisponible"

    class Category(models.TextChoices):
        FURNITURE = "Mobilier", "Mobilier"
        SOUND = "Son & lumière", "Son & lumière"
        DECOR = "Décoration", "Décoration"
        SPACE = "Espace", "Espace"
        OTHER = "Autre", "Autre"

    name = models.CharField("nom de la ressource", max_length=160)
    category = models.CharField("catégorie", max_length=20, choices=Category, default=Category.OTHER)
    quantity = models.PositiveIntegerField("quantité totale")
    status = models.CharField("état", max_length=20, choices=Status, default=Status.AVAILABLE)
    description = models.TextField("description", blank=True)

    class Meta:
        db_table = "gestion_resource"
        ordering = ("name", "pk")
        verbose_name = "ressource"

    def __str__(self):
        return self.name

    def available_between(self, start_at, end_at, exclude_pk=None):
        if self.status != self.Status.AVAILABLE:
            return 0
        overlapping = self.allocations.filter(
            status=Allocation.Status.ASSIGNED, start_at__lt=end_at, end_at__gt=start_at,
        ).exclude(pk=exclude_pk).exclude(event__status=Event.Status.CANCELLED)
        periods = ((max(start, start_at), min(end, end_at), quantity)
                   for start, end, quantity in overlapping.values_list("start_at", "end_at", "quantity"))
        return self.quantity - peak_quantity(periods)

    def clean(self):
        super().clean()
        if not self.pk:
            return
        current = self.allocations.filter(status=Allocation.Status.ASSIGNED,
                                          end_at__gt=timezone.now()).exclude(event__status=Event.Status.CANCELLED)
        peak = peak_quantity(current.values_list("start_at", "end_at", "quantity"))
        if self.quantity is not None and peak > self.quantity:
            raise ValidationError({"quantity": "Cette quantité est inférieure au stock déjà affecté."})
        if peak and self.status != self.Status.AVAILABLE:
            raise ValidationError({"status": "Annulez les affectations en cours ou à venir avant de rendre la ressource indisponible."})


def peak_quantity(periods):
    changes = []
    for start, end, quantity in periods:
        changes.extend(((start, quantity), (end, -quantity)))
    used = peak = 0
    for _, delta in sorted(changes):
        used += delta
        peak = max(peak, used)
    return peak


class Allocation(Period):
    class Status(models.TextChoices):
        ASSIGNED = "Affecté", "Affecté"
        CANCELLED = "Annulé", "Annulé"

    event = models.ForeignKey(Event, models.PROTECT, verbose_name="événement", related_name="allocations")
    resource = models.ForeignKey(Resource, models.PROTECT, verbose_name="ressource", related_name="allocations")
    quantity = models.PositiveIntegerField("quantité", validators=[MinValueValidator(1)])
    status = models.CharField("statut", max_length=20, choices=Status, default=Status.ASSIGNED)

    class Meta(Period.Meta):
        db_table = "gestion_allocation"
        ordering = ("-start_at", "pk")
        verbose_name = "affectation"
        indexes = [models.Index(fields=["resource", "start_at", "end_at"], name="gestion_all_resourc_bfb645_idx")]
        constraints = Period.Meta.constraints + [
            models.CheckConstraint(condition=Q(quantity__gt=0), name="allocation_positive_quantity"),
        ]

    def __str__(self):
        return f"{self.resource} · {self.event}"

    def clean(self):
        super().clean()
        if self.status != self.Status.ASSIGNED:
            return
        self.check_event_period()
        if self.event_id and self.event.status == Event.Status.CANCELLED:
            raise ValidationError("Cet événement est annulé.")
        if not (self.resource_id and self.start_at and self.end_at and self.quantity):
            return
        if self.resource.status != Resource.Status.AVAILABLE:
            raise ValidationError({"resource": "Cette ressource est indisponible."})
        available = self.resource.available_between(self.start_at, self.end_at, exclude_pk=self.pk)
        if self.quantity > available:
            raise ValidationError({"quantity": f"Quantité disponible sur tout ce créneau : {available}."})
