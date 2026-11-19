from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.evenements.models import Event
from apps.utilisateurs.models import Role


class Provider(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "Disponible", "Disponible"
        RESERVED = "Réservé", "Réservé"
        INACTIVE = "Inactif", "Inactif"

    name = models.CharField("raison sociale", max_length=160)
    specialty = models.CharField("spécialité", max_length=120)
    city = models.CharField("ville", max_length=120)
    email = models.EmailField("e-mail", max_length=190)
    phone = models.CharField("téléphone", max_length=30, blank=True)
    availability = models.CharField("disponibilités", max_length=255, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.PROTECT, verbose_name="compte prestataire", related_name="provider",
                               blank=True, null=True, limit_choices_to={"role": Role.PROVIDER})
    status = models.CharField("statut", max_length=20, choices=Status, default=Status.AVAILABLE)

    class Meta:
        db_table = "gestion_provider"
        ordering = ("name", "pk")
        verbose_name = "prestataire"

    def __str__(self):
        return self.name


class Service(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "Actif", "Actif"
        INACTIVE = "Inactif", "Inactif"

    provider = models.ForeignKey(Provider, models.PROTECT, verbose_name="prestataire", related_name="services")
    name = models.CharField("nom du service", max_length=160)
    description = models.TextField("description", blank=True)
    price = models.DecimalField("tarif (TND)", max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField("statut", max_length=20, choices=Status, default=Status.ACTIVE)

    class Meta:
        db_table = "gestion_service"
        ordering = ("name", "pk")
        constraints = [models.CheckConstraint(condition=Q(price__gte=0), name="service_positive_price")]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.pk:
            previous_provider = Service.objects.filter(pk=self.pk).values_list("provider_id", flat=True).first()
            if previous_provider != self.provider_id and self.reservations.exists():
                raise ValidationError({"provider": "Ce service est déjà associé à des réservations."})


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "En attente", "En attente"
        ACCEPTED = "Acceptée", "Acceptée"
        REJECTED = "Refusée", "Refusée"
        CANCELLED = "Annulée", "Annulée"

    event = models.ForeignKey(Event, models.PROTECT, verbose_name="événement", related_name="reservations")
    service = models.ForeignKey(Service, models.PROTECT, verbose_name="service", related_name="reservations")
    amount = models.DecimalField("montant (TND)", max_digits=12, decimal_places=2, default=0,
                                 validators=[MinValueValidator(0)])
    status = models.CharField("statut", max_length=20, choices=Status, default=Status.PENDING)
    rating = models.PositiveSmallIntegerField("note sur 5", blank=True, null=True,
                                               validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField("avis", blank=True)

    class Meta:
        db_table = "gestion_reservation"
        ordering = ("-pk",)
        verbose_name = "réservation"
        indexes = [models.Index(fields=["event", "status"], name="gestion_res_event_i_4b1d7a_idx")]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gte=0), name="reservation_positive_amount"),
            models.CheckConstraint(condition=Q(rating__isnull=True) | Q(rating__range=(1, 5)),
                                   name="reservation_rating_range"),
        ]

    def __str__(self):
        return f"{self.service} · {self.event}"

    def clean(self):
        super().clean()
        if self.status not in (self.Status.PENDING, self.Status.ACCEPTED):
            return
        if self.event_id and self.event.status == Event.Status.CANCELLED:
            raise ValidationError("Cet événement est annulé.")
        if self.service_id and (self.service.status == Service.Status.INACTIVE or
                                self.service.provider.status == Provider.Status.INACTIVE):
            raise ValidationError("Ce service ou son prestataire est inactif.")
