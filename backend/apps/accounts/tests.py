from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.password_reset import build_reset_link
from apps.organisations.models import Organisation


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organisation.objects.create(name="Test Org")
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="old-password",
            organisation=self.org,
        )

    def test_request_reset_sends_email_for_existing_user(self):
        res = self.client.post(
            "/api/auth/password-reset/",
            {"email": "user@example.com"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn("/reset-password?uid=", mail.outbox[0].body)

    def test_request_reset_unknown_email_still_ok(self):
        res = self.client.post(
            "/api/auth/password-reset/",
            {"email": "missing@example.com"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_confirm_reset_updates_password(self):
        uid, token, _ = build_reset_link(self.user)
        res = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"uid": uid, "token": token, "password": "new-password"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-password"))

    def test_confirm_reset_rejects_invalid_token(self):
        uid, _, _ = build_reset_link(self.user)
        res = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"uid": uid, "token": "bad-token", "password": "new-password"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)
