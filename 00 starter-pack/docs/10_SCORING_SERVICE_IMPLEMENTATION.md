# Scoring Service Implementation

Create:

```text
apps/scoring/services.py
```

## Public Function

```python
def score_session(session: AssessmentSession) -> ScoreSessionResult:
    ...
```

## Responsibilities

- Validate all questions have responses.
- Calculate effective Likert scores.
- Calculate weighted domain contributions.
- Persist `DomainScoreResult` rows.
- Return domain result dictionary.

## Suggested Implementation

```python
from collections import defaultdict

def effective_score(raw_score: int, reverse_logic: bool) -> int:
    if raw_score < 1 or raw_score > 5:
        raise ValueError("Likert score must be between 1 and 5")
    return 6 - raw_score if reverse_logic else raw_score


def score_session(session):
    domain_totals = defaultdict(float)

    responses = (
        session.responses
        .select_related("question")
        .prefetch_related("question__domain_weights__domain")
    )

    for response in responses:
        score = effective_score(
            response.raw_likert_score,
            response.question.reverse_logic,
        )

        if response.effective_likert_score != score:
            response.effective_likert_score = score
            response.save(update_fields=["effective_likert_score"])

        for mapping in response.question.domain_weights.all():
            domain_totals[mapping.domain_id] += score * mapping.weight

    results = {}

    for domain in Domain.objects.all():
        total = domain_totals.get(domain.id, 0.0)
        triggered = total >= domain.threshold

        result, _ = DomainScoreResult.objects.update_or_create(
            session=session,
            domain=domain,
            defaults={
                "score": total,
                "threshold": domain.threshold,
                "triggered": triggered,
            },
        )

        results[domain.name] = result

    return results
```
