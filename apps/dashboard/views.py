from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.views.generic import TemplateView

from apps.core.access import MODULES, SECTIONS, allowed, is_admin, scoped

from apps.evenements.models import Event

from .models import Activity


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        user, now = self.request.user, timezone.now()
        events = scoped(user, SECTIONS["events"])
        upcoming = events.filter(start_at__gte=now).exclude(status=Event.Status.CANCELLED)
        first = timezone.localdate().replace(day=1)
        months = [first]
        for _ in range(5):
            months.insert(0, (months[0] - timedelta(days=1)).replace(day=1))
        counts = dict(events.filter(start_at__date__gte=months[0], start_at__date__lte=timezone.localdate()).order_by()
                      .annotate(month=TruncMonth("start_at")).values("month").annotate(total=Count("pk"))
                      .values_list("month", "total"))
        monthly_counts = {month.date(): total for month, total in counts.items()}
        statuses = dict(events.order_by().values("status").annotate(total=Count("pk")).values_list("status", "total"))
        modules = [s for s in SECTIONS.values() if not s.path and allowed(user, s)]
        activities = Activity.objects.select_related("user")
        if not is_admin(user):
            activities = activities.filter(user=user)
        return {
            "title": "Tableau de bord",
            "kpis": [(MODULES[s.module].label, MODULES[s.module].icon, scoped(user, s).count(), s.url())
                     for s in modules if s.key in {"events", "participants", "providers", "resources"}],
            "links": [(MODULES[s.module], s.url()) for s in modules],
            "events": [(event, SECTIONS["events"].url("detail", event.pk)) for event in upcoming[:5]],
            "activity": [(item, SECTIONS[item.entity].label) for item in activities[:8] if item.entity in SECTIONS],
            "event_list_url": SECTIONS["events"].url(),
            "month_rows": [(month.strftime("%m/%Y"), monthly_counts.get(month, 0)) for month in months],
            "status_rows": list(statuses.items()),
            "chart_data": {
                "months": [month.strftime("%m/%Y") for month in months],
                "monthly": [monthly_counts.get(month, 0) for month in months],
                "statuses": list(statuses),
                "totals": list(statuses.values()),
            },
        }
