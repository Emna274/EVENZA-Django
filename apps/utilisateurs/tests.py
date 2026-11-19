from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.core.test_support import EvenzaTestCase


class UtilisateursTests(EvenzaTestCase):
    def test_existing_user_identity_and_admin_bookmarks(self):
        self.assertEqual(get_user_model()._meta.label, "gestion.User")
        self.assertEqual(get_user_model()._meta.db_table, "gestion_user")
        old = reverse("admin:gestion_event_change", args=[self.event.pk])
        new = reverse("admin:evenements_event_change", args=[self.event.pk])
        self.assertEqual(old, f"/admin/gestion/event/{self.event.pk}/change/")
        self.assertEqual(self.client.get(old).status_code, 200)
        self.assertEqual(self.client.get(new).status_code, 200)

    def test_crud_users(self):
        self.assert_crud("users", {"name": "Compte test", "email": "nouveau@example.com",
                                   "role": "Client", "is_active": "on", "password": self.password},
                         "name", "Compte test", "Compte modifié")
