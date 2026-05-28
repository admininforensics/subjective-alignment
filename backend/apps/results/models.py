from django.db import models

from apps.assessments.models import Domain, Question
from apps.licensing.models import AssessmentSession
from apps.rules.models import Rule


class Response(models.Model):
    session = models.ForeignKey(
        AssessmentSession,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    raw_likert_score = models.PositiveSmallIntegerField()
    effective_likert_score = models.PositiveSmallIntegerField()
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "question"], name="uniq_session_question_response")
        ]


class DomainScoreResult(models.Model):
    session = models.ForeignKey(
        AssessmentSession,
        on_delete=models.CASCADE,
        related_name="domain_results",
    )
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
    score = models.FloatField()
    threshold = models.FloatField()
    triggered = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "domain"], name="uniq_session_domain_result")
        ]


class TriggeredFlag(models.Model):
    session = models.ForeignKey(
        AssessmentSession,
        on_delete=models.CASCADE,
        related_name="triggered_flags",
    )
    rule = models.ForeignKey(Rule, on_delete=models.PROTECT)
    flag = models.CharField(max_length=255)
    insight_snapshot = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "rule"], name="uniq_session_rule_flag")
        ]
