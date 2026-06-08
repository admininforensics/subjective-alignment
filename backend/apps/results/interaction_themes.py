"""Interaction theme library — maps domain patterns to interpretive themes."""

from __future__ import annotations

# Keyed by sorted tuple of the two most elevated domains.
PAIR_THEMES: dict[tuple[str, str], str] = {
    ("Authenticity Strain", "Burnout Risk"): (
        "Sustained adaptation is creating energy costs"
    ),
    ("Burnout Risk", "Structural Misfit"): (
        "The demands of the role may not align with how you naturally operate"
    ),
    ("Authenticity Strain", "Structural Misfit"): (
        "Ongoing adaptation to fit the environment is creating role friction"
    ),
    ("Burnout Risk", "Suppressed Influence"): (
        "Effort is being expended without a corresponding sense of influence or impact"
    ),
    ("Authenticity Strain", "Suppressed Influence"): (
        "Insight is not translating into influence while authenticity feels constrained"
    ),
    ("Burnout Risk", "Values Misalignment"): (
        "Meaning and role requirements are diverging, increasing the personal cost of work"
    ),
    ("Authenticity Strain", "Values Misalignment"): (
        "Success may require presenting yourself in ways that conflict with personal values"
    ),
    ("Burnout Risk", "Emotional Containment"): (
        "Pressure is being carried internally without adequate release or recovery"
    ),
    ("Burnout Risk", "Internal Contradiction"): (
        "Competing priorities are reducing clarity while demand remains high"
    ),
    ("Burnout Risk", "Old Wounds New Systems"): (
        "Past experiences may be amplifying the cost of current pressures"
    ),
    ("Authenticity Strain", "Emotional Containment"): (
        "Authentic expression may feel constrained, increasing internal tension"
    ),
    ("Authenticity Strain", "Internal Contradiction"): (
        "There may be a gap between who you are and how you feel required to show up"
    ),
    ("Authenticity Strain", "Old Wounds New Systems"): (
        "Past experiences may be influencing how safe it feels to show up authentically"
    ),
    ("Internal Contradiction", "Structural Misfit"): (
        "Competing internal drivers may be intensified by structural constraints"
    ),
    ("Structural Misfit", "Suppressed Influence"): (
        "The structure of the role may limit your ability to shape outcomes"
    ),
    ("Emotional Containment", "Structural Misfit"): (
        "The environment may require containment of feelings that would otherwise signal misalignment"
    ),
    ("Old Wounds New Systems", "Structural Misfit"): (
        "Current structures may be reactivating patterns from earlier professional experiences"
    ),
    ("Internal Contradiction", "Values Misalignment"): (
        "Competing priorities may reflect deeper uncertainty about what matters most"
    ),
    ("Suppressed Influence", "Values Misalignment"): (
        "Limited influence may make it harder to align the system with what you value"
    ),
    ("Emotional Containment", "Old Wounds New Systems"): (
        "Unresolved relational history may be shaping how pressure is held and expressed"
    ),
    ("Emotional Containment", "Values Misalignment"): (
        "Holding back emotionally may be masking a deeper values tension"
    ),
    ("Internal Contradiction", "Old Wounds New Systems"): (
        "Past experiences may be contributing to competing internal drivers"
    ),
    ("Internal Contradiction", "Suppressed Influence"): (
        "Internal hesitation may be limiting the expression of insight and influence"
    ),
    ("Old Wounds New Systems", "Suppressed Influence"): (
        "Past experiences may be influencing how safe it feels to assert influence"
    ),
    ("Old Wounds New Systems", "Values Misalignment"): (
        "Earlier experiences may be shaping what feels meaningful or acceptable now"
    ),
    ("Emotional Containment", "Suppressed Influence"): (
        "Emotional restraint may be limiting the expression of insight and impact"
    ),
}

DOMAIN_FALLBACK_THEMES: dict[str, str] = {
    "Burnout Risk": "Role demands are exceeding available resources",
    "Authenticity Strain": "Sustained adaptation is creating energy costs",
    "Suppressed Influence": "Insight is not translating into influence",
    "Internal Contradiction": "Competing priorities are reducing clarity",
    "Structural Misfit": "The demands of the role may not align with how you naturally operate",
    "Old Wounds New Systems": "Past experiences are influencing present professional reactions",
    "Emotional Containment": "Pressure is being carried internally without adequate release",
    "Values Misalignment": "Meaning and role requirements are diverging",
}


def resolve_interaction_theme(primary_domain: str, secondary_domain: str | None) -> str:
    if secondary_domain:
        key = tuple(sorted([primary_domain, secondary_domain]))
        if key in PAIR_THEMES:
            return PAIR_THEMES[key]
    return DOMAIN_FALLBACK_THEMES.get(
        primary_domain,
        "Several areas of strain are interacting within your current professional system",
    )
