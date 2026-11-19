import secrets

from django.core import mail
from django.test import Client
from django.urls import reverse
import re
from apps.accounts.models import LoginAlert, LoginAttempt
from apps.ressources.models import Resource
from apps.utilisateurs.models import Role, User
from apps.core.test_support import EvenzaTestCase


class AccountsTests(EvenzaTestCase):
    def test_login_logout_signup_reset_and_csrf(self):
        self.client.logout()
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("login") + "?next=/")
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        self.assertRedirects(self.client.post(reverse("signup"), {
            "name": "Nouveau", "email": "Inscription@Example.com", "password": self.password, "role": "Administrateur",
        }), reverse("login"))
        new = User.objects.get(email="inscription@example.com")
        self.assertEqual(new.role, Role.PARTICIPANT)
        self.assertTrue(new.check_password(self.password))
        self.assertRedirects(self.client.post(reverse("login"), {
            "username": "INSCRIPTION@example.com", "password": self.password,
        }), reverse("dashboard"))
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("login"))
        self.assertRedirects(self.client.post(reverse("password_reset"), {"email": new.email}),
                             reverse("password_reset_done"))
        link = re.search(r"http://testserver(\S+)", mail.outbox[-1].body).group(1)
        response = self.client.get(link, follow=True)
        self.assertContains(response, "Définir un mot de passe")
        new_password = secrets.token_urlsafe(32)
        self.assertRedirects(self.client.post(response.redirect_chain[-1][0], {
            "new_password1": new_password, "new_password2": new_password,
        }), reverse("password_reset_complete"))
        new.refresh_from_db()
        self.assertTrue(new.check_password(new_password))
        protected = Client(enforce_csrf_checks=True)
        protected.force_login(self.admin)
        self.assertEqual(protected.post(self.link("resources", "delete", self.resource)).status_code, 403)
        self.assertTrue(Resource.objects.filter(pk=self.resource.pk).exists())

    def test_login_attempt_alert_and_rate_limit(self):
        self.client.logout()
        for _ in range(10):
            response = self.client.post(reverse("login"), {"username": self.admin.email, "password": "wrong"})
            self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse("login"), {"username": self.admin.email, "password": self.password})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(LoginAttempt.objects.count(), 10)
        self.assertTrue(LoginAlert.objects.filter(email=self.admin.email).exists())
