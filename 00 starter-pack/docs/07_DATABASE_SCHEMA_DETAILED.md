# Detailed Database Schema

Use Django models with PostgreSQL.

## Organisation

```python
class Organisation(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
```

## User

Use Django's `AbstractUser` or a custom user model.

```python
class User(AbstractUser):
    organisation = models.ForeignKey(
        Organisation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )
    role = models.CharField(max_length=50)
```

Suggested roles:

```text
RESPONDENT
MANAGER
ORG_ADMIN
SUPER_ADMIN
```

## Assessment

```python
class Assessment(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "version")
```

## Area and SubArea

```python
class Area(models.Model):
    name = models.CharField(max_length=255, unique=True)

class SubArea(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="subareas")
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ("area", "name")
```

## Domain

```python
class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True)
    threshold = models.FloatField()
    description = models.TextField(blank=True)
```

## Question

```python
class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="questions")
    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    subarea = models.ForeignKey(SubArea, on_delete=models.PROTECT)
    text = models.TextField()
    order = models.PositiveIntegerField()
    reverse_logic = models.BooleanField(default=False)
    individual = models.BooleanField(default=False)
    team = models.BooleanField(default=False)

    class Meta:
        unique_together = ("assessment", "text")
        ordering = ["order"]
```

## QuestionDomainWeight

```python
class QuestionDomainWeight(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="domain_weights")
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="question_weights")
    weight = models.FloatField(default=0)

    class Meta:
        unique_together = ("question", "domain")
```

## Licence

```python
class Licence(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name="licences")
    assessment = models.ForeignKey(Assessment, on_delete=models.PROTECT)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    assigned_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_licences")
    status = models.CharField(max_length=50, default="AVAILABLE")
    purchased_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
```

Statuses:

```text
AVAILABLE
ASSIGNED
IN_PROGRESS
CONSUMED
EXPIRED
REVOKED
```

## AssessmentSession

```python
class AssessmentSession(models.Model):
    licence = models.OneToOneField(Licence, on_delete=models.PROTECT, related_name="session")
    respondent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessment_sessions")
    assessment = models.ForeignKey(Assessment, on_delete=models.PROTECT)
    status = models.CharField(max_length=50, default="NOT_STARTED")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
```

Statuses:

```text
NOT_STARTED
IN_PROGRESS
COMPLETED
LOCKED
RESET
```

## Response

```python
class Response(models.Model):
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    raw_likert_score = models.PositiveSmallIntegerField()
    effective_likert_score = models.PositiveSmallIntegerField()
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("session", "question")
```

## DomainScoreResult

```python
class DomainScoreResult(models.Model):
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name="domain_results")
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
    score = models.FloatField()
    threshold = models.FloatField()
    triggered = models.BooleanField(default=False)

    class Meta:
        unique_together = ("session", "domain")
```

## Rule

```python
class Rule(models.Model):
    code = models.SlugField(max_length=150, unique=True)
    rule_type = models.CharField(max_length=50, default="PAIRWISE_AND")
    domain_a = models.ForeignKey(Domain, on_delete=models.PROTECT, related_name="rules_as_domain_a")
    domain_b = models.ForeignKey(Domain, on_delete=models.PROTECT, related_name="rules_as_domain_b")
    description = models.TextField(blank=True)
    flag = models.CharField(max_length=255)
    insight = models.TextField()
    is_active = models.BooleanField(default=True)
```

## TriggeredFlag

```python
class TriggeredFlag(models.Model):
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name="triggered_flags")
    rule = models.ForeignKey(Rule, on_delete=models.PROTECT)
    flag = models.CharField(max_length=255)
    insight_snapshot = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session", "rule")
```
