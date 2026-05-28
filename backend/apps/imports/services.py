from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from django.db import transaction
from django.utils.text import slugify

from apps.assessments.models import (
    Area,
    Assessment,
    Domain,
    Question,
    QuestionDomainWeight,
    SubArea,
)
from apps.rules.models import Rule, RuleType


def normalize_domain_name(name: str) -> str:
    return " ".join(name.strip().replace(",", "").split())


def parse_weight(value) -> float:
    if value is None:
        return 0.0
    value = str(value).strip()
    if value == "":
        return 0.0
    return float(value)


@dataclass(frozen=True)
class SeedSummary:
    assessment_created: bool
    domains_created: int
    domains_updated: int
    questions_created: int
    questions_updated: int
    weights_created: int
    weights_updated: int
    rules_created: int
    rules_updated: int


@transaction.atomic
def seed_assessment(
    *,
    questions_csv: Path,
    thresholds_csv: Path,
    rules_csv: Path,
    assessment_name: str,
    assessment_version: str,
) -> SeedSummary:
    assessment, assessment_created = Assessment.objects.update_or_create(
        name=assessment_name,
        version=assessment_version,
        defaults={"is_active": True},
    )

    domains_by_name, d_created, d_updated = _import_domains_and_thresholds(thresholds_csv)
    q_created, q_updated, w_created, w_updated = _import_questions_and_weights(
        assessment=assessment,
        questions_csv=questions_csv,
        domains_by_name=domains_by_name,
    )
    r_created, r_updated = _import_rules(rules_csv=rules_csv, domains_by_name=domains_by_name)

    return SeedSummary(
        assessment_created=assessment_created,
        domains_created=d_created,
        domains_updated=d_updated,
        questions_created=q_created,
        questions_updated=q_updated,
        weights_created=w_created,
        weights_updated=w_updated,
        rules_created=r_created,
        rules_updated=r_updated,
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="mac_roman", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _import_domains_and_thresholds(thresholds_csv: Path) -> tuple[dict[str, Domain], int, int]:
    rows = _read_csv(thresholds_csv)
    created = 0
    updated = 0
    domains_by_name: dict[str, Domain] = {}

    for row in rows:
        raw_name = row.get("Domain", "") or ""
        threshold_raw = row.get("Threshold", "") or ""
        name = normalize_domain_name(raw_name)
        threshold = float(str(threshold_raw).strip())

        domain, was_created = Domain.objects.update_or_create(
            name=name,
            defaults={"threshold": threshold},
        )
        if was_created:
            created += 1
        else:
            updated += 1
        domains_by_name[name] = domain

    return domains_by_name, created, updated


def _import_questions_and_weights(
    *,
    assessment: Assessment,
    questions_csv: Path,
    domains_by_name: dict[str, Domain],
) -> tuple[int, int, int, int]:
    rows = _read_csv(questions_csv)
    created_q = 0
    updated_q = 0
    created_w = 0
    updated_w = 0

    if not rows:
        return 0, 0, 0, 0

    reserved_columns = {
        "Question",
        "Area",
        "SubArea",
        "Reverse Logic",
        "Individual",
        "Team",
    }

    domain_columns = [c for c in rows[0].keys() if c not in reserved_columns]

    for idx, row in enumerate(rows):
        area, _ = Area.objects.update_or_create(name=(row.get("Area", "") or "").strip())
        subarea, _ = SubArea.objects.update_or_create(
            area=area,
            name=(row.get("SubArea", "") or "").strip(),
        )

        question_text = (row.get("Question", "") or "").strip()
        reverse_logic = str(row.get("Reverse Logic", "0") or "0").strip() == "1"
        individual = str(row.get("Individual", "0") or "0").strip() == "1"
        team = str(row.get("Team", "0") or "0").strip() == "1"

        question, was_created = Question.objects.update_or_create(
            assessment=assessment,
            text=question_text,
            defaults={
                "area": area,
                "subarea": subarea,
                "order": idx + 1,
                "reverse_logic": reverse_logic,
                "individual": individual,
                "team": team,
            },
        )
        if was_created:
            created_q += 1
        else:
            updated_q += 1

        for domain_col in domain_columns:
            domain_name = normalize_domain_name(domain_col)
            domain = domains_by_name.get(domain_name)
            if not domain:
                continue

            weight = parse_weight(row.get(domain_col))
            mapping, mapping_created = QuestionDomainWeight.objects.update_or_create(
                question=question,
                domain=domain,
                defaults={"weight": weight},
            )
            if mapping_created:
                created_w += 1
            else:
                updated_w += 1
            _ = mapping

    return created_q, updated_q, created_w, updated_w


def _import_rules(*, rules_csv: Path, domains_by_name: dict[str, Domain]) -> tuple[int, int]:
    rows = _read_csv(rules_csv)
    created = 0
    updated = 0

    for row in rows:
        domain_a_name = normalize_domain_name((row.get("Domain A", "") or "").strip())
        domain_b_name = normalize_domain_name((row.get("Domain B", "") or "").strip())

        domain_a = domains_by_name.get(domain_a_name)
        domain_b = domains_by_name.get(domain_b_name)
        if not domain_a or not domain_b:
            raise ValueError(f"Rule references unknown domains: '{domain_a_name}', '{domain_b_name}'")

        rule_text = (row.get("Rule", "") or "").strip()
        flag = (row.get("Flag", "") or "").strip()
        insight = (row.get("Insight", "") or "").strip()

        code = slugify(f"{domain_a.name}-{domain_b.name}-{flag}")[:150]
        _, was_created = Rule.objects.update_or_create(
            code=code,
            defaults={
                "domain_a": domain_a,
                "domain_b": domain_b,
                "description": rule_text,
                "flag": flag,
                "insight": insight,
                "rule_type": RuleType.PAIRWISE_AND,
                "is_active": True,
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return created, updated

