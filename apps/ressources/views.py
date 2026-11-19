from apps.core.views import RecordCreate, RecordDetail, RecordList, RecordUpdate

from .forms import AllocationForm, AvailabilityForm, ResourceForm


class ResourceList(RecordList):
    extra_filters = ("category",)


class AllocationList(RecordList):
    date_filter = True


class ResourceDetail(RecordDetail):
    template_name = "ressources/detail.html"
    related_sections = (("allocations", "resource"),)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = AvailabilityForm(self.request.GET or None)
        context["availability_form"] = form
        if form.is_valid():
            context["available_quantity"] = self.object.available_between(**form.cleaned_data)
        return context


class ResourceEditor:
    def record_form(self, section, actor, record=None):
        return AllocationForm if section.key == "allocations" else ResourceForm


class ResourceCreate(ResourceEditor, RecordCreate):
    pass


class ResourceUpdate(ResourceEditor, RecordUpdate):
    pass
