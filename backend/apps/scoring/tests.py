from django.test import TestCase

from apps.assessments.models import Assessment, Area, Domain, Question, QuestionDomainWeight, SubArea
from apps.licensing.models import AssessmentSession, Licence, LicenceStatus, SessionStatus
from apps.organisations.models import Organisation
from apps.results.models import Response
from apps.scoring.services import effective_score, score_session
from apps.accounts.models import User


class ScoringServiceTests(TestCase):
    def test_effective_score_reverse_logic(self):
        self.assertEqual(effective_score(1, True), 5)
        self.assertEqual(effective_score(5, True), 1)
        self.assertEqual(effective_score(3, True), 3)
        self.assertEqual(effective_score(4, False), 4)

    def test_weighted_scoring_and_threshold_trigger(self):
        org = Organisation.objects.create(name="Org")
        respondent = User.objects.create_user(
            email="r@example.com",
            username="r",
            password="pw",
            organisation=org,
        )
        assessment = Assessment.objects.create(name="A", version="1.0", is_active=True)
        area = Area.objects.create(name="Context")
        sub = SubArea.objects.create(area=area, name="Economic")
        domain = Domain.objects.create(name="Burnout Risk", threshold=3.0)
        q = Question.objects.create(
            assessment=assessment,
            area=area,
            subarea=sub,
            text="Q1",
            order=1,
            reverse_logic=True,
        )
        QuestionDomainWeight.objects.create(question=q, domain=domain, weight=1.0)

        licence = Licence.objects.create(
            organisation=org,
            assessment=assessment,
            assigned_to=respondent,
            status=LicenceStatus.IN_PROGRESS,
        )
        session = AssessmentSession.objects.create(
            licence=licence,
            respondent=respondent,
            assessment=assessment,
            status=SessionStatus.IN_PROGRESS,
        )
        Response.objects.create(session=session, question=q, raw_likert_score=1, effective_likert_score=1)

        results = score_session(session)
        r = results["Burnout Risk"]
        self.assertEqual(r.score, 5.0)
        self.assertTrue(r.triggered)
