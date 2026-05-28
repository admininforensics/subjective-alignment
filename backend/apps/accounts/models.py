from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.organisations.models import Organisation


class UserRole(models.TextChoices):
    RESPONDENT = "RESPONDENT"
    MANAGER = "MANAGER"
    ORG_ADMIN = "ORG_ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    organisation = models.ForeignKey(
        Organisation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )
    role = models.CharField(max_length=50, choices=UserRole.choices, default=UserRole.RESPONDENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


class ManagerAssignment(models.Model):
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="managed_assignments",
    )
    respondent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="manager_assignments",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["manager", "respondent"],
                name="uniq_manager_assignment",
            )
        ]
