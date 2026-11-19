from django.utils import timezone

from apps.core.views import RecordCreate, RecordDelete, RecordDetail, RecordList, RecordUpdate
from apps.evenements.models import Event

from .forms import AccountForm
from .models import Role


class UserRecords:
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_superuser=False, is_staff=False)
        return queryset


class UserList(UserRecords, RecordList):
    extra_filters = ("is_active",)


class UserDetail(UserRecords, RecordDetail):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        record = self.object
        if record.role == Role.ORGANIZER:
            upcoming = record.organized_events.filter(end_at__gte=timezone.now()).exclude(status=Event.Status.CANCELLED)
            context["details"].append(("événements en cours ou à venir", upcoming.count()))
        return context


class UserCreate(UserRecords, RecordCreate):
    def record_form(self, section, actor, record=None):
        return AccountForm


class UserUpdate(UserRecords, RecordUpdate):
    def record_form(self, section, actor, record=None):
        return AccountForm


class UserDelete(UserRecords, RecordDelete):
    pass
