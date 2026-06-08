"""Extract interpretive themes from response patterns for Section 5."""

from __future__ import annotations

import re

from apps.licensing.models import AssessmentSession
from apps.results.models import Response


def question_text_to_theme(text: str) -> str:
    theme = text.strip().rstrip(".")
    theme = re.sub(r"^I\s+", "", theme, flags=re.IGNORECASE)
    theme = re.sub(r"^I'm\s+", "Feeling ", theme, flags=re.IGNORECASE)
    theme = re.sub(r"^I am\s+", "Being ", theme, flags=re.IGNORECASE)
    theme = re.sub(r"^I feel\s+", "Feeling ", theme, flags=re.IGNORECASE)
    theme = re.sub(r"^I have\s+", "Having ", theme, flags=re.IGNORECASE)
    theme = re.sub(r"^My\s+", "Personal ", theme, flags=re.IGNORECASE)
    if theme:
        theme = theme[0].upper() + theme[1:]
    if len(theme) > 72:
        theme = theme[:69].rstrip() + "..."
    return theme


def extract_domain_themes(session: AssessmentSession, domain_name: str, limit: int = 5) -> dict:
    contributions: list[dict] = []

    responses = (
        Response.objects.filter(session=session)
        .select_related("question", "question__subarea", "question__subarea__area")
        .prefetch_related("question__domain_weights__domain")
    )

    for response in responses:
        for mapping in response.question.domain_weights.all():
            if mapping.domain.name != domain_name or not mapping.weight:
                continue
            contribution = response.effective_likert_score * mapping.weight
            contributions.append(
                {
                    "contribution": contribution,
                    "subarea": response.question.subarea.name,
                    "area": response.question.area.name,
                    "theme": question_text_to_theme(response.question.text),
                    "effective_score": response.effective_likert_score,
                }
            )

    contributions.sort(key=lambda item: item["contribution"], reverse=True)
    top = contributions[:limit]

    subarea_totals: dict[str, float] = {}
    for item in contributions:
        subarea_totals[item["subarea"]] = subarea_totals.get(item["subarea"], 0.0) + item["contribution"]

    major_subdomains = [
        name
        for name, _ in sorted(subarea_totals.items(), key=lambda pair: pair[1], reverse=True)[:3]
    ]

    return {
        "domain": domain_name,
        "major_contributors": major_subdomains,
        "key_themes": [item["theme"] for item in top],
        "top_contributions": top,
    }


def build_section5_context(
    session: AssessmentSession,
    normalized: dict[str, dict],
    interaction_theme: str,
    elevated_limit: int = 2,
) -> dict:
    elevated = [
        name
        for name, data in sorted(
            normalized.items(),
            key=lambda item: item[1]["normalized_score"],
            reverse=True,
        )
        if data["level"] in {"Moderate", "High"}
    ][:elevated_limit]

    if not elevated:
        elevated = [name for name, _ in sorted(
            normalized.items(),
            key=lambda item: item[1]["normalized_score"],
            reverse=True,
        )[:1]]

    domain_contexts = [extract_domain_themes(session, name) for name in elevated]
    for ctx, name in zip(domain_contexts, elevated):
        ctx["level"] = normalized[name]["level"]

    return {
        "elevated_domains": domain_contexts,
        "interaction_themes": [interaction_theme],
    }
