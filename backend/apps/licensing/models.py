from django.conf import settings
from django.db import models

from apps.assessments.models import Assessment
from apps.organisations.models import Organisation


class LicenceStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    CONSUMED = "CONSUMED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class SessionStatus(models.TextChoices):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    LOCKED = "LOCKED"
    RESET = "RESET"


class Licence(models.Model):
    code = models.CharField(max_length=64, unique=True, null=True, blank=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="licences",
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.PROTECT)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_licences",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="licences_assigned_by_me",
    )
    status = models.CharField(max_length=50, choices=LicenceStatus.choices, default=LicenceStatus.AVAILABLE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)


class AssessmentSession(models.Model):
    licence = models.OneToOneField(Licence, on_delete=models.PROTECT, related_name="session")
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment_sessions",
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.PROTECT)
    status = models.CharField(max_length=50, choices=SessionStatus.choices, default=SessionStatus.NOT_STARTED)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
