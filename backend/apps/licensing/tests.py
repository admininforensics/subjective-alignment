from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.assessments.models import Assessment
from apps.licensing.models import Licence, LicenceStatus
from apps.licensing.models import AssessmentSession, SessionStatus
from apps.licensing.services import (
    delete_latest_completed_session,
    ensure_testing_licence,
    get_dashboard_info,
    restart_in_progress_session,
    save_response,
    simulate_survey_completion,
    start_session_for_user,
)
from apps.assessments.models import Area, Domain, Question, QuestionDomainWeight, SubArea
from apps.results.models import DomainScoreResult, Response
from apps.organisations.models import Organisation


@override_settings(SKIP_LICENCE_REQUIREMENT=True)
class SkipLicenceRequirementTests(TestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="Test Org")
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="pw",
            organisation=self.org,
            role=UserRole.RESPONDENT,
        )
        Assessment.objects.create(name="Test Assessment", version="1.0", is_active=True)

    def test_ensure_testing_licence_auto_assigns(self):
        self.assertFalse(Licence.objects.filter(assigned_to=self.user).exists())
        ensure_testing_licence(self.user)
        licence = Licence.objects.get(assigned_to=self.user)
        self.assertEqual(licence.status, LicenceStatus.ASSIGNED)

    def test_dashboard_info_includes_auto_licence(self):
        info = get_dashboard_info(self.user)
        self.assertIsNotNone(info.assigned_licence)

    def test_ensure_testing_licence_assigns_dev_org_when_missing(self):
        user = User.objects.create_user(
            email="solo@example.com",
            username="solo",
            password="pw",
            role=UserRole.RESPONDENT,
        )
        self.assertIsNone(user.organisation_id)
        ensure_testing_licence(user)
        user.refresh_from_db()
        self.assertIsNotNone(user.organisation_id)
        self.assertTrue(Licence.objects.filter(assigned_to=user).exists())


class SessionManagementTests(TestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="Test Org")
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="pw",
            organisation=self.org,
            role=UserRole.RESPONDENT,
        )
        self.assessment = Assessment.objects.create(name="Test Assessment", version="1.0", is_active=True)
        self.licence = Licence.objects.create(
            organisation=self.org,
            assessment=self.assessment,
            assigned_to=self.user,
            status=LicenceStatus.ASSIGNED,
        )
        area = Area.objects.create(name="A")
        sub = SubArea.objects.create(area=area, name="S")
        self.question = Question.objects.create(
            assessment=self.assessment,
            area=area,
            subarea=sub,
            order=1,
            text="Q1",
        )

    def test_restart_clears_answers_and_starts_fresh_session(self):
        session = start_session_for_user(self.user)
        save_response(session=session, question=self.question, raw_likert_score=3)
        self.assertEqual(Response.objects.filter(session=session).count(), 1)

        new_session = restart_in_progress_session(user=self.user)
        self.assertNotEqual(new_session.id, session.id)
        self.assertFalse(Response.objects.filter(session_id=session.id).exists())
        self.assertEqual(Response.objects.filter(session=new_session).count(), 0)

    def test_delete_latest_completed_removes_session_but_keeps_licence(self):
        session = start_session_for_user(self.user)
        save_response(session=session, question=self.question, raw_likert_score=4)
        session.status = SessionStatus.COMPLETED
        session.completed_at = timezone.now()
        session.save(update_fields=["status", "completed_at"])
        licence = Licence.objects.get(id=session.licence_id)
        licence.status = LicenceStatus.CONSUMED
        licence.consumed_at = timezone.now()
        licence.save(update_fields=["status", "consumed_at"])

        delete_latest_completed_session(user=self.user)
        self.assertFalse(AssessmentSession.objects.filter(id=session.id).exists())
        licence.refresh_from_db()
        self.assertEqual(licence.assigned_to_id, self.user.id)
        self.assertEqual(licence.status, LicenceStatus.ASSIGNED)
        self.assertIsNone(licence.consumed_at)


@override_settings(DEBUG=True, REPORT_LLM_PROVIDER="template")
class SimulateSurveyCompletionTests(TestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="Test Org")
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="pw",
            organisation=self.org,
            role=UserRole.RESPONDENT,
        )
        self.assessment = Assessment.objects.create(name="Test Assessment", version="1.0", is_active=True)
        self.licence = Licence.objects.create(
            organisation=self.org,
            assessment=self.assessment,
            assigned_to=self.user,
            status=LicenceStatus.ASSIGNED,
        )
        area = Area.objects.create(name="A")
        sub = SubArea.objects.create(area=area, name="S")
        domain = Domain.objects.create(name="Burnout Risk", threshold=3.0)
        self.questions = [
            Question.objects.create(
                assessment=self.assessment,
                area=area,
                subarea=sub,
                order=index + 1,
                text=f"Question {index + 1}",
            )
            for index in range(3)
        ]
        for question in self.questions:
            QuestionDomainWeight.objects.create(question=question, domain=domain, weight=1.0)

    def test_simulate_fills_all_questions_and_completes_session(self):
        session = simulate_survey_completion(user=self.user, raw_likert_score=4)
        self.assertEqual(session.status, SessionStatus.COMPLETED)
        self.assertEqual(Response.objects.filter(session=session).count(), 3)
        self.assertTrue(DomainScoreResult.objects.filter(session=session).exists())
        self.licence.refresh_from_db()
        self.assertEqual(self.licence.status, LicenceStatus.CONSUMED)

    def test_simulate_uses_random_scores_by_default(self):
        session = simulate_survey_completion(user=self.user)
        scores = list(
            Response.objects.filter(session=session).values_list("raw_likert_score", flat=True)
        )
        self.assertEqual(len(scores), 3)
        self.assertTrue(all(1 <= score <= 5 for score in scores))

    @override_settings(DEBUG=False)
    def test_simulate_rejected_when_debug_disabled(self):
        from apps.licensing.services import SessionError

        with self.assertRaises(SessionError):
            simulate_survey_completion(user=self.user)
