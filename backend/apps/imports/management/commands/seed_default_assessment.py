from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.imports.services import seed_assessment

DEFAULT_ASSESSMENT_NAME = "Subjective Alignment Assessment"
DEFAULT_ASSESSMENT_VERSION = "1.0"


class Command(BaseCommand):
    help = "Seed the default assessment from repo /data CSVs (idempotent)."

    def handle(self, *args, **options):
        data_dir = Path(settings.BASE_DIR).parent / "data"
        questions = data_dir / "sa-questions-likert.csv"
        thresholds = data_dir / "domain-thresholds.csv"
        rules = data_dir / "rules-bank.csv"

        missing = [p for p in (questions, thresholds, rules) if not p.is_file()]
        if missing:
            raise CommandError(
                "Missing seed CSV(s): "
                + ", ".join(str(p) for p in missing)
                + f" (expected under {data_dir})"
            )

        summary = seed_assessment(
            questions_csv=questions,
            thresholds_csv=thresholds,
            rules_csv=rules,
            assessment_name=DEFAULT_ASSESSMENT_NAME,
            assessment_version=DEFAULT_ASSESSMENT_VERSION,
        )

        self.stdout.write(self.style.SUCCESS("Default assessment seed complete."))
        self.stdout.write(
            f"Assessment: {DEFAULT_ASSESSMENT_NAME} ({DEFAULT_ASSESSMENT_VERSION})\n"
            f"Assessment created: {summary.assessment_created}\n"
            f"Domains created/updated: {summary.domains_created}/{summary.domains_updated}\n"
            f"Questions created/updated: {summary.questions_created}/{summary.questions_updated}\n"
            f"Weights created/updated: {summary.weights_created}/{summary.weights_updated}\n"
            f"Rules created/updated: {summary.rules_created}/{summary.rules_updated}\n"
        )
