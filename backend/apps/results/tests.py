from django.test import TestCase

from apps.assessments.models import Assessment, Area, Domain, Question, QuestionDomainWeight, SubArea
from apps.licensing.models import AssessmentSession, Licence, LicenceStatus, SessionStatus
from apps.organisations.models import Organisation
from unittest.mock import patch

from apps.results.interpretation import build_snapshot_variables, get_level, normalize_score
from apps.results.llm import PROVIDER_OLLAMA, PROVIDER_TEMPLATE, generate_overall_snapshot
from apps.results.interaction_themes import resolve_interaction_theme
from apps.results.models import AssessmentReport, DomainScoreResult, Response
from apps.results.report_service import generate_report
from apps.results.theme_extraction import question_text_to_theme
from apps.accounts.models import User


class InterpretationTests(TestCase):
    def test_score_bands(self):
        self.assertEqual(get_level(20), "Low")
        self.assertEqual(get_level(55), "Moderate")
        self.assertEqual(get_level(80), "High")

    def test_normalize_score(self):
        self.assertEqual(normalize_score(182.5, 365), 50.0)

    def test_interaction_theme_pair(self):
        theme = resolve_interaction_theme("Burnout Risk", "Authenticity Strain")
        self.assertEqual(theme, "Sustained adaptation is creating energy costs")

    def test_snapshot_variables_include_required_fields(self):
        normalized = {
            "Burnout Risk": {"normalized_score": 72, "level": "High"},
            "Authenticity Strain": {"normalized_score": 68, "level": "Moderate"},
            "Suppressed Influence": {"normalized_score": 20, "level": "Low"},
            "Internal Contradiction": {"normalized_score": 30, "level": "Low"},
            "Structural Misfit": {"normalized_score": 55, "level": "Moderate"},
            "Old Wounds New Systems": {"normalized_score": 25, "level": "Low"},
            "Emotional Containment": {"normalized_score": 40, "level": "Moderate"},
            "Values Misalignment": {"normalized_score": 15, "level": "Low"},
        }
        variables = build_snapshot_variables(normalized)
        self.assertIn("overall_system_state", variables)
        self.assertIn("interaction_theme", variables)
        self.assertIn("tone", variables)
        self.assertEqual(variables["primary_domain"], "Burnout Risk")


class LlmProviderTests(TestCase):
    def test_ollama_provider_used_when_configured(self):
        variables = {
            "overall_system_state": "Emerging Strain",
            "primary_domain": "Burnout Risk",
            "secondary_domain": "Authenticity Strain",
            "interaction_theme": "Sustained adaptation is creating energy costs",
            "tone": "Reflective",
        }
        with patch.dict("os.environ", {"REPORT_LLM_PROVIDER": "ollama"}, clear=False):
            with patch(
                "apps.results.llm._call_ollama",
                return_value="Sentence one. Sentence two. Sentence three.",
            ):
                text, provider = generate_overall_snapshot(variables)
        self.assertEqual(provider, PROVIDER_OLLAMA)
        self.assertEqual(text, "Sentence one. Sentence two. Sentence three.")

    def test_template_fallback_when_ollama_unavailable(self):
        variables = {
            "overall_system_state": "Stable",
            "primary_domain": "Burnout Risk",
            "secondary_domain": None,
            "interaction_theme": "Role demands are exceeding available resources",
            "tone": "Reassuring",
        }
        with patch.dict("os.environ", {"REPORT_LLM_PROVIDER": "template"}, clear=False):
            _, provider = generate_overall_snapshot(variables)
        self.assertEqual(provider, PROVIDER_TEMPLATE)


class ThemeExtractionTests(TestCase):
    def test_question_text_to_theme(self):
        theme = question_text_to_theme("I feel pressure to present myself in a particular way.")
        self.assertIn("pressure to present myself", theme.lower())


class ReportServiceTests(TestCase):
    def test_generate_report_persists_all_sections(self):
        org = Organisation.objects.create(name="Org")
        respondent = User.objects.create_user(
            email="r@example.com",
            username="r",
            password="pw",
            organisation=org,
        )
        assessment = Assessment.objects.create(name="A", version="1.0", is_active=True)
        area = Area.objects.create(name="Context")
        sub = SubArea.objects.create(area=area, name="Culture")
        domain = Domain.objects.create(name="Burnout Risk", threshold=3.0)
        q = Question.objects.create(
            assessment=assessment,
            area=area,
            subarea=sub,
            text="I feel tense and overwhelmed at work.",
            order=1,
            reverse_logic=False,
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
            status=SessionStatus.COMPLETED,
        )
        Response.objects.create(session=session, question=q, raw_likert_score=5, effective_likert_score=5)
        DomainScoreResult.objects.create(
            session=session,
            domain=domain,
            score=5.0,
            threshold=3.0,
            triggered=True,
        )

        report = generate_report(session=session)
        self.assertIsInstance(report, AssessmentReport)
        self.assertIn("welcome", report.content)
        self.assertIn("overall_snapshot", report.content)
        self.assertIn("what_results_suggest", report.content)
        self.assertIn("wheel", report.content)
        self.assertEqual(len(report.content["top_strain_areas"]), 1)
