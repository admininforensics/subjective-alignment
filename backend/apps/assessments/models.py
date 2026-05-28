from django.db import models


class Assessment(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "version"], name="uniq_assessment_name_version")
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.version})"


class Area(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class SubArea(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="subareas")
    name = models.CharField(max_length=255)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["area", "name"], name="uniq_area_subarea")]

    def __str__(self) -> str:
        return f"{self.area.name} / {self.name}"


class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True)
    threshold = models.FloatField()
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


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
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["assessment", "text"], name="uniq_assessment_question_text")
        ]

    def __str__(self) -> str:
        return f"Q{self.order}: {self.text[:60]}"


class QuestionDomainWeight(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="domain_weights",
    )
    domain = models.ForeignKey(
        Domain,
        on_delete=models.CASCADE,
        related_name="question_weights",
    )
    weight = models.FloatField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "domain"],
                name="uniq_question_domain_weight",
            )
        ]
