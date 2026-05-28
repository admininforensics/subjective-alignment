from __future__ import annotations

from django.db import transaction

from apps.licensing.models import AssessmentSession
from apps.results.models import TriggeredFlag
from apps.rules.models import Rule


@transaction.atomic
def evaluate_rules(session: AssessmentSession) -> list[TriggeredFlag]:
    domain_results = {
        result.domain_id: result
        for result in session.domain_results.select_related("domain").all()
    }

    triggered_flags: list[TriggeredFlag] = []

    for rule in Rule.objects.filter(is_active=True).select_related("domain_a", "domain_b"):
        domain_a_result = domain_results.get(rule.domain_a_id)
        domain_b_result = domain_results.get(rule.domain_b_id)
        if not domain_a_result or not domain_b_result:
            continue

        if domain_a_result.triggered and domain_b_result.triggered:
            flag, _ = TriggeredFlag.objects.update_or_create(
                session=session,
                rule=rule,
                defaults={"flag": rule.flag, "insight_snapshot": rule.insight},
            )
            triggered_flags.append(flag)

    return triggered_flags

