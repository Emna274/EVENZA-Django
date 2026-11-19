from apps.core.sections import Module, Section

from .models import Program, Suggestion


MODULE = Module("programmes", "Programmes", "Gestion des programmes", "clock",
           "Composez le déroulé de vos événements, session après session.")
SECTIONS = (
    Section("programs", "programmes", "", "Sessions", Program,
            "event title description start_at end_at speaker status", "title event start_at speaker status",
            "title description event__title speaker"),
    Section("suggestions", "programmes", "suggestions/", "Suggestions de programme", Suggestion,
            "event title start_at end_at", "title event start_at status", "title event__title"),
)
