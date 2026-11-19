from apps.accounts.services import notify
from apps.core.access import is_admin
from apps.core.views import RecordCreate, RecordDetail, RecordList, RecordUpdate
from apps.participants.models import Participant
from apps.utilisateurs.models import Role

from .forms import record_form
from .models import Event


def limited_event_access(user):
    return not is_admin(user) and user.role in (Role.PARTICIPANT, Role.PROVIDER)


class EventList(RecordList):
    extra_filters = ("type",)
    date_filter = True

    def get_search_fields(self):
        if limited_event_access(self.request.user):
            return "title location description"
        return super().get_search_fields()


class EventDetail(RecordDetail):
    related_sections = (("programs", "event"), ("participants", "event"),
                        ("reservations", "event"), ("allocations", "event"))

    def get_detail_fields(self):
        fields = super().get_detail_fields()
        if limited_event_access(self.request.user):
            return [field for field in fields if field not in {"budget", "client", "organizer", "validator"}]
        return fields

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user, record = self.request.user, self.object
        if is_admin(user) or user.role == Role.ORGANIZER:
            count = record.registrations.filter(status__in=Participant.OCCUPIED).count()
            context["details"].append(("places occupées", f"{count} / {record.capacity}"))
        return context


class EventEditor:
    record_form = staticmethod(record_form)

    def prepare_record(self, record):
        user = self.request.user
        if user.role == Role.ADMIN and record.status == Event.Status.CONFIRMED and not record.validator_id:
            record.validator = user

    @staticmethod
    def status_changed(record):
        if record.status == Event.Status.CANCELLED:
            for user_id in record.registrations.exclude(user=None).values_list("user_id", flat=True).distinct():
                notify(user_id, f"L’événement « {record} » a été annulé.")


class EventCreate(EventEditor, RecordCreate):
    pass


class EventUpdate(EventEditor, RecordUpdate):
    pass
