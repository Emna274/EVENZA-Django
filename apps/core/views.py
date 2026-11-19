import csv
import io
from datetime import datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count
from django.db.models.deletion import ProtectedError, RestrictedError
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .access import MODULES, SECTIONS, allowed, scoped, search_query
from .audit import record_activity, record_changes
from .forms import record_form
from .operations import available_operations


class SectionView(LoginRequiredMixin, UserPassesTestMixin):
    section = None
    permission = "view"

    def test_func(self):
        return allowed(self.request.user, self.section, self.permission)

    def get_queryset(self):
        queryset = scoped(self.request.user, self.section)
        relations = [field.name for field in self.section.model._meta.fields if field.is_relation]
        return queryset.select_related(*relations) if relations else queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user, section = self.request.user, self.section
        context.update(
            module=MODULES[section.module],
            section=section,
            tabs=[(other, other.url()) for other in SECTIONS.values()
                  if other.module == section.module and allowed(user, other)],
            list_url=section.url(),
            create_url=section.url("create") if allowed(user, section, "add") else None,
        )
        return context

    def row_actions(self, record):
        user, section = self.request.user, self.section
        return {
            "view_url": section.url("detail", record.pk),
            "edit_url": section.url("update", record.pk) if allowed(user, section, "change") else None,
            "delete_url": (section.url("delete", record.pk) if record != user and
                           allowed(user, section, "delete") else None),
        }


def cell_value(record, field):
    value = getattr(record, f"get_{field}_display", None)
    if value:
        return value()
    value = getattr(record, field)
    if isinstance(value, bool):
        return "Actif" if value else "Inactif"
    return "—" if value is None or value == "" else value


class RecordList(SectionView, ListView):
    template_name = "gestion/list.html"
    paginate_by = 12
    extra_filters = ()
    date_filter = False

    def get_search_fields(self):
        return self.section.search

    def get_queryset(self):
        self.base_queryset = super().get_queryset()
        queryset = self.base_queryset
        self.query = self.request.GET.get("q", "").strip()[:200]
        fields = self.get_search_fields()
        for word in self.query.split():
            queryset = queryset.filter(search_query(word, fields))
        self.filters = []
        for field in (self.section.filter, *self.extra_filters):
            model_field = self.section.model._meta.get_field(field)
            options = dict(model_field.flatchoices)
            if field == "is_active":
                options = {"1": "Actif", "0": "Inactif"}
            value = self.request.GET.get(field, "")
            if value in options:
                queryset = queryset.filter(**{field: value == "1" if field == "is_active" else value})
            else:
                value = ""
            self.filters.append({"name": field, "label": model_field.verbose_name.capitalize(),
                                 "options": options.items(), "selected": value})
        self.chosen_date = None
        if self.date_filter:
            try:
                self.chosen_date = parse_date(self.request.GET.get("date", ""))
            except ValueError:
                pass
            if self.chosen_date:
                start = timezone.make_aware(datetime.combine(self.chosen_date, time.min))
                end = start + timedelta(days=1)
                queryset = queryset.filter(start_at__lt=end, end_at__gt=start)
        self.entity_filters = []
        for field in ("event", "resource"):
            if field not in self.section.fields.split():
                continue
            model_field = self.section.model._meta.get_field(field)
            options = scoped(self.request.user, next(section for section in SECTIONS.values()
                                                     if section.model is model_field.related_model))
            selected = self.request.GET.get(field, "")
            if selected.isascii() and selected.isdecimal() and len(selected) <= 18:
                queryset = queryset.filter(**{f"{field}_id": int(selected)})
            else:
                selected = ""
            self.entity_filters.append({
                "name": field,
                "label": model_field.verbose_name.capitalize(),
                "options": ((str(record.pk), str(record)) for record in options),
                "selected": selected,
            })
        return queryset

    def get(self, request, *args, **kwargs):
        if request.GET.get("export") == "csv":
            queryset = self.get_queryset()
            output = io.StringIO()
            writer = csv.writer(output, delimiter=";")
            columns = self.section.columns.split()
            writer.writerow([self.section.model._meta.get_field(field).verbose_name for field in columns])
            for record in queryset.iterator():
                row = [str(cell_value(record, field)) for field in columns]
                writer.writerow(["'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value for value in row])
            return HttpResponse("\ufeff" + output.getvalue(), content_type="text/csv; charset=utf-8",
                                headers={"Content-Disposition": f'attachment; filename="{self.section.key}.csv"'})
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        columns = self.section.columns.split()
        context.update(
            title=MODULES[self.section.module].title,
            subtitle=MODULES[self.section.module].description,
            headings=[self.section.model._meta.get_field(field).verbose_name for field in columns],
            rows=[{"cells": [cell_value(record, field) for field in columns], **self.row_actions(record)}
                  for record in context["object_list"]],
            filters=[*self.filters, *self.entity_filters],
            query=self.query,
            date_filter=self.date_filter,
            chosen_date=self.chosen_date,
            total_count=self.base_queryset.count(),
            filtered_count=context["paginator"].count,
        )
        field = self.section.filter
        choices = dict(self.section.model._meta.get_field(field).flatchoices)
        breakdown = self.base_queryset.order_by().values(field).annotate(total=Count("pk"))
        context["breakdown"] = [(choices.get(row[field], row[field]), row["total"]) for row in breakdown]
        return context


class RecordDetail(SectionView, DetailView):
    template_name = "gestion/detail.html"
    related_sections = ()

    def get_detail_fields(self):
        return self.section.fields.split()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user, record = self.request.user, self.object
        fields = self.get_detail_fields()
        groups = []
        for related_key, field in self.related_sections:
            section = SECTIONS[related_key]
            if allowed(user, section):
                records = scoped(user, section).filter(**{field: record})
                groups.append((section.label, [(str(item), section.url("detail", item.pk)) for item in records[:10]]))
        context.update(
            title=str(record),
            details=[(self.section.model._meta.get_field(field).verbose_name, cell_value(record, field)) for field in fields],
            related_groups=groups,
            operations=available_operations(user, self.section, record),
            **self.row_actions(record),
        )
        return context


class RecordEditor(SectionView):
    template_name = "gestion/form.html"
    record_form = staticmethod(record_form)
    status_changed = None

    def prepare_record(self, record):
        pass

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_form_class(self):
        self.previous_status = getattr(self.object, "status", None)
        return self.record_form(self.section, self.request.user, self.object)

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), "actor": self.request.user}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Modifier · {self.object}" if self.object else f"Ajouter · {self.section.label}"
        return context

    def form_valid(self, form):
        self.prepare_record(form.instance)
        response = super().form_valid(form)
        if self.request.user == self.object and form.cleaned_data.get("password"):
            update_session_auth_hash(self.request, self.object)
        record_changes(self.request.user, self.section, self.object,
                       "Modification" if self.permission == "change" else "Création", self.previous_status, self.status_changed)
        messages.success(self.request, "Les informations ont été enregistrées.")
        return response

    def get_success_url(self):
        return self.section.url()


class RecordCreate(RecordEditor, CreateView):
    permission = "add"


class RecordUpdate(RecordEditor, UpdateView):
    permission = "change"


class RecordDelete(SectionView, DeleteView):
    permission = "delete"
    template_name = "gestion/delete.html"

    def get_object(self, queryset=None):
        record = super().get_object(queryset)
        if record == self.request.user:
            raise PermissionDenied
        return record

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Supprimer · {self.object}"
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        pk = self.object.pk
        try:
            response = super().form_valid(form)
        except (ProtectedError, RestrictedError):
            form.add_error(None, "Cette fiche est liée à d’autres enregistrements. Traitez d’abord les fiches associées.")
            return self.form_invalid(form)
        record_activity(self.request.user, self.section, pk, "Suppression")
        messages.success(self.request, "La fiche a été supprimée.")
        return response

    def get_success_url(self):
        return self.section.url()
