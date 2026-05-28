from django.db import models

from apps.assessments.models import Domain


class RuleType(models.TextChoices):
    PAIRWISE_AND = "PAIRWISE_AND"
    ADVANCED_EXPRESSION = "ADVANCED_EXPRESSION"


class Rule(models.Model):
    code = models.SlugField(max_length=150, unique=True)
    rule_type = models.CharField(max_length=50, choices=RuleType.choices, default=RuleType.PAIRWISE_AND)
    domain_a = models.ForeignKey(
        Domain,
        on_delete=models.PROTECT,
        related_name="rules_as_domain_a",
    )
    domain_b = models.ForeignKey(
        Domain,
        on_delete=models.PROTECT,
        related_name="rules_as_domain_b",
    )
    description = models.TextField(blank=True)
    flag = models.CharField(max_length=255)
    insight = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.code
