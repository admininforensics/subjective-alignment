# Likert and Scoring Engine Specification

## Likert Scale

The respondent answers every question on a 1–5 scale.

| Label | Raw Score |
|---|---:|
| Strongly Disagree | 1 |
| Disagree | 2 |
| Neutral | 3 |
| Agree | 4 |
| Strongly Agree | 5 |

## Reverse Logic

Each question has a `Reverse Logic` field.

If `Reverse Logic = 0`, use raw score directly.

If `Reverse Logic = 1`, invert the score:

```python
effective_score = 6 - raw_score
```

Examples:

| Raw Score | Reverse Score |
|---:|---:|
| 1 | 5 |
| 2 | 4 |
| 3 | 3 |
| 4 | 2 |
| 5 | 1 |

## Weighted Contribution

For each question-domain mapping:

```python
contribution = effective_score * domain_weight
```

## Domain Total

```python
domain_total = sum(contributions_for_domain)
```

## Triggered Domain

```python
triggered = domain_total >= domain.threshold
```

## Completion-Time Scoring

At assessment completion:

1. Load all responses.
2. Calculate effective scores.
3. Multiply by question-domain weights.
4. Sum totals per domain.
5. Compare totals to thresholds.
6. Persist domain score results.
7. Evaluate rules.
8. Persist triggered flags and insight snapshots.

## Important

Store both:

- raw Likert score
- effective Likert score

This makes reverse-scoring auditable.
