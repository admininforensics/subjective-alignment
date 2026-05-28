# Import Pipeline Implementation

Create a Django management command:

```text
apps/imports/management/commands/seed_assessment.py
```

Usage:

```bash
python manage.py seed_assessment   --questions seed_data/sa-questions-likert.csv   --thresholds seed_data/domain-thresholds.csv   --rules seed_data/rules-bank.csv   --assessment-name "Subjective Alignment Assessment"   --assessment-version "1.0"
```

## Requirements

- Idempotent
- Safe to re-run
- Uses `update_or_create`
- Logs created/updated counts
- Validates that all rule domains exist
- Normalizes domain names
- Parses blank weights as `0.0`
- Reads files with `mac_roman` encoding

## Pseudocode

```python
def seed_assessment(...):
    assessment = create_or_update_assessment()

    domains = import_domains_and_thresholds()
    questions = import_questions_and_weights()
    rules = import_rules()

    print_summary()
```

## Domain Import

```python
Domain.objects.update_or_create(
    name=normalized_domain_name,
    defaults={"threshold": threshold},
)
```

## Question Import

```python
Question.objects.update_or_create(
    assessment=assessment,
    text=question_text,
    defaults={
        "area": area,
        "subarea": subarea,
        "order": index + 1,
        "reverse_logic": bool(reverse_logic),
        "individual": bool(individual),
        "team": bool(team),
    },
)
```

## Weight Import

For each domain column:

```python
QuestionDomainWeight.objects.update_or_create(
    question=question,
    domain=domain,
    defaults={"weight": weight},
)
```

## Rule Import

```python
Rule.objects.update_or_create(
    code=slugify(f"{domain_a.name}-{domain_b.name}-{flag}"),
    defaults={
        "domain_a": domain_a,
        "domain_b": domain_b,
        "description": rule_text,
        "flag": flag,
        "insight": insight,
        "rule_type": "PAIRWISE_AND",
    },
)
```
