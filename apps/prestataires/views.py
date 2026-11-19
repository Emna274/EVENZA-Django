from django.db.models import Avg

from apps.core.access import SECTIONS, scoped
from apps.core.views import RecordCreate, RecordDetail, RecordList, RecordUpdate

from .forms import record_form
from .operations import reservation_status_changed


class ProviderList(RecordList):
    template_name = "prestataires/list.html"


class ProviderDetail(RecordDetail):
    related_sections = (("services", "provider"),)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ratings = scoped(self.request.user, SECTIONS["reservations"]).filter(
            service__provider=self.object, rating__isnull=False,
        )
        average = ratings.aggregate(value=Avg("rating"))["value"]
        if average is not None:
            context["details"].append(("note moyenne", f"{average:.1f} / 5"))
        return context


class ProviderCreate(RecordCreate):
    record_form = staticmethod(record_form)


class ProviderUpdate(RecordUpdate):
    record_form = staticmethod(record_form)


class ReservationCreate(ProviderCreate):
    status_changed = staticmethod(reservation_status_changed)


class ReservationUpdate(ProviderUpdate):
    status_changed = staticmethod(reservation_status_changed)
