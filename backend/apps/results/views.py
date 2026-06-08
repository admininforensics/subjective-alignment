from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.licensing.models import AssessmentSession, SessionStatus
from apps.licensing.services import can_view_session
from apps.results.models import AssessmentReport, DomainScoreResult, TriggeredFlag
from apps.results.report_service import generate_report


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

        report = AssessmentReport.objects.filter(session=session).first()
        if not report and session.status == SessionStatus.COMPLETED:
            report = generate_report(session=session)

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
                "report": report.content if report else None,
            }
        )
