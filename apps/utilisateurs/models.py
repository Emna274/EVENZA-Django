from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower


class Role(models.TextChoices):
    ADMIN = "Administrateur", "Administrateur"
    ORGANIZER = "Organisateur", "Organisateur"
    CLIENT = "Client", "Client"
    PROVIDER = "Prestataire", "Prestataire"
    PARTICIPANT = "Participant", "Participant"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Une adresse e-mail est requise.")
        user = self.model(email=email.strip().lower(), name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.update(role=Role.ADMIN, is_staff=True, is_superuser=True, is_active=True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField("nom complet", max_length=120)
    email = models.EmailField("adresse e-mail", max_length=190, unique=True)
    role = models.CharField("rôle", max_length=20, choices=Role, default=Role.PARTICIPANT)
    phone = models.CharField("téléphone", max_length=30, blank=True)
    availability = models.CharField("disponibilités", max_length=255, blank=True)
    skills = models.CharField("compétences", max_length=255, blank=True)
    is_active = models.BooleanField("compte actif", default=True)
    is_staff = models.BooleanField("accès à l’administration Django", default=False)
    created_at = models.DateTimeField("date de création", auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        ordering = ("name", "pk")
        verbose_name = "utilisateur"
        constraints = [models.UniqueConstraint(Lower("email"), name="evenza_unique_user_email")]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        self.email = self.email.strip().lower()
        if self.pk:
            old = User.objects.filter(pk=self.pk).first()
            if old and old.email != self.email and self.registrations.exists():
                raise ValidationError({"email": "Cette adresse est liée à des inscriptions existantes."})
            if old and old.role != self.role:
                from apps.prestataires.models import Provider

                links = {
                    Role.ADMIN: self.validated_events,
                    Role.ORGANIZER: self.organized_events,
                    Role.CLIENT: self.client_events,
                    Role.PROVIDER: Provider.objects.filter(user=self),
                    Role.PARTICIPANT: self.registrations,
                }
                if links[old.role].exists():
                    raise ValidationError({"role": "Ce compte est déjà lié à des fiches dans ce rôle."})
