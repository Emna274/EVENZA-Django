import secrets
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from apps.evenements.models import Event
from apps.participants.models import Participant
from apps.prestataires.models import Provider, Service
from apps.ressources.models import Resource
from apps.utilisateurs.models import Role, User
from apps.core.access import SECTIONS


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EvenzaTestCase(TestCase):
    password = secrets.token_urlsafe(32)

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("admin@example.com", "Admin", cls.password)
        cls.organizer = User.objects.create_user("orga@example.com", "Organisateur", role=Role.ORGANIZER)
        cls.guest = User.objects.create_user("guest@example.com", "Invitée")
        cls.provider_user = User.objects.create_user("offre@example.com", "Partenaire", role=Role.PROVIDER)
        cls.customer = User.objects.create_user("client@example.com", "Cliente", role=Role.CLIENT)
        cls.start = (timezone.now() + timedelta(days=9)).replace(second=0, microsecond=0)
        cls.end = cls.start + timedelta(hours=4)
        cls.event = Event.objects.create(title="Gala Évenza", location="Tunis", start_at=cls.start,
                                                end_at=cls.end, capacity=8, organizer=cls.organizer,
                                                client=cls.customer, status=Event.Status.CONFIRMED)
        cls.provider = Provider.objects.create(name="Horizon", specialty="Photo", city="Tunis",
                                                      email="photo@example.com", user=cls.provider_user)
        cls.service = Service.objects.create(provider=cls.provider, name="Portraits", price=250)
        cls.resource = Resource.objects.create(name="Projecteurs", quantity=4)
        cls.registration = Participant.objects.create(
            event=cls.event, user=cls.guest, name=cls.guest.name, email=cls.guest.email,
            status=Participant.Status.CONFIRMED,
        )

    def setUp(self):
        self.client.force_login(self.admin)

    @staticmethod
    def local(value):
        return timezone.localtime(value).strftime("%Y-%m-%dT%H:%M")

    def period(self, start=None, end=None):
        return {"start_at": self.local(start or self.start), "end_at": self.local(end or self.end)}

    def link(self, key, action="list", record=None):
        return SECTIONS[key].url(action, record.pk if record else None)

    def assert_crud(self, key, data, field, initial, updated):
        section = SECTIONS[key]
        create_url = self.link(key, "create")
        self.assertEqual(self.client.get(create_url).status_code, 200)
        response = self.client.post(create_url, data)
        self.assertRedirects(response, self.link(key))
        record = section.model.objects.get(**{field: initial})
        self.assertContains(self.client.get(self.link(key)), self.link(key, "detail", record))
        self.assertEqual(self.client.get(self.link(key, "detail", record)).status_code, 200)
        edit = self.link(key, "update", record)
        self.assertEqual(str(self.client.get(edit).context["form"][field].value()), str(initial))
        data[field] = updated
        if key == "users":
            data["password"] = ""
        self.assertRedirects(self.client.post(edit, data), self.link(key))
        record.refresh_from_db()
        self.assertEqual(str(getattr(record, field)), str(updated))
        delete = self.link(key, "delete", record)
        self.assertEqual(self.client.get(delete).status_code, 200)
        self.assertTrue(section.model.objects.filter(pk=record.pk).exists())
        self.assertRedirects(self.client.post(delete), self.link(key))
        self.assertFalse(section.model.objects.filter(pk=record.pk).exists())
