from django.test import TestCase

from apps.assessments.models import Domain
from apps.licensing.models import AssessmentSession, Licence
from apps.organisations.models import Organisation
from apps.results.models import DomainScoreResult, TriggeredFlag
from apps.rules.models import Rule
from apps.rules.services import evaluate_rules
from apps.accounts.models import User
from apps.assessments.models import Assessment


class RuleServiceTests(TestCase):
    def test_pairwise_rule_triggers_only_when_both_domains_triggered(self):
        org = Organisation.objects.create(name="Org")
        respondent = User.objects.create_user(email="r@example.com", username="r", password="pw", organisation=org)
        assessment = Assessment.objects.create(name="A", version="1.0", is_active=True)
        d1 = Domain.objects.create(name="Burnout Risk", threshold=1)
        d2 = Domain.objects.create(name="Authenticity Strain", threshold=1)
        rule = Rule.objects.create(
            code="burnout-auth-energy",
            domain_a=d1,
            domain_b=d2,
            description="",
            flag="Energy Leak",
            insight="Insight text",
        )

        licence = Licence.objects.create(organisation=org, assessment=assessment, assigned_to=respondent)
        session = AssessmentSession.objects.create(licence=licence, respondent=respondent, assessment=assessment)

        DomainScoreResult.objects.create(session=session, domain=d1, score=2, threshold=1, triggered=True)
        DomainScoreResult.objects.create(session=session, domain=d2, score=2, threshold=1, triggered=True)

        flags = evaluate_rules(session)
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0].rule_id, rule.id)
        self.assertEqual(TriggeredFlag.objects.filter(session=session).count(), 1)
