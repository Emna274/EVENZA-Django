from apps.core.forms import LocalDateTime, RecordForm

from .models import Program, Suggestion


class ProgramForm(RecordForm):
    class Meta:
        model = Program
        fields = ("event", "title", "description", "start_at", "end_at", "speaker", "status")
        widgets = {"start_at": LocalDateTime(), "end_at": LocalDateTime()}


class SuggestionForm(RecordForm):
    class Meta:
        model = Suggestion
        fields = ("event", "title", "start_at", "end_at")
        widgets = {"start_at": LocalDateTime(), "end_at": LocalDateTime()}


def record_form(section, actor, record=None):
    return ProgramForm if section.key == "programs" else SuggestionForm
