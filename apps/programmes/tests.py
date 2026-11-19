from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from apps.programmes.models import Program, Suggestion
from apps.core.test_support import EvenzaTestCase


class ProgrammesTests(EvenzaTestCase):
    def test_crud_programs(self):
        self.assert_crud("programs", {"event": self.event.pk, "title": "Petit déjeuner",
                                      "status": "Planifié", **self.period()},
                         "title", "Petit déjeuner", "Buffet")

    def test_session_date_filter_ignores_exact_midnight_end(self):
        day = timezone.localtime(self.start).replace(hour=0, minute=0)
        for title, start, end in [("Veille", day - timedelta(hours=1), day),
                                  ("Matin", day, day + timedelta(hours=1))]:
            Program.objects.create(event=self.event, title=title, start_at=start, end_at=end)
        response = self.client.get(self.link("programs"), {"date": day.date().isoformat()})
        self.assertContains(response, "Matin")
        self.assertNotContains(response, "Veille")

    def test_suggestions_can_be_approved_once(self):
        self.client.force_login(self.organizer)
        response = self.client.post(self.link("suggestions", "create"), {
            "event": self.event.pk, "title": "Ouverture", **self.period(),
        })
        self.assertRedirects(response, self.link("suggestions"))
        record = Suggestion.objects.get()
        url = reverse("record-operation", args=["suggestions", record.pk, "approve"])
        self.assertRedirects(self.client.post(url), self.link("suggestions", "detail", record))
        self.assertEqual(self.client.post(url).status_code, 403)
        session = Program.objects.get(title=record.title)
        self.assertEqual(session.event, self.event)
