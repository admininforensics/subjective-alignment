# Rule Engine Specification

The current rule engine is pairwise and threshold-based.

A rule has:

- Domain A
- Domain B
- Rule description
- Flag
- Insight

A rule triggers if and only if both domains are triggered.

```python
if domain_a.triggered and domain_b.triggered:
    trigger_rule(rule)
```

## Current Rules

| Domain A                | Domain B               | Rule                                                | Flag                       | Insight                                                                                                                |
|:------------------------|:-----------------------|:----------------------------------------------------|:---------------------------|:-----------------------------------------------------------------------------------------------------------------------|
| Burnout Risk            | Authenticity Strain    | High burnout + high authenticity strain             | Energy Leak                | You may be draining energy by constantly presenting a version of yourself that doesn't feel natural.                   |
| Burnout Risk            | Suppressed Influence   | Burnout high + low perceived influence              | Suppressed Drive           | You're expending effort without feeling heard or able to shape outcomes—this creates exhaustion without traction.      |
| Burnout Risk            | Internal Contradiction | Burnout high + internal misalignment                | System Overload            | You’re operating under high strain while also being pulled in contradictory internal directions.                       |
| Burnout Risk            | Structural Misfit      | Burnout high + role misfit                          | Incompatible Load          | Your current structure may not be built to support your working style—leading to unsustainable strain.                 |
| Burnout Risk            | Old Wounds New Systems | Burnout high + unresolved relational history        | Fragile Recovery           | Old relational injuries may be resurfacing under current pressures—making recovery difficult.                          |
| Burnout Risk            | Emotional Containment  | Burnout high + emotional suppression                | Silent Exhaustion          | You’re carrying hidden pressure without emotional release—risking quiet collapse.                                      |
| Burnout Risk            | Values Misalignment    | Burnout high + low alignment with values            | Meaning Erosion            | You’re working hard in a system that doesn’t reflect what matters to you—this corrodes energy over time.               |
| Authenticity Strain     | Suppressed Influence   | High authenticity strain + low influence            | Muffled Identity           | You may be censoring yourself to fit in while also lacking the power to speak up—creating identity fatigue.            |
| Authenticity Strain     | Internal Contradiction | High authenticity strain + internal misalignment    | Fragmented Self            | There may be a deep gap between who you are, how you show up, and how you're structured to operate.                    |
| Authenticity Strain     | Structural Misfit      | High authenticity strain + structural role mismatch | Role Conflict              | You’re contorting yourself to fit a structure that doesn’t suit your wiring—leading to quiet dissonance.               |
| Authenticity Strain     | Old Wounds New Systems | Authenticity strain + unresolved authority wounds   | Identity Residue           | Past injury may be influencing how safe it feels to show up authentically now.                                         |
| Authenticity Strain     | Emotional Containment  | High authenticity strain + high containment         | Emotional Lockdown         | You may be suppressing authentic feelings to meet relational or cultural expectations—creating internal tension.       |
| Authenticity Strain     | Values Misalignment    | Authenticity strain + values conflict               | Dissonant Performance      | You’re performing well, but not in a way that reflects who you are or what matters to you.                             |
| Suppressed Influence    | Internal Contradiction | Desire to influence + internal hesitation           | Friction at the Edge       | You may want to step forward but be holding yourself back due to conflicting internal beliefs or fears.                |
| Suppressed Influence    | Structural Misfit      | Low influence + rigid structure                     | Blocked Access             | Your desire to shape or lead may be stifled by a system that resists your natural way of working.                      |
| Suppressed Influence    | Old Wounds New Systems | Low influence + past authority wounds               | Silenced Potential         | You may carry a vision that goes unheard—not only because of the system, but because of unhealed relational injuries.  |
| Suppressed Influence    | Emotional Containment  | Low influence + high containment                    | Muted Impact               | You may be holding back your influence to avoid emotional risk—leading to under-recognition.                           |
| Suppressed Influence    | Values Misalignment    | Low influence + values misfit                       | Compromised Contribution   | You want to shape outcomes, but the system doesn’t value the same things—muting your potential.                        |
| Internal Contradiction  | Structural Misfit      | Internal friction + structure misfit                | Systemic Conflict          | You’re caught between inner contradictions and a rigid external structure—leading to cognitive dissonance.             |
| Internal Contradiction  | Old Wounds New Systems | Internal conflict + past relational wounds          | Residual Tension           | Unresolved emotional dynamics may be amplifying your internal confusion or split priorities.                           |
| Internal Contradiction  | Emotional Containment  | Contradiction + containment                         | Emotional Disorientation   | You may be holding tension without clarity or release—making it hard to find internal coherence.                       |
| Internal Contradiction  | Values Misalignment    | Contradiction + value conflict                      | Fragmented Drive           | What you’re doing may not align with what you believe—creating a split in purpose or energy.                           |
| Structural Misfit       | Old Wounds New Systems | Structural tension + relational injury              | Environmental Reactivation | Your current environment may be triggering old themes of exclusion or marginalisation.                                 |
| Structural Misfit       | Emotional Containment  | Misfit + emotional suppression                      | Frozen in Place            | You know the structure doesn’t fit, but it doesn’t feel safe to push back—so you remain stuck.                         |
| Structural Misfit       | Values Misalignment    | Misfit + values gap                                 | Systemic Incongruence      | Your structure and values don’t match—so effort feels unmoored from meaning.                                           |
| Old Wounds, New Systems | Emotional Containment  | Relational injury + high containment                | Residual Guarding          | You may be emotionally armoured due to past hurts—creating a barrier even in safe systems.                             |
| Old Wounds, New Systems | Values Misalignment    | Old betrayal + current misalignment                 | Cynical Drift              | You’ve been let down before, and now you’re operating in a system that doesn’t reflect your deeper values.             |
| Emotional Containment   | Values Misalignment    | High containment + values gap                       | Quiet Disengagement        | You’re holding back emotion while also working on something that feels meaningless—this can lead to silent withdrawal. |

## Recommended Implementation

The current implementation should use a pairwise rule model because the CSV rule bank is pairwise.

However, design the service layer so that a future advanced rule engine can be added without rewriting the rest of the app.

Recommended approach:

- Store current rules in a simple `Rule` table.
- Implement evaluation in `rules/services.py`.
- Keep the public scoring output independent of the rule implementation.
- Add a `rule_type` field defaulting to `PAIRWISE_AND`.

## Future-Proofing

Suggested enum:

```python
class RuleType(models.TextChoices):
    PAIRWISE_AND = "PAIRWISE_AND"
    ADVANCED_EXPRESSION = "ADVANCED_EXPRESSION"
```

For now, only implement `PAIRWISE_AND`.

Do not implement dynamic expression evaluation in the MVP.
