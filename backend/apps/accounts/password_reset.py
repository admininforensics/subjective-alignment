from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.accounts.models import User


def build_reset_link(user: User) -> tuple[str, str, str]:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    base = settings.FRONTEND_URL.rstrip("/")
    link = f"{base}/reset-password?uid={uid}&token={token}"
    return uid, token, link


def send_password_reset_email(user: User) -> None:
    _, _, link = build_reset_link(user)
    subject = "Reset your Subjective Alignment password"
    message = (
        f"Hi,\n\n"
        f"Use the link below to reset your password. It expires after a limited time.\n\n"
        f"{link}\n\n"
        f"If you did not request this, you can ignore this email.\n"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def user_from_uid(uid: str) -> User | None:
    try:
        pk = force_str(urlsafe_base64_decode(uid))
        return User.objects.get(pk=pk)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def reset_password(uid: str, token: str, password: str) -> User:
    user = user_from_uid(uid)
    if user is None or not default_token_generator.check_token(user, token):
        raise ValueError("Invalid or expired reset link.")
    user.set_password(password)
    user.save(update_fields=["password"])
    return user
