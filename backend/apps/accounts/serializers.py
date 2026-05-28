from rest_framework import serializers

from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    organisation_id = serializers.IntegerField(allow_null=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "role", "organisation_id"]

