from apps.core.sections import Module, Section

from .models import Event


MODULE = Module("evenements", "Événements", "Gestion des événements", "calendar-event",
           "Planifiez vos événements et suivez leur avancement.")
SECTIONS = (
    Section("events", "evenements", "", "Événements", Event,
            "title description start_at end_at location type capacity budget status client organizer validator",
            "title start_at location type status", "title location description client__name organizer__name"),
)
