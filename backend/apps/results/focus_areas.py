"""Section 6 focus area selection — reflection layer, not advice."""

from __future__ import annotations

from apps.licensing.models import AssessmentSession
from apps.results.interpretation import overall_alignment_level
from apps.results.theme_extraction import extract_domain_themes

DRIVER_KEYWORDS: dict[str, tuple[str, ...]] = {
    "recovery": (
        "overwhelm",
        "tense",
        "energy",
        "recovery",
        "rest",
        "tired",
        "exhaust",
        "demand",
        "resilience",
        "fatigue",
        "workload",
    ),
    "adaptation": (
        "adapt",
        "present",
        "conform",
        "authentic",
        "culture",
        "express",
        "disagree",
        "acceptance",
        "visibility",
        "perform",
    ),
    "fit": (
        "fit",
        "structure",
        "role",
        "pace",
        "rhythm",
        "working style",
        "misfit",
        "environment",
    ),
    "influence": (
        "influence",
        "heard",
        "impact",
        "voice",
        "authority",
        "shape",
        "contribute",
    ),
    "values": (
        "values",
        "meaning",
        "purpose",
        "matter",
        "principle",
    ),
    "internal": (
        "conflict",
        "competing",
        "priority",
        "contradict",
        "uncertain",
    ),
    "historical": (
        "past",
        "history",
        "wound",
        "earlier",
        "previous",
        "experience",
    ),
    "containment": (
        "contain",
        "suppress",
        "hold",
        "emotion",
        "pressure",
        "release",
    ),
}

FOCUS_TITLES: dict[tuple[str, str], str] = {
    ("Burnout Risk", "recovery"): "Protecting Energy and Recovery",
    ("Burnout Risk", "adaptation"): "Reducing the Cost of Adaptation",
    ("Burnout Risk", "fit"): "Restoring Capacity",
    ("Authenticity Strain", "adaptation"): "Reducing the Cost of Adaptation",
    ("Authenticity Strain", "fit"): "Evaluating Environmental Fit",
    ("Suppressed Influence", "influence"): "Increasing Influence and Impact",
    ("Internal Contradiction", "internal"): "Clarifying Internal Priorities",
    ("Structural Misfit", "fit"): "Evaluating Environmental Fit",
    ("Old Wounds New Systems", "historical"): "Recognising Historical Influences",
    ("Emotional Containment", "containment"): "Creating Space for Emotional Processing",
    ("Values Misalignment", "values"): "Reconnecting with What Matters",
}

DEFAULT_FOCUS_TITLES: dict[str, str] = {
    "Burnout Risk": "Protecting Energy and Recovery",
    "Authenticity Strain": "Reducing the Cost of Adaptation",
    "Suppressed Influence": "Increasing Influence and Impact",
    "Internal Contradiction": "Clarifying Internal Priorities",
    "Structural Misfit": "Evaluating Environmental Fit",
    "Old Wounds New Systems": "Recognising Historical Influences",
    "Emotional Containment": "Creating Space for Emotional Processing",
    "Values Misalignment": "Reconnecting with What Matters",
}

FOCUS_TEMPLATES: dict[str, dict[str, str]] = {
    "Reducing the Cost of Adaptation": {
        "why_this_matters": (
            "Your results suggest that maintaining alignment with your environment may require "
            "ongoing adjustment in how you present, communicate, or work. While this can be "
            "effective, it may also contribute to fatigue if sustained over long periods."
        ),
        "reflective_question": (
            "Where do you feel most able to operate naturally, and where do you feel most "
            "required to adapt?"
        ),
    },
    "Protecting Energy and Recovery": {
        "why_this_matters": (
            "The profile suggests that demands may be accumulating more quickly than "
            "opportunities for recovery."
        ),
        "reflective_question": (
            "What activities, relationships, or environments consistently restore energy, "
            "and how available are they within your current routine?"
        ),
    },
    "Restoring Capacity": {
        "why_this_matters": (
            "Your results suggest that current demands may be outpacing opportunities for "
            "recovery. Reflecting on how energy is restored, protected, and allocated may help "
            "clarify where strain is accumulating."
        ),
        "reflective_question": (
            "Where is your energy being spent most heavily, and what would need to change for "
            "recovery to feel more possible?"
        ),
    },
    "Evaluating Environmental Fit": {
        "why_this_matters": (
            "The assessment suggests that some of the strain may arise from the relationship "
            "between you and the system, rather than from any lack of capability or motivation."
        ),
        "reflective_question": (
            "If the environment changed but you remained the same, which of your current "
            "challenges would likely disappear?"
        ),
    },
    "Increasing Influence and Impact": {
        "why_this_matters": (
            "Your results point toward a gap between what you see and what you are able to "
            "shape. When insight does not translate into influence, effort can feel less "
            "rewarding over time."
        ),
        "reflective_question": (
            "Where do you have ideas or perspective that feel difficult to bring into the "
            "conversation or decision?"
        ),
    },
    "Clarifying Internal Priorities": {
        "why_this_matters": (
            "Competing internal drivers may be making it harder to move with clarity. "
            "Attention to where priorities pull in different directions can help reveal what "
            "feels most unresolved."
        ),
        "reflective_question": (
            "When you imagine making a difficult choice at work, what values or commitments "
            "feel most in tension with one another?"
        ),
    },
    "Recognising Historical Influences": {
        "why_this_matters": (
            "Past professional experiences can shape present reactions in ways that are not "
            "always immediately visible. Recognising these patterns may help explain responses "
            "that feel disproportionate or persistent."
        ),
        "reflective_question": (
            "Are there earlier experiences that seem to echo in your current environment, and "
            "how do they affect how safe or workable it feels?"
        ),
    },
    "Creating Space for Emotional Processing": {
        "why_this_matters": (
            "Carrying pressure without adequate release can increase strain over time. "
            "Understanding where emotions are held back may clarify an additional source of "
            "cost within the system."
        ),
        "reflective_question": (
            "Where do you notice yourself containing feelings that might otherwise signal "
            "misalignment or need?"
        ),
    },
    "Reconnecting with What Matters": {
        "why_this_matters": (
            "When daily work diverges from personal meaning, motivation and satisfaction can "
            "erode gradually. Reflecting on what matters most can help clarify whether strain "
            "is partly values-related."
        ),
        "reflective_question": (
            "Which aspects of your work currently feel most aligned with what matters to you, "
            "and which feel furthest from it?"
        ),
    },
    "Maintaining Alignment": {
        "why_this_matters": (
            "Although strain is limited, small areas of pressure can still warrant attention "
            "before they accumulate. Reflection now may help preserve the balance your results "
            "suggest is largely present."
        ),
        "reflective_question": (
            "Which small frictions in your current system feel worth noticing before they grow?"
        ),
    },
}


def focus_area_count(system_state: str, normalized: dict[str, dict]) -> int:
    high_count = sum(1 for item in normalized.values() if item["level"] == "High")
    moderate_count = sum(1 for item in normalized.values() if item["level"] == "Moderate")

    if system_state == "Stable":
        return 2 if moderate_count >= 1 else 1
    if system_state == "Emerging Strain":
        return 3 if high_count >= 1 or moderate_count >= 2 else 2
    if system_state == "Meaningful Strain":
        return 4 if high_count >= 2 else 3
    return 4


def _text_blob(domain_context: dict) -> str:
    parts = list(domain_context.get("major_contributors", []))
    parts.extend(domain_context.get("key_themes", []))
    return " ".join(parts).lower()


def detect_driver(domain: str, domain_context: dict) -> str:
    blob = _text_blob(domain_context)

    domain_driver_priority: dict[str, tuple[str, ...]] = {
        "Burnout Risk": ("recovery", "adaptation", "fit"),
        "Authenticity Strain": ("adaptation", "fit"),
        "Suppressed Influence": ("influence",),
        "Internal Contradiction": ("internal",),
        "Structural Misfit": ("fit", "adaptation"),
        "Old Wounds New Systems": ("historical",),
        "Emotional Containment": ("containment", "adaptation"),
        "Values Misalignment": ("values", "adaptation"),
    }

    for driver in domain_driver_priority.get(domain, ("fit",)):
        if any(keyword in blob for keyword in DRIVER_KEYWORDS.get(driver, ())):
            return driver
    return domain_driver_priority.get(domain, ("fit",))[0]


def resolve_focus_title(
    domain: str,
    domain_context: dict,
    *,
    interaction_theme: str,
    secondary_domain: str | None,
) -> str:
    driver = detect_driver(domain, domain_context)

    if domain == "Burnout Risk" and secondary_domain == "Authenticity Strain":
        return "Reducing the Cost of Adaptation"
    if "adaptation" in interaction_theme.lower() and domain in {
        "Burnout Risk",
        "Authenticity Strain",
        "Emotional Containment",
    }:
        return "Reducing the Cost of Adaptation"
    if domain == "Structural Misfit" or (
        secondary_domain == "Structural Misfit" and driver == "fit"
    ):
        return "Evaluating Environmental Fit"

    return FOCUS_TITLES.get((domain, driver), DEFAULT_FOCUS_TITLES[domain])


def build_section6_context(
    *,
    session: AssessmentSession,
    normalized: dict[str, dict],
    interaction_theme: str,
    snapshot_variables: dict,
) -> dict:
    system_state = snapshot_variables["overall_system_state"]
    count = focus_area_count(system_state, normalized)
    secondary_domain = snapshot_variables.get("secondary_domain")

    ranked_domains = [
        name
        for name, _ in sorted(
            normalized.items(),
            key=lambda item: item[1]["normalized_score"],
            reverse=True,
        )
    ]

    elevated = [name for name in ranked_domains if normalized[name]["level"] in {"Moderate", "High"}]
    candidate_domains = elevated if elevated else ranked_domains[:2]

    candidates: list[dict] = []
    seen_titles: set[str] = set()

    for domain in candidate_domains:
        domain_context = extract_domain_themes(session, domain)
        domain_context["level"] = normalized[domain]["level"]
        title = resolve_focus_title(
            domain,
            domain_context,
            interaction_theme=interaction_theme,
            secondary_domain=secondary_domain,
        )
        if title in seen_titles:
            continue
        seen_titles.add(title)
        candidates.append(
            {
                "title": title,
                "theme": domain,
                "contributing_themes": domain_context.get("key_themes", [])[:3],
                "major_contributors": domain_context.get("major_contributors", [])[:3],
                "interaction_theme": interaction_theme,
                "driver": detect_driver(domain, domain_context),
            }
        )
        if len(candidates) >= count:
            break

    if not candidates:
        candidates.append(
            {
                "title": "Maintaining Alignment",
                "theme": ranked_domains[0],
                "contributing_themes": [],
                "major_contributors": [],
                "interaction_theme": interaction_theme,
                "driver": "fit",
            }
        )

    while len(candidates) < count and len(candidates) < len(ranked_domains):
        for domain in ranked_domains:
            if any(item["theme"] == domain for item in candidates):
                continue
            domain_context = extract_domain_themes(session, domain)
            title = resolve_focus_title(
                domain,
                domain_context,
                interaction_theme=interaction_theme,
                secondary_domain=secondary_domain,
            )
            if title in seen_titles:
                continue
            seen_titles.add(title)
            candidates.append(
                {
                    "title": title,
                    "theme": domain,
                    "contributing_themes": domain_context.get("key_themes", [])[:3],
                    "major_contributors": domain_context.get("major_contributors", [])[:3],
                    "interaction_theme": interaction_theme,
                    "driver": detect_driver(domain, domain_context),
                }
            )
            break
        else:
            break

    return {
        "system_state": system_state,
        "focus_area_count": len(candidates),
        "interaction_theme": interaction_theme,
        "candidates": candidates[:count],
    }
