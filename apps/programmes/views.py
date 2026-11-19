from apps.core.views import RecordCreate, RecordDetail, RecordList, RecordUpdate

from .forms import record_form


class ProgramList(RecordList):
    date_filter = True


class SuggestionDetail(RecordDetail):
    def get_detail_fields(self):
        return [*super().get_detail_fields(), "status"]


class ProgramCreate(RecordCreate):
    template_name = "programmes/form.html"
    record_form = staticmethod(record_form)


class ProgramUpdate(RecordUpdate):
    template_name = "programmes/form.html"
    record_form = staticmethod(record_form)
