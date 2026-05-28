from rest_framework import serializers

from apps.assessments.models import Assessment, Question


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ["id", "name", "version", "description", "is_active"]


class QuestionSerializer(serializers.ModelSerializer):
    area = serializers.CharField(source="area.name", read_only=True)
    subarea = serializers.CharField(source="subarea.name", read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "order",
            "text",
            "area",
            "subarea",
            "reverse_logic",
            "individual",
            "team",
        ]

