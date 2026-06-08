"""Interpret raw domain scores into report variables."""

from __future__ import annotations

from apps.assessments.models import Domain, QuestionDomainWeight
from apps.results.constants import DOMAIN_ORDER, PRIMARY_THEMES
from apps.results.interaction_themes import resolve_interaction_theme
from apps.results.models import DomainScoreResult


def get_level(score: float) -> str:
    if score <= 39:
        return "Low"
    if score <= 69:
        return "Moderate"
    return "High"


def get_domain_max_scores() -> dict[str, float]:
    max_scores: dict[str, float] = {name: 0.0 for name in DOMAIN_ORDER}
    for mapping in QuestionDomainWeight.objects.filter(weight__gt=0).select_related("domain"):
        domain_name = mapping.domain.name
        if domain_name in max_scores:
            max_scores[domain_name] += 5 * mapping.weight
    return max_scores


def normalize_score(raw_score: float, max_score: float) -> float:
    if max_score <= 0:
        return 0.0
    return round(min(100.0, max(0.0, (raw_score / max_score) * 100)), 1)


def normalize_domain_results(
    domain_results: list[DomainScoreResult],
) -> dict[str, dict]:
    max_scores = get_domain_max_scores()
    normalized: dict[str, dict] = {}
    for result in domain_results:
        name = result.domain.name
        max_score = max_scores.get(name, 0.0)
        normalized_score = normalize_score(result.score, max_score)
        normalized[name] = {
            "raw_score": result.score,
            "threshold": result.threshold,
            "triggered": result.triggered,
            "max_score": max_score,
            "normalized_score": normalized_score,
            "level": get_level(normalized_score),
        }
    return normalized


def overall_alignment_level(normalized: dict[str, dict]) -> str:
    scores = [item["normalized_score"] for item in normalized.values()]
    high_count = sum(1 for item in normalized.values() if item["level"] == "High")
    avg = sum(scores) / len(scores) if scores else 0.0

    if high_count >= 3 or avg >= 70:
        return "Significant Misalignment"
    if high_count >= 2 or avg >= 55:
        return "Meaningful Strain"
    if high_count >= 1 or avg >= 40:
        return "Emerging Strain"
    return "Stable"


def alignment_level_label(system_state: str) -> str:
    mapping = {
        "Stable": "High",
        "Emerging Strain": "Moderate",
        "Meaningful Strain": "Low",
        "Significant Misalignment": "Low",
    }
    return mapping.get(system_state, "Moderate")


def emotional_tone(system_state: str) -> str:
    mapping = {
        "Stable": "Reassuring",
        "Emerging Strain": "Reflective",
        "Meaningful Strain": "Concerned",
        "Significant Misalignment": "Direct",
    }
    return mapping.get(system_state, "Reflective")


def top_domains(normalized: dict[str, dict], count: int = 3) -> list[str]:
    ordered = sorted(
        normalized.items(),
        key=lambda item: item[1]["normalized_score"],
        reverse=True,
    )
    return [name for name, _ in ordered[:count]]


def build_snapshot_variables(normalized: dict[str, dict]) -> dict:
    tops = top_domains(normalized, 3)
    primary = tops[0] if tops else DOMAIN_ORDER[0]
    secondary = tops[1] if len(tops) > 1 else None
    system_state = overall_alignment_level(normalized)

    return {
        "overall_system_state": system_state,
        "overall_alignment": alignment_level_label(system_state),
        "primary_domain": primary,
        "secondary_domain": secondary,
        "primary_theme": PRIMARY_THEMES.get(primary, primary),
        "top_flags": tops,
        "interaction_theme": resolve_interaction_theme(primary, secondary),
        "tone": emotional_tone(system_state),
    }
