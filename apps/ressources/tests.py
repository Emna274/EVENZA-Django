from datetime import timedelta
from apps.ressources.models import Allocation, Resource
from apps.core.test_support import EvenzaTestCase


class RessourcesTests(EvenzaTestCase):
    def test_crud_resources(self):
        self.assert_crud("resources", {"name": "Chaises", "quantity": 20, "category": "Mobilier",
                                        "status": "Disponible"}, "name", "Chaises", "Fauteuils")

    def test_allocation_crud_and_capacity(self):
        data = {"event": self.event.pk, "resource": self.resource.pk, "status": "Affecté", **self.period()}
        self.assert_crud("allocations", {**data, "quantity": 2}, "quantity", 2, 3)
        self.assertRedirects(self.client.post(self.link("allocations", "create"), {**data, "quantity": 3}),
                             self.link("allocations"))
        response = self.client.post(self.link("allocations", "create"), {**data, "quantity": 2})
        self.assertFormError(response.context["form"], "quantity", "Quantité disponible sur tout ce créneau : 1.")
        response = self.client.post(self.link("resources", "update", self.resource),
                                    {"name": self.resource.name, "category": "Autre", "quantity": 2,
                                     "status": "Disponible"})
        self.assertFormError(response.context["form"], "quantity", "Cette quantité est inférieure au stock déjà affecté.")

    def test_allocation_uses_peak_concurrency_not_sum(self):
        mid = self.start + timedelta(hours=2)
        for start, end in [(self.start, mid), (mid, self.end)]:
            Allocation.objects.create(event=self.event, resource=self.resource, quantity=2,
                                             start_at=start, end_at=end)
        response = self.client.post(self.link("allocations", "create"), {
            "event": self.event.pk, "resource": self.resource.pk, "quantity": 2, "status": "Affecté", **self.period(),
        })
        self.assertRedirects(response, self.link("allocations"))
        response = self.client.get(self.link("resources", "detail", self.resource), self.period())
        self.assertEqual(response.context["available_quantity"], 0)
        self.assertContains(response, "Quantité disponible sur tout le créneau")

    def test_search_filters_pagination_and_csv(self):
        for i in range(14):
            Resource.objects.create(name=f"Photophore {i}", quantity=2)
        response = self.client.get(self.link("resources"), {"q": "photophore", "status": "Disponible"})
        self.assertEqual(response.context["paginator"].count, 14)
        self.assertEqual(len(response.context["rows"]), 12)
        self.assertEqual(self.client.get(self.link("resources"), {"q": "photophore", "page": 2})
                         .context["page_obj"].number, 2)
        response = self.client.get(self.link("resources"), {"q": "photophore", "export": "csv"})
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("Photophore 13", response.content.decode())
        self.assertNotIn("Projecteurs", response.content.decode())
