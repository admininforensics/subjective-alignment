from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.licensing.models import AssessmentSession
from apps.licensing.services import can_view_session
from apps.results.models import DomainScoreResult, TriggeredFlag


class ResultsDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id: int):
        session = AssessmentSession.objects.select_related("respondent").get(id=session_id)
        if not can_view_session(actor=request.user, session=session):
            return Response({"detail": "Forbidden"}, status=403)

        domain_results = (
            DomainScoreResult.objects.filter(session=session)
            .select_related("domain")
            .order_by("domain__name")
        )
        flags = TriggeredFlag.objects.filter(session=session).order_by("triggered_at")

        return Response(
            {
                "session": {
                    "id": session.id,
                    "status": session.status,
                    "completed_at": session.completed_at,
                    "respondent_id": session.respondent_id,
                },
                "domain_results": [
                    {
                        "domain": r.domain.name,
                        "score": r.score,
                        "threshold": r.threshold,
                        "triggered": r.triggered,
                    }
                    for r in domain_results
                ],
                "flags": [{"flag": f.flag, "insight": f.insight_snapshot} for f in flags],
            }
        )
