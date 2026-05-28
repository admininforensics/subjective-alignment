import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser from env vars if missing."

    def handle(self, *args, **options):
        User = get_user_model()

        email = (os.environ.get("DJANGO_SUPERUSER_EMAIL") or "").strip().lower()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or ""
        username = (os.environ.get("DJANGO_SUPERUSER_USERNAME") or "").strip()

        if not email:
            self.stdout.write("DJANGO_SUPERUSER_EMAIL not set; skipping.")
            return
        if not password:
            self.stdout.write("DJANGO_SUPERUSER_PASSWORD not set; skipping.")
            return

        if not username:
            # Custom user requires username; default to email local-part.
            username = email.split("@")[0][:150]

        existing = User.objects.filter(email=email).first()
        if existing:
            if not existing.is_superuser or not existing.is_staff:
                existing.is_staff = True
                existing.is_superuser = True
                existing.save(update_fields=["is_staff", "is_superuser"])
                self.stdout.write(f"Upgraded existing user to superuser: {email}")
            else:
                self.stdout.write(f"Superuser already exists: {email}")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(f"Created superuser: {email}")
