"""SUBAL report and wheel constants (aligned with report template docs)."""

DOMAIN_ORDER = [
    "Burnout Risk",
    "Authenticity Strain",
    "Suppressed Influence",
    "Internal Contradiction",
    "Structural Misfit",
    "Old Wounds New Systems",
    "Emotional Containment",
    "Values Misalignment",
]

DOMAIN_SLUGS = {
    "Burnout Risk": "burnout_risk",
    "Authenticity Strain": "authenticity_strain",
    "Suppressed Influence": "suppressed_influence",
    "Internal Contradiction": "internal_contradiction",
    "Structural Misfit": "structural_misfit",
    "Old Wounds New Systems": "old_wounds_new_systems",
    "Emotional Containment": "emotional_containment",
    "Values Misalignment": "values_misalignment",
}

DOMAIN_COLORS = {
    "burnout_risk": "#0B4F71",
    "authenticity_strain": "#31B8C6",
    "suppressed_influence": "#6F3FA0",
    "internal_contradiction": "#D83A4B",
    "structural_misfit": "#F47C20",
    "old_wounds_new_systems": "#F2A51A",
    "emotional_containment": "#68B84E",
    "values_misalignment": "#28A98B",
}

DOMAIN_REFLECTIONS = {
    "Burnout Risk": "Demand versus available energy",
    "Authenticity Strain": "Pressure to adapt or perform",
    "Suppressed Influence": "Gap between insight and impact",
    "Internal Contradiction": "Competing internal drivers",
    "Structural Misfit": "Fit between person, role, and system",
    "Old Wounds New Systems": "Past experiences shaping present reactions",
    "Emotional Containment": "Capacity to hold and regulate pressure",
    "Values Misalignment": "Fit between work and personal meaning",
}

PRIMARY_THEMES = {
    "Burnout Risk": "Burnout Risk",
    "Authenticity Strain": "Adaptation Pressure",
    "Suppressed Influence": "Suppressed Contribution",
    "Internal Contradiction": "Internal Conflict",
    "Structural Misfit": "Role Misfit",
    "Old Wounds New Systems": "Past Experiences Influencing Present Systems",
    "Emotional Containment": "Adaptation Pressure",
    "Values Misalignment": "Values Conflict",
}

WELCOME_TEXT = (
    "This report shows how your work role, environment, goals, and personal style are "
    "currently interacting. It is not a personality test or diagnosis. It is designed "
    "to help you understand where things feel aligned, where friction exists, and what "
    "may need attention."
)

CLOSING_REFLECTION = (
    "Alignment is not fixed. It changes as your role, goals, environment, and life "
    "circumstances change. This report gives you a snapshot of your current professional "
    "system. Its purpose is to help you see the pattern more clearly, so that future "
    "decisions can be made with greater awareness."
)

SUGGESTED_NEXT_STEPS = [
    "Review the top 3 areas of strain.",
    "Identify which result feels most accurate.",
    "Identify which result feels uncomfortable or surprising.",
    "Consider whether the issue is mainly personal, relational, structural, or organisational.",
    "Decide what one small shift would improve alignment in the next month.",
]

FOCUS_AREA_TEMPLATES = {
    "Burnout Risk": {
        "title": "Restore Energy",
        "why": "Sustained demand without adequate recovery can gradually erode engagement and resilience.",
    },
    "Authenticity Strain": {
        "title": "Reduce Authenticity Strain",
        "why": "Ongoing adaptation to fit the environment can create distance between how you operate and how you feel expected to show up.",
    },
    "Suppressed Influence": {
        "title": "Increase Influence",
        "why": "When insight does not translate into impact, effort can feel unrewarded and motivation may decline.",
    },
    "Internal Contradiction": {
        "title": "Clarify Internal Priorities",
        "why": "Competing internal drivers can make decisions feel harder and reduce a sense of direction.",
    },
    "Structural Misfit": {
        "title": "Improve Role Fit",
        "why": "A mismatch between your natural way of working and the structure of the role can create persistent friction.",
    },
    "Old Wounds New Systems": {
        "title": "Recognise Historical Influences",
        "why": "Past experiences can shape present reactions in ways that are not always immediately visible.",
    },
    "Emotional Containment": {
        "title": "Create Space for Emotional Processing",
        "why": "Carrying pressure without adequate release can increase strain over time.",
    },
    "Values Misalignment": {
        "title": "Reconnect with What Matters",
        "why": "When daily work diverges from personal meaning, motivation and satisfaction can erode gradually.",
    },
}
