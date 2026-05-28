from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assessments.serializers import AssessmentSerializer
from apps.licensing.models import Licence, LicenceStatus


class CurrentAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        licence = (
            Licence.objects.filter(assigned_to=request.user)
            .exclude(status__in=[LicenceStatus.EXPIRED, LicenceStatus.REVOKED])
            .order_by("-purchased_at")
            .first()
        )
        if not licence:
            return Response({"detail": "No assigned licence"}, status=404)
        return Response(AssessmentSerializer(licence.assessment).data)
