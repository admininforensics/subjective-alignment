# Rule Service Implementation

Create:

```text
apps/rules/services.py
```

## Public Function

```python
def evaluate_rules(session: AssessmentSession) -> list[TriggeredFlag]:
    ...
```

## Suggested Implementation

```python
def evaluate_rules(session):
    domain_results = {
        result.domain_id: result
        for result in session.domain_results.select_related("domain")
    }

    triggered_flags = []

    for rule in Rule.objects.filter(is_active=True).select_related("domain_a", "domain_b"):
        domain_a_result = domain_results.get(rule.domain_a_id)
        domain_b_result = domain_results.get(rule.domain_b_id)

        if not domain_a_result or not domain_b_result:
            continue

        if domain_a_result.triggered and domain_b_result.triggered:
            flag, _ = TriggeredFlag.objects.update_or_create(
                session=session,
                rule=rule,
                defaults={
                    "flag": rule.flag,
                    "insight_snapshot": rule.insight,
                },
            )
            triggered_flags.append(flag)

    return triggered_flags
```

## Completion Orchestration

Create a completion function:

```python
def complete_session(session):
    validate_session_can_be_completed(session)
    score_session(session)
    flags = evaluate_rules(session)
    mark_session_completed(session)
    consume_licence(session.licence)
    return flags
```
