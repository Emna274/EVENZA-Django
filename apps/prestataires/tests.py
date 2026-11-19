from apps.prestataires.models import Reservation
from apps.core.test_support import EvenzaTestCase


class PrestatairesTests(EvenzaTestCase):
    def test_crud_providers(self):
        self.assert_crud("providers", {"name": "Lumière", "specialty": "Traiteur", "city": "Tunis",
                                       "email": "chef@example.com", "status": "Disponible"},
                         "name", "Lumière", "Au soleil")

    def test_services_reservations_and_complaints(self):
        self.assert_crud("services", {"provider": self.provider.pk, "name": "Montage", "price": "19.50",
                                      "status": "Actif"}, "name", "Montage", "Retouches")
        self.assert_crud("reservations", {"event": self.event.pk, "service": self.service.pk,
                                          "amount": "21.50", "status": "En attente"}, "amount", "21.50", "42.50")
        self.assert_crud("complaints", {"participant": self.registration.pk, "subject": "Accès",
                                        "message": "Préciser l’entrée.", "status": "Ouverte"},
                         "subject", "Accès", "Entrée")

    def test_providers_card_view_preserves_actions_and_filtered_export(self):
        response = self.client.get(self.link("providers"), {"vue": "cartes", "q": "Horizon"})
        self.assertContains(response, 'class="provider-card"')
        for action in ("detail", "update", "delete"):
            self.assertContains(response, self.link("providers", action, self.provider))
        export = self.client.get(self.link("providers"), {"vue": "cartes", "q": "Horizon", "export": "csv"})
        self.assertIn("Horizon", export.content.decode())

    def test_provider_can_accept_but_cannot_change_amount(self):
        reservation = Reservation.objects.create(event=self.event, service=self.service, amount=50)
        self.client.force_login(self.provider_user)
        self.assertRedirects(self.client.post(self.link("reservations", "update", reservation),
                                              {"status": "Acceptée", "amount": 1}), self.link("reservations"))
        reservation.refresh_from_db()
        self.assertEqual(reservation.amount, 50)
        self.assertEqual(reservation.status, Reservation.Status.ACCEPTED)
        self.assertTrue(self.organizer.notifications.filter(message__contains="Acceptée").exists())
        self.assertEqual(self.client.get(self.link("resources")).status_code, 403)
