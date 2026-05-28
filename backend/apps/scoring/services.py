from __future__ import annotations

from collections import defaultdict

from django.db import transaction

from apps.assessments.models import Domain, Question
from apps.licensing.models import AssessmentSession
from apps.results.models import DomainScoreResult, Response


def effective_score(raw_score: int, reverse_logic: bool) -> int:
    if raw_score < 1 or raw_score > 5:
        raise ValueError("Likert score must be between 1 and 5")
    return 6 - raw_score if reverse_logic else raw_score


@transaction.atomic
def score_session(session: AssessmentSession) -> dict[str, DomainScoreResult]:
    questions_count = Question.objects.filter(assessment=session.assessment).count()
    responses_qs = (
        Response.objects.filter(session=session)
        .select_related("question")
        .prefetch_related("question__domain_weights__domain")
    )
    if responses_qs.count() != questions_count:
        raise ValueError("Cannot score session until all questions have responses")

    domain_totals: dict[int, float] = defaultdict(float)

    for response in responses_qs:
        score = effective_score(response.raw_likert_score, response.question.reverse_logic)
        if response.effective_likert_score != score:
            response.effective_likert_score = score
            response.save(update_fields=["effective_likert_score"])

        for mapping in response.question.domain_weights.all():
            if mapping.weight:
                domain_totals[mapping.domain_id] += score * mapping.weight

    results: dict[str, DomainScoreResult] = {}
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

