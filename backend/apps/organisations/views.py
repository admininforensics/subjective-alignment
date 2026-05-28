from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User, UserRole
from apps.accounts.serializers import UserSerializer
from apps.licensing.models import AssessmentSession, Licence, LicenceStatus, SessionStatus
from apps.licensing.services import can_view_session
from apps.results.models import TriggeredFlag


class OrganisationRespondentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in {UserRole.ORG_ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER}:
            return Response({"detail": "Forbidden"}, status=403)

        qs = User.objects.filter(role=UserRole.RESPONDENT)
        if request.user.role != UserRole.SUPER_ADMIN:
            qs = qs.filter(organisation_id=request.user.organisation_id)
        return Response(UserSerializer(qs.order_by("id"), many=True).data)


class OrganisationResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in {UserRole.ORG_ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER}:
            return Response({"detail": "Forbidden"}, status=403)

        sessions = AssessmentSession.objects.select_related("respondent").filter(status=SessionStatus.COMPLETED)
        if request.user.role == UserRole.ORG_ADMIN:
            sessions = sessions.filter(respondent__organisation_id=request.user.organisation_id)
        elif request.user.role == UserRole.MANAGER:
            sessions = sessions.filter(respondent__manager_assignments__manager=request.user)

        out = []
        for session in sessions.order_by("-completed_at")[:200]:
            if not can_view_session(actor=request.user, session=session):
                continue
            flags = list(
                TriggeredFlag.objects.filter(session=session)
                .order_by("triggered_at")
                .values_list("flag", flat=True)
            )
            out.append(
                {
                    "session_id": session.id,
                    "respondent_id": session.respondent_id,
                    "completed_at": session.completed_at,
                    "flags": flags,
                }
            )

        return Response(out)
