from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name="notifications")
    message = models.CharField("message", max_length=500)
    read_at = models.DateTimeField("lue le", null=True, blank=True)
    created_at = models.DateTimeField("date", auto_now_add=True)

    class Meta:
        db_table = "gestion_notification"
        ordering = ("-created_at", "-pk")

    def __str__(self):
        return self.message


class LoginAttempt(models.Model):
    email = models.CharField(max_length=190, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    success = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gestion_loginattempt"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["email", "created_at"], name="gestion_log_email_9e94bb_idx"), models.Index(fields=["ip", "created_at"], name="gestion_log_ip_b68cc7_idx")]

    def __str__(self):
        return self.email


class LoginAlert(models.Model):
    email = models.EmailField(max_length=190, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gestion_loginalert"
        ordering = ("-created_at", "-pk")
        verbose_name = "alerte de connexion"

    def __str__(self):
        return self.email or "Connexions échouées"
