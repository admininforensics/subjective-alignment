# Seed Data Specification

The seed data lives in `/seed_data`.

## Files

```text
seed_data/
├── sa-questions-likert.csv
├── domain-thresholds.csv
└── rules-bank.csv
```

## Encoding

Read all files using:

```python
encoding = "mac_roman"
```

This is important for smart quotes and long dashes in the insights.

## `sa-questions-likert.csv`

Contains 132 questions.

Columns:

| Column | Purpose |
|---|---|
| Question | Question text shown to respondent |
| Area | High-level grouping |
| SubArea | Lower-level grouping |
| Burnout Risk | Domain weight |
| Authenticity Strain | Domain weight |
| Suppressed Influence | Domain weight |
| Internal Contradiction | Domain weight |
| Structural Misfit | Domain weight |
| Old Wounds New Systems | Domain weight |
| Emotional Containment | Domain weight |
| Values Misalignment | Domain weight |
| Reverse Logic | 0 = normal Likert, 1 = reversed Likert |
| Individual | 1 if applicable to individual context |
| Team | 1 if applicable to team context |

## Area/SubArea Distribution

| Area          | SubArea                  |   Question Count |
|:--------------|:-------------------------|-----------------:|
| Circumstances | Collegial Relationships  |                6 |
| Circumstances | Internal Problems        |                6 |
| Circumstances | Organisation Performance |                6 |
| Circumstances | Organisation Position    |                6 |
| Context       | Cultural                 |                6 |
| Context       | Economic                 |                6 |
| Context       | Family                   |                6 |
| Context       | Health                   |                6 |
| Context       | Political                |                6 |
| Goals         | Freedom                  |                6 |
| Goals         | Legacy                   |                6 |
| Goals         | Opposition               |                6 |
| Goals         | Personal                 |                6 |
| Position      | Exposure                 |                6 |
| Position      | Hierarchy                |                6 |
| Position      | KPIs                     |                6 |
| Position      | Relationships            |                6 |
| Subjectivity  | Injuries                 |                6 |
| Subjectivity  | Motivation               |                6 |
| Subjectivity  | Pain Management          |                6 |
| Subjectivity  | Personality              |                6 |
| Subjectivity  | Unconscious              |                6 |

## Sample Questions

| Question                                                                                                                  | Area    | SubArea   |   Burnout Risk |   Authenticity Strain |   Suppressed Influence |   Internal Contradiction |   Structural Misfit |   Old Wounds New Systems |   Emotional Containment |   Values Misalignment |   Reverse Logic |   Individual |   Team |
|:--------------------------------------------------------------------------------------------------------------------------|:--------|:----------|---------------:|----------------------:|-----------------------:|-------------------------:|--------------------:|-------------------------:|------------------------:|----------------------:|----------------:|-------------:|-------:|
| I am financially dependent on my job.                                                                                     | Context | Economic  |            0   |                   0.6 |                    0   |                      0   |                 0   |                      0   |                     0   |                   0.8 |               0 |            0 |      0 |
| My financial planning extends long term (years rather than months).                                                       | Context | Economic  |            0   |                   0.4 |                    0   |                      0   |                 0   |                      0   |                     0   |                   0   |               0 |            0 |      0 |
| I would be significantly impacted by a 20–30% drop in income.                                                             | Context | Economic  |            0   |                   0.2 |                    0   |                      0   |                 0   |                      0   |                     0   |                   0   |               0 |            0 |      0 |
| I feel financially secure in my current role.                                                                             | Context | Economic  |            0   |                   0.6 |                    0   |                      0   |                 0   |                      0   |                     0   |                   0.6 |               0 |            0 |      0 |
| My financial responsibilities outside of work influence how I show up professionally.                                     | Context | Economic  |            0.4 |                   0.8 |                    0   |                      0.8 |                 0.4 |                      0.8 |                     0.8 |                   0.6 |               0 |            0 |      0 |
| I often make career decisions primarily based on financial considerations.                                                | Context | Economic  |            0   |                   0.8 |                    0.2 |                      0.4 |                 0.4 |                      0.6 |                     0   |                   0.8 |               0 |            0 |      0 |
| I feel fully represented and included in the development of the company culture.                                          | Context | Political |            0.8 |                   1   |                    0.8 |                      1   |                 0.8 |                      0.6 |                     0.4 |                   0   |               1 |            0 |      1 |
| Unspoken cultural dynamics in my company tend to be ignored and are difficult to address.                                 | Context | Political |            0.6 |                   0.8 |                    0.6 |                      0.6 |                 0.4 |                      0.4 |                     0   |                   0   |               0 |            0 |      0 |
| I feel positive about conversations about transformation, race, or equity at work.                                        | Context | Political |            0   |                   0.4 |                    0.4 |                      0   |                 0   |                      0.2 |                     0.4 |                   0.2 |               1 |            0 |      0 |
| I feel that my identity (race, culture, background) negatively influences how others perceive my competence or potential. | Context | Political |            0.8 |                   0.8 |                    0.2 |                      1   |                 0.2 |                      1   |                     0   |                   0.6 |               0 |            0 |      0 |

## `domain-thresholds.csv`

| Domain                 |   Threshold |
|:-----------------------|------------:|
| Burnout Risk           |         267 |
| Authenticity Strain    |         257 |
| Suppressed Influence   |         118 |
| Internal Contradiction |         188 |
| Structural Misfit      |         188 |
| Old Wounds New Systems |         173 |
| Emotional Containment  |         210 |
| Values Misalignment    |         137 |

## `rules-bank.csv`

Contains 28 pairwise rules.

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

## Data Normalisation

Normalize domain names before matching:

```python
def normalize_domain_name(name: str) -> str:
    return " ".join(name.strip().replace(",", "").split())
```

This handles:

```text
Old Wounds, New Systems
Old Wounds New Systems
```

Both must resolve to:

```text
Old Wounds New Systems
```

## Data Cleaning

Some numeric cells may contain blanks or whitespace.

Use:

```python
def parse_weight(value) -> float:
    if value is None:
        return 0.0
    value = str(value).strip()
    if value == "":
        return 0.0
    return float(value)
```
