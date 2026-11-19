from django.conf import settings
from django.db import models


class Activity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True, blank=True)
    entity = models.CharField("gestion", max_length=60)
    record_id = models.PositiveBigIntegerField("identifiant")
    action = models.CharField("action", max_length=60)
    created_at = models.DateTimeField("date", auto_now_add=True)

    class Meta:
        db_table = "gestion_activity"
        ordering = ("-created_at", "-pk")
        verbose_name = "activité"

    def __str__(self):
        return f"{self.action} · {self.entity}"
