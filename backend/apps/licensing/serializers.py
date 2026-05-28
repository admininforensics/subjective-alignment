from rest_framework import serializers

from apps.licensing.models import AssessmentSession, Licence
from apps.results.models import Response


class LicenceMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licence
        fields = ["id", "status"]


class SessionMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentSession
        fields = ["id", "status"]


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ["question_id", "raw_likert_score", "effective_likert_score", "answered_at"]


class SaveResponseRequestSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    raw_likert_score = serializers.IntegerField(min_value=1, max_value=5)


class ActivateLicenceRequestSerializer(serializers.Serializer):
    code = serializers.CharField()


class SessionDetailSerializer(serializers.ModelSerializer):
    progress = serializers.FloatField()

    class Meta:
        model = AssessmentSession
        fields = ["id", "status", "started_at", "completed_at", "last_activity_at", "progress"]

