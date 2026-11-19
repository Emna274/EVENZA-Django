from apps.core.sections import Module, Section

from .models import Complaint, Participant


MODULE = Module("participants", "Participants", "Gestion des participants", "people",
           "Retrouvez vos invités et suivez leurs inscriptions et présences.")
SECTIONS = (
    Section("participants", "participants", "", "Inscriptions", Participant,
            "event user name email category preference seat status rating feedback", "name email event seat status",
            "name email category event__title seat"),
    Section("complaints", "participants", "reclamations/", "Réclamations", Complaint,
            "participant subject message status response", "subject participant status",
            "subject participant__name participant__event__title"),
)
