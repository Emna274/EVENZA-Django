from datetime import timedelta
from apps.evenements.models import Event
from apps.core.test_support import EvenzaTestCase


class EvenementsTests(EvenzaTestCase):
    def test_crud_events(self):
        self.assert_crud("events", {"title": "Atelier photo", "location": "La Marsa", "capacity": 10,
                                    "budget": 50, "type": "Privé", "status": "Brouillon", **self.period()},
                         "title", "Atelier photo", "Atelier vidéo")

    def test_invalid_dates_and_protected_delete(self):
        data = {"event": self.event.pk, "title": "Session", "status": "Planifié",
                **self.period(self.start - timedelta(hours=1), self.end)}
        response = self.client.post(self.link("programs", "create"), data)
        self.assertFormError(response.context["form"], None,
                             "Le créneau doit être compris dans les dates de l’événement.")
        response = self.client.post(self.link("events", "delete", self.event))
        self.assertContains(response, "Cette fiche est liée")
        self.assertTrue(Event.objects.filter(pk=self.event.pk).exists())

    def test_guest_permissions_and_scoped_relations(self):
        unrelated = Event.objects.create(
            title="Privé", location="Sfax", start_at=self.start, end_at=self.end, capacity=3,
        )
        self.client.force_login(self.guest)
        self.assertEqual(self.client.get(self.link("users")).status_code, 403)
        self.assertEqual(self.client.get(self.link("events", "detail", unrelated)).status_code, 404)
        self.assertEqual(self.client.get(self.link("events", "update", self.event)).status_code, 403)
        self.assertNotContains(self.client.get(self.link("events", "detail", self.event)), "Budget")
        response = self.client.post(self.link("participants", "create"), {"event": self.event.pk})
        self.assertFormError(response.context["form"], None, "Cette adresse est déjà inscrite à cet événement.")
        self.client.force_login(self.organizer)
        response = self.client.post(self.link("programs", "create"), {
            "event": unrelated.pk, "title": "Tentative", "status": "Planifié", **self.period(),
        })
        self.assertTrue(response.context["form"]["event"].errors)
        response = self.client.post(self.link("events", "create"), {
            "title": "Proposition", "status": "Confirmé", "type": "Privé", "capacity": 5, "budget": 0,
            "location": "Tunis", **self.period(),
        })
        self.assertTrue(response.context["form"]["status"].errors)

    def test_create_event_as_client_and_confirm_as_admin(self):
        self.client.force_login(self.customer)
        data = {"title": "Demande", "location": "Tunis", "capacity": 2, "budget": 0, "type": "Privé", **self.period()}
        self.assertRedirects(self.client.post(self.link("events", "create"), {**data, "status": "Confirmé"}),
                             self.link("events"))
        event = Event.objects.get(title="Demande")
        self.assertEqual(event.client, self.customer)
        self.assertEqual(event.status, Event.Status.DRAFT)
        self.client.force_login(self.admin)
        self.assertRedirects(self.client.post(self.link("events", "update", event), {**data, "status": "Confirmé"}),
                             self.link("events"))
        event.refresh_from_db()
        self.assertEqual(event.validator, self.admin)
