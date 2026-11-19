import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower

from apps.evenements.models import Event
from apps.utilisateurs.models import Role


def badge_token():
    return secrets.token_hex(32)


class Participant(models.Model):
    class Status(models.TextChoices):
        INVITED = "Invité", "Invité"
        REGISTERED = "Inscrit", "Inscrit"
        CONFIRMED = "Confirmé", "Confirmé"
        PRESENT = "Présent", "Présent"
        ABSENT = "Absent", "Absent"
        WAITLIST = "Liste d’attente", "Liste d’attente"
        CANCELLED = "Annulé", "Annulé"
        DECLINED = "Refusé", "Refusé"

    OCCUPIED = (Status.REGISTERED, Status.CONFIRMED, Status.PRESENT, Status.ABSENT)
    BADGE_STATUSES = (Status.CONFIRMED, Status.PRESENT)
    event = models.ForeignKey(Event, models.PROTECT, verbose_name="événement", related_name="registrations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, verbose_name="compte participant", related_name="registrations",
                             null=True, blank=True, limit_choices_to={"role": Role.PARTICIPANT})
    name = models.CharField("nom complet", max_length=120)
    email = models.EmailField("e-mail", max_length=190)
    category = models.CharField("catégorie", max_length=80, default="Invité")
    preference = models.CharField("préférence de placement", max_length=160, blank=True)
    seat = models.CharField("place attribuée", max_length=80, blank=True)
    status = models.CharField("statut", max_length=20, choices=Status, default=Status.REGISTERED)
    badge_token = models.CharField(max_length=64, unique=True, default=badge_token, editable=False)
    rating = models.PositiveSmallIntegerField("note sur 5", blank=True, null=True,
                                               validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField("avis", blank=True)
    created_at = models.DateTimeField("date d’inscription", auto_now_add=True)

    class Meta:
        db_table = "gestion_participant"
        ordering = ("name", "pk")
        indexes = [models.Index(fields=["event", "status"], name="gestion_par_event_i_a5c412_idx")]
        constraints = [
            models.UniqueConstraint(Lower("email"), F("event"), name="unique_participant_event_email"),
            models.UniqueConstraint(fields=["event", "user"], name="unique_participant_event_user"),
            models.UniqueConstraint(Lower("seat"), F("event"),
                                    condition=Q(status__in=("Inscrit", "Confirmé", "Présent", "Absent")) & ~Q(seat=""),
                                    name="unique_occupied_event_seat"),
            models.CheckConstraint(condition=Q(rating__isnull=True) | Q(rating__range=(1, 5)),
                                   name="participant_rating_range"),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        self.email = self.email.strip().lower()
        if not self.event_id:
            return
        if self.user_id and self.email != self.user.email:
            raise ValidationError({"email": "Utilisez l’adresse e-mail du compte associé."})
        if Participant.objects.filter(event_id=self.event_id, email__iexact=self.email).exclude(pk=self.pk).exists():
            raise ValidationError({"email": "Cette adresse est déjà inscrite à cet événement."})
        if self.status not in self.OCCUPIED:
            return
        if self.event.status == Event.Status.CANCELLED:
            raise ValidationError("Cet événement est annulé.")
        occupied = Participant.objects.filter(status__in=self.OCCUPIED).exclude(pk=self.pk)
        same_event = occupied.filter(event_id=self.event_id)
        if same_event.count() >= self.event.capacity:
            raise ValidationError("La capacité de l’événement est atteinte. Utilisez la liste d’attente.")
        if self.seat and same_event.filter(seat__iexact=self.seat).exists():
            raise ValidationError({"seat": "Cette place est déjà attribuée."})
        identity = Q(email__iexact=self.email)
        if self.user_id:
            identity |= Q(user_id=self.user_id)
        if occupied.filter(identity, event__start_at__lt=self.event.end_at,
                           event__end_at__gt=self.event.start_at).exclude(event_id=self.event_id).exclude(
                               event__status=Event.Status.CANCELLED).exists():
            raise ValidationError("Cette personne est déjà inscrite à un événement sur le même créneau.")


class Complaint(models.Model):
    class Status(models.TextChoices):
        OPEN = "Ouverte", "Ouverte"
        IN_PROGRESS = "En cours", "En cours"
        RESOLVED = "Résolue", "Résolue"

    participant = models.ForeignKey(Participant, models.PROTECT, verbose_name="inscription", related_name="complaints")
    subject = models.CharField("objet", max_length=160)
    message = models.TextField("message")
    status = models.CharField("statut", max_length=20, choices=Status, default=Status.OPEN)
    response = models.TextField("réponse", blank=True)

    class Meta:
        db_table = "gestion_complaint"
        ordering = ("-pk",)
        verbose_name = "réclamation"

    def __str__(self):
        return self.subject


class Document(models.Model):
    participant = models.ForeignKey(Participant, models.PROTECT, related_name="documents")
    original_name = models.CharField("nom du fichier", max_length=190)
    mime = models.CharField("type de fichier", max_length=100)
    size = models.PositiveIntegerField("taille")
    content = models.BinaryField(editable=False)
    created_at = models.DateTimeField("date de dépôt", auto_now_add=True)

    class Meta:
        db_table = "gestion_document"
        ordering = ("-created_at", "-pk")

    def __str__(self):
        return self.original_name
