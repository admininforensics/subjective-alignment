from pathlib import Path

from django.core.management.base import BaseCommand

from apps.imports.services import seed_assessment


class Command(BaseCommand):
    help = "Seed assessment data from CSV files (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--questions", required=True)
        parser.add_argument("--thresholds", required=True)
        parser.add_argument("--rules", required=True)
        parser.add_argument("--assessment-name", required=True)
        parser.add_argument("--assessment-version", required=True)

    def handle(self, *args, **options):
        summary = seed_assessment(
            questions_csv=Path(options["questions"]),
            thresholds_csv=Path(options["thresholds"]),
            rules_csv=Path(options["rules"]),
            assessment_name=options["assessment_name"],
            assessment_version=options["assessment_version"],
        )

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write(
            f"Assessment created: {summary.assessment_created}\n"
            f"Domains created/updated: {summary.domains_created}/{summary.domains_updated}\n"
            f"Questions created/updated: {summary.questions_created}/{summary.questions_updated}\n"
            f"Weights created/updated: {summary.weights_created}/{summary.weights_updated}\n"
            f"Rules created/updated: {summary.rules_created}/{summary.rules_updated}\n"
        )

