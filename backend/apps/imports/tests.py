from django.test import TestCase

from apps.assessments.models import Domain, Question
from apps.imports.services import normalize_domain_name, parse_weight, seed_assessment
from apps.rules.models import Rule


class ImportServiceTests(TestCase):
    def test_normalize_domain_name_removes_commas_and_whitespace(self):
        self.assertEqual(
            normalize_domain_name(" Old Wounds,  New Systems "),
            "Old Wounds New Systems",
        )

    def test_parse_weight_handles_blanks(self):
        self.assertEqual(parse_weight(None), 0.0)
        self.assertEqual(parse_weight(""), 0.0)
        self.assertEqual(parse_weight("   "), 0.0)
        self.assertEqual(parse_weight("0.6"), 0.6)

    def test_seed_assessment_is_idempotent(self):
        summary1 = seed_assessment(
            questions_csv=(self._seed_path("sa-questions-likert.csv")),
            thresholds_csv=(self._seed_path("domain-thresholds.csv")),
            rules_csv=(self._seed_path("rules-bank.csv")),
            assessment_name="Subjective Alignment Assessment",
            assessment_version="1.0",
        )
        summary2 = seed_assessment(
            questions_csv=(self._seed_path("sa-questions-likert.csv")),
            thresholds_csv=(self._seed_path("domain-thresholds.csv")),
            rules_csv=(self._seed_path("rules-bank.csv")),
            assessment_name="Subjective Alignment Assessment",
            assessment_version="1.0",
        )

        self.assertTrue(summary1.assessment_created)
        self.assertFalse(summary2.assessment_created)
        self.assertEqual(Domain.objects.count(), 8)
        self.assertEqual(Question.objects.count(), 132)
        self.assertEqual(Rule.objects.count(), 28)

    def _seed_path(self, name: str):
        from pathlib import Path

        return Path(__file__).resolve().parents[3] / "seed_data" / name
