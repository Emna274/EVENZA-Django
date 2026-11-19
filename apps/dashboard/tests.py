from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from apps.evenements.models import Event
from apps.core.test_support import EvenzaTestCase


class DashboardTests(EvenzaTestCase):
    def test_dashboard_real_data_and_navigation(self):
        start = timezone.now() - timedelta(days=1)
        Event.objects.create(title="Événement passé", start_at=start, end_at=start + timedelta(hours=1),
                                    location="Tunis", capacity=15)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, self.event.title)
        self.assertEqual(sum(response.context["chart_data"]["monthly"]), 1)
        self.assertEqual(sum(response.context["chart_data"]["totals"]), 2)
        for key in ("events", "providers", "users", "programs", "participants", "resources"):
            self.assertContains(response, self.link(key))

    def test_calendar_matches_scoped_event_date_filter(self):
        day = timezone.localtime(self.start).date()
        other = Event.objects.create(
            title="Événement hors de mon espace", start_at=self.start,
            end_at=self.end, location="Sousse", capacity=3,
        )
        url = reverse("dashboard")
        month = day.strftime("%Y-%m")
        date_url = f'{self.link("events")}?date={day}'
        self.assertContains(self.client.get(url, {"mois": month}), ", 2 événements")
        self.client.force_login(self.organizer)
        response = self.client.get(url, {"mois": month})
        self.assertContains(response, date_url)
        self.assertContains(response, ", 1 événement")
        self.assertNotContains(response, ", 2 événements")
        filtered = self.client.get(date_url)
        self.assertContains(filtered, self.event.title)
        self.assertNotContains(filtered, other.title)
        self.assertContains(self.client.get(url, {"mois": "10000-13"}), 'id="calendrier"')

    def test_dashboard_create_shortcut_matches_permissions(self):
        create_url = self.link("events", "create")
        self.assertContains(self.client.get(reverse("dashboard")), f'href="{create_url}"')
        self.client.force_login(self.guest)
        self.assertNotContains(self.client.get(reverse("dashboard")), f'href="{create_url}"')
