from django.core import mail
from django.core import signing
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from apps.evenements.models import Event
from apps.participants.models import Document, Participant
from apps.utilisateurs.models import User
from apps.core.test_support import EvenzaTestCase


class ParticipantsTests(EvenzaTestCase):
    def test_crud_participants(self):
        self.assert_crud("participants", {"event": self.event.pk, "name": "Public",
                                           "email": "public@example.com", "category": "Invité", "status": "Inscrit"},
                         "name", "Public", "Public corrigé")

    def test_participant_waitlist_and_cancellation(self):
        self.event.capacity = 1
        self.event.save(update_fields=["capacity"])
        other = User.objects.create_user("autre@example.com", "Autre")
        self.client.force_login(other)
        self.assertRedirects(self.client.post(self.link("participants", "create"), {"event": self.event.pk}),
                             self.link("participants"))
        waiting = Participant.objects.get(user=other)
        self.assertEqual(waiting.status, Participant.Status.WAITLIST)
        self.client.force_login(self.guest)
        self.assertRedirects(self.client.post(self.link("participants", "update", self.registration),
                                              {"status": "Annulé"}), self.link("participants"))
        self.assertTrue(self.guest.notifications.filter(message__contains="Annulé").exists())
        self.client.force_login(self.organizer)
        url = reverse("record-operation", args=["participants", waiting.pk, "promote"])
        self.assertRedirects(self.client.post(url), self.link("participants", "detail", waiting))
        waiting.refresh_from_db()
        self.assertEqual(waiting.status, Participant.Status.REGISTERED)

    def test_participant_time_conflict(self):
        other = Event.objects.create(
            title="Autre événement", location="Tunis", start_at=self.start, end_at=self.end,
            capacity=10, status=Event.Status.CONFIRMED,
        )
        self.client.force_login(self.guest)
        response = self.client.post(self.link("participants", "create"), {"event": other.pk})
        self.assertFormError(response.context["form"], None,
                             "Cette personne est déjà inscrite à un événement sur le même créneau.")

    def test_invitation_requires_recipient_and_links_inscription(self):
        invitee = User.objects.create_user("invite@example.com", "Invité")
        record = Participant.objects.create(
            event=self.event, name=invitee.name, email=invitee.email, status=Participant.Status.INVITED,
        )
        self.client.force_login(self.organizer)
        self.client.post(reverse("record-operation", args=["participants", record.pk, "invite"]))
        self.assertEqual(mail.outbox[0].to, [invitee.email])
        token = signing.dumps({"pk": record.pk, "email": record.email}, salt="evenza-invitation")
        url = reverse("invitation", args=[token])
        self.client.force_login(self.guest)
        self.assertEqual(self.client.post(url, {"response": "confirm"}).status_code, 403)
        self.client.force_login(invitee)
        self.assertRedirects(self.client.post(url, {"response": "confirm"}), self.link("participants", "detail", record))
        record.refresh_from_db()
        self.assertEqual(record.user, invitee)
        self.assertEqual(record.status, Participant.Status.CONFIRMED)

    def test_private_documents_and_badge_checkin(self):
        self.client.force_login(self.guest)
        file = SimpleUploadedFile("programme.pdf", b"%PDF-1.4\ncontenu")
        url = reverse("upload-document", args=[self.registration.pk])
        self.assertRedirects(self.client.post(url, {"document": file}),
                             self.link("participants", "detail", self.registration))
        document = Document.objects.get()
        download = reverse("download-document", args=[document.pk])
        self.assertEqual(b"".join(self.client.get(download).streaming_content), b"%PDF-1.4\ncontenu")
        badge = self.client.get(reverse("badge", args=[self.registration.pk]))
        self.assertEqual(badge["Content-Type"], "image/svg+xml")
        self.assertIn(b"<svg", badge.content)
        check = reverse("check-in", args=[self.registration.badge_token])
        self.assertEqual(self.client.post(check).status_code, 403)
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get(download).status_code, 404)
        self.client.force_login(self.organizer)
        self.assertEqual(self.client.get(check).status_code, 200)
        self.assertRedirects(self.client.post(check), self.link("participants", "detail", self.registration))
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.status, Participant.Status.PRESENT)
