"""Generate and persist the full SUBAL assessment report."""

from __future__ import annotations

from django.db import transaction

from apps.licensing.models import AssessmentSession
from apps.results.constants import (
    CLOSING_REFLECTION,
    DOMAIN_ORDER,
    DOMAIN_REFLECTIONS,
    DOMAIN_SLUGS,
    SUGGESTED_NEXT_STEPS,
    WELCOME_TEXT,
)
from apps.results.focus_areas import build_section6_context
from apps.results.interpretation import build_snapshot_variables, normalize_domain_results
from apps.results.llm import (
    generate_focus_areas,
    generate_overall_snapshot,
    generate_what_results_suggest,
)
from apps.results.models import AssessmentReport, DomainScoreResult, TriggeredFlag
from apps.results.theme_extraction import build_section5_context


def _strain_explanation(domain_name: str, flags: list[TriggeredFlag]) -> str:
    for flag in flags:
        if domain_name.lower() in flag.flag.lower() or domain_name.lower() in flag.insight_snapshot.lower():
            return flag.insight_snapshot
    return DOMAIN_REFLECTIONS.get(domain_name, "An area worth reflecting on within your current system.")


def _build_top_strain_areas(
    normalized: dict[str, dict],
    flags: list[TriggeredFlag],
) -> list[dict]:
    tops = sorted(
        normalized.items(),
        key=lambda item: item[1]["normalized_score"],
        reverse=True,
    )[:3]

    areas = []
    for rank, (name, data) in enumerate(tops, start=1):
        areas.append(
            {
                "rank": rank,
                "domain": name,
                "level": data["level"],
                "normalized_score": data["normalized_score"],
                "what_this_means": _strain_explanation(name, flags),
            }
        )
    return areas


def _build_full_results_summary(normalized: dict[str, dict]) -> list[dict]:
    summary = []
    for name in DOMAIN_ORDER:
        data = _domain_data(normalized, name)
        summary.append(
            {
                "domain": name,
                "level": data["level"],
                "normalized_score": data["normalized_score"],
                "what_it_reflects": DOMAIN_REFLECTIONS[name],
            }
        )
    return summary


def _domain_data(normalized: dict[str, dict], name: str) -> dict:
    return normalized.get(
        name,
        {"normalized_score": 0.0, "level": "Low"},
    )


def _build_wheel_payload(normalized: dict[str, dict]) -> dict:
    scores = {}
    levels = {}
    for name in DOMAIN_ORDER:
        data = _domain_data(normalized, name)
        slug = DOMAIN_SLUGS[name]
        scores[slug] = data["normalized_score"]
        levels[slug] = data["level"]

    top_pressure_zones = sorted(
        [
            {
                "domain": name,
                "slug": DOMAIN_SLUGS[name],
                "score": _domain_data(normalized, name)["normalized_score"],
                "level": _domain_data(normalized, name)["level"],
            }
            for name in DOMAIN_ORDER
        ],
        key=lambda item: item["score"],
        reverse=True,
    )[:3]

    return {
        "scores": scores,
        "levels": levels,
        "top_pressure_zones": top_pressure_zones,
    }


@transaction.atomic
def generate_report(*, session: AssessmentSession) -> AssessmentReport:
    domain_results = list(
        DomainScoreResult.objects.filter(session=session).select_related("domain")
    )
    flags = list(TriggeredFlag.objects.filter(session=session).order_by("triggered_at"))
    normalized = normalize_domain_results(domain_results)
    snapshot_variables = build_snapshot_variables(normalized)
    section5_context = build_section5_context(
        session=session,
        normalized=normalized,
        interaction_theme=snapshot_variables["interaction_theme"],
    )

    section6_context = build_section6_context(
        session=session,
        normalized=normalized,
        interaction_theme=snapshot_variables["interaction_theme"],
        snapshot_variables=snapshot_variables,
    )

    main_pattern, snapshot_provider = generate_overall_snapshot(snapshot_variables)
    what_results_suggest, section5_provider = generate_what_results_suggest(section5_context)
    focus_areas_raw, section6_provider = generate_focus_areas(section6_context)
    llm_provider = next(
        (provider for provider in (snapshot_provider, section5_provider, section6_provider) if provider != "template"),
        "template",
    )

    recommended_focus_areas = [
        {
            "rank": index,
            "domain": area["theme"],
            "title": area["title"],
            "why_this_matters": area["why_this_matters"],
            "reflective_question": area["reflective_question"],
        }
        for index, area in enumerate(focus_areas_raw, start=1)
    ]

    payload = {
        "welcome": WELCOME_TEXT,
        "overall_snapshot": {
            "alignment_level": snapshot_variables["overall_alignment"],
            "system_state": snapshot_variables["overall_system_state"],
            "main_pattern": main_pattern,
            "variables": snapshot_variables,
        },
        "top_strain_areas": _build_top_strain_areas(normalized, flags),
        "full_results_summary": _build_full_results_summary(normalized),
        "what_results_suggest": what_results_suggest,
        "recommended_focus_areas": recommended_focus_areas,
        "suggested_next_steps": SUGGESTED_NEXT_STEPS,
        "closing_reflection": CLOSING_REFLECTION,
        "wheel": _build_wheel_payload(normalized),
        "section5_context": section5_context,
        "section6_context": section6_context,
        "llm_provider": llm_provider,
        "llm_used": llm_provider != "template",
    }

    report, _ = AssessmentReport.objects.update_or_create(
        session=session,
        defaults={"content": payload},
    )
    return report
