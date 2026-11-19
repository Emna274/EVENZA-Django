"""Imports historiques sérialisés par la migration initiale."""

from apps.participants.models import badge_token
from apps.utilisateurs.models import UserManager

__all__ = ["UserManager", "badge_token"]
