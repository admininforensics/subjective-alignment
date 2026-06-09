from django.test import TestCase

from apps.assessments.models import Assessment, Area, Domain, Question, QuestionDomainWeight, SubArea
from apps.licensing.models import AssessmentSession, Licence, LicenceStatus, SessionStatus
from apps.organisations.models import Organisation
from unittest.mock import patch

from apps.results.focus_areas import (
    build_section6_context,
    detect_driver,
    focus_area_count,
    resolve_focus_title,
)
from apps.results.interpretation import build_snapshot_variables, get_level, normalize_score
from apps.results.llm import PROVIDER_OLLAMA, PROVIDER_TEMPLATE, generate_focus_areas, generate_overall_snapshot
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


class FocusAreaTests(TestCase):
    def test_focus_area_count_by_system_state(self):
        normalized = {name: {"level": "Low", "normalized_score": 20} for name in [
            "Burnout Risk", "Authenticity Strain", "Suppressed Influence", "Internal Contradiction",
            "Structural Misfit", "Old Wounds New Systems", "Emotional Containment", "Values Misalignment",
        ]}
        self.assertEqual(focus_area_count("Stable", normalized), 1)

        normalized["Burnout Risk"]["level"] = "High"
        self.assertEqual(focus_area_count("Significant Misalignment", normalized), 4)

    def test_burnout_adaptation_driver_selects_adaptation_title(self):
        context = {
            "major_contributors": ["Culture"],
            "key_themes": ["Feeling pressure to present myself in a particular way"],
        }
        title = resolve_focus_title(
            "Burnout Risk",
            context,
            interaction_theme="Sustained adaptation is creating energy costs",
            secondary_domain="Authenticity Strain",
        )
        self.assertEqual(title, "Reducing the Cost of Adaptation")

    def test_template_focus_areas_include_reflective_question(self):
        section6_context = {
            "candidates": [
                {
                    "title": "Protecting Energy and Recovery",
                    "theme": "Burnout Risk",
                    "contributing_themes": ["Feeling tense and overwhelmed"],
                    "major_contributors": ["Context"],
                    "interaction_theme": "Role demands are exceeding available resources",
                    "driver": "recovery",
                }
            ]
        }
        with patch.dict("os.environ", {"REPORT_LLM_PROVIDER": "template"}, clear=False):
            areas, provider = generate_focus_areas(section6_context)
        self.assertEqual(provider, PROVIDER_TEMPLATE)
        self.assertIn("reflective_question", areas[0])
        self.assertIn("why_this_matters", areas[0])


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
        self.assertTrue(report.content["recommended_focus_areas"])
        self.assertIn("reflective_question", report.content["recommended_focus_areas"][0])
