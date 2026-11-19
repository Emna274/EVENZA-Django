from django import forms

from apps.core.forms import LocalDateTime, RecordForm, StyledForm

from .models import Allocation, Resource


class ResourceForm(RecordForm):
    class Meta:
        model = Resource
        fields = ("name", "category", "quantity", "status", "description")


class AllocationForm(RecordForm):
    class Meta:
        model = Allocation
        fields = ("event", "resource", "quantity", "start_at", "end_at", "status")
        widgets = {"start_at": LocalDateTime(), "end_at": LocalDateTime()}


class AvailabilityForm(StyledForm, forms.Form):
    start_at = forms.DateTimeField(label="Début du créneau", widget=LocalDateTime())
    end_at = forms.DateTimeField(label="Fin du créneau", widget=LocalDateTime())

    def clean(self):
        data = super().clean()
        if "start_at" in data and "end_at" in data and data["end_at"] <= data["start_at"]:
            self.add_error("end_at", "La fin doit être postérieure au début.")
        return data
