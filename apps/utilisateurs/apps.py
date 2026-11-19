from django.apps import AppConfig


class UtilisateursConfig(AppConfig):
    name = "apps.utilisateurs"
    label = "gestion"  # Identité historique de AUTH_USER_MODEL.
    verbose_name = "Utilisateurs"
