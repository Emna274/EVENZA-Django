from calendar import Calendar, monthrange
from datetime import date, datetime, time, timedelta

from django import template
from django.utils import timezone

from apps.evenements.models import Event
from apps.core.access import SECTIONS, allowed, scoped

register = template.Library()

STATUS_STYLES = {
    "positive": {"Confirmé", "Actif", "Disponible", "Présent", "Acceptée", "Validée", "Résolue"},
    "pending": {"En préparation", "En attente", "Liste d’attente", "En cours", "Maintenance", "Réservé"},
    "negative": {"Annulé", "Annulée", "Inactif", "Refusé", "Refusée", "Rejetée", "Indisponible", "Absent"},
    "neutral": {"Brouillon", "Terminé", "Planifié", "Inscrit", "Invité", "Affecté", "Ouverte"},
}
EVENT_COVERS = {
    Event.Type.WEDDING: "reception",
    Event.Type.BUSINESS: "conference",
    Event.Type.CONFERENCE: "conference",
    Event.Type.PRIVATE: "private",
}


@register.filter
def status_style(value):
    return next((style for style, statuses in STATUS_STYLES.items() if value in statuses), "")


@register.filter
def status_column(section, index):
    return section.columns.split()[index] in {"status", "is_active"}


@register.filter
def event_cover(value):
    return f"images/{EVENT_COVERS.get(value, 'gala')}-card.webp"


@register.simple_tag(takes_context=True)
def event_creation_url(context):
    section = SECTIONS["events"]
    if allowed(context["request"].user, section, "add"):
        return section.url("create")
    return ""


def selected_month(value, today):
    try:
        month = date.fromisoformat(f"{value}-01")
    except ValueError:
        return today.replace(day=1)
    return month if 2 <= month.year <= 9998 else today.replace(day=1)


@register.inclusion_tag("components/calendar.html", takes_context=True)
def event_calendar(context):
    request = context["request"]
    today = timezone.localdate()
    month = selected_month(request.GET.get("mois", ""), today)
    previous_month = (month - timedelta(days=1)).replace(day=1)
    next_month = month + timedelta(days=monthrange(month.year, month.month)[1])
    start = timezone.make_aware(datetime.combine(month, time.min))
    end = timezone.make_aware(datetime.combine(next_month, time.min))
    section = SECTIONS["events"]
    events = scoped(request.user, section).filter(start_at__lt=end, end_at__gt=start)
    totals = {}
    for starts, ends in events.values_list("start_at", "end_at"):
        day = max(month, timezone.localdate(starts))
        last_day = min(next_month - timedelta(days=1), timezone.localdate(ends - timedelta(microseconds=1)))
        while day <= last_day:
            totals[day] = totals.get(day, 0) + 1
            day += timedelta(days=1)
    weeks = [
        [{"date": day, "current_month": day.month == month.month, "today": day == today, "count": totals.get(day, 0)}
         for day in week]
        for week in Calendar().monthdatescalendar(month.year, month.month)
    ]
    return {
        "month": month,
        "previous_month": previous_month if previous_month.year >= 2 else None,
        "next_month": next_month if next_month.year <= 9998 else None,
        "weeks": weeks,
        "event_list_url": section.url(),
    }
