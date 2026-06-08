from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assessments.models import Question
from apps.assessments.serializers import QuestionSerializer
from apps.licensing.models import AssessmentSession
from apps.licensing.serializers import (
    ActivateLicenceRequestSerializer,
    LicenceMiniSerializer,
    ResponseSerializer,
    SaveResponseRequestSerializer,
    SessionDetailSerializer,
    SessionMiniSerializer,
)
from apps.licensing.services import (
    LicenceError,
    SessionError,
    complete_session,
    delete_latest_completed_session,
    get_dashboard_info,
    purchase_licence_for_user,
    restart_in_progress_session,
    save_response,
    simulate_survey_completion,
    start_session_for_user,
)
from apps.results.models import Response as ResponseModel
from apps.accounts.models import User, UserRole
from apps.licensing.models import Licence, LicenceStatus


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        info = get_dashboard_info(request.user)
        return Response(
            {
                "assigned_licence": LicenceMiniSerializer(info.assigned_licence).data
                if info.assigned_licence
                else None,
                "session": (
                    {
                        **SessionMiniSerializer(info.session).data,
                        "progress": info.progress,
                    }
                    if info.session
                    else None
                ),
                "latest_result": {"session_id": info.latest_completed_session.id}
                if info.latest_completed_session
                else None,
            }
        )


class StartSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session = start_session_for_user(request.user)
        return Response({"session_id": session.id, "status": session.status})


class RestartSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            session = restart_in_progress_session(user=request.user)
        except SessionError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({"session_id": session.id, "status": session.status})


class DeleteCompletedSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            delete_latest_completed_session(user=request.user)
        except SessionError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({"deleted": True})


class SimulateSurveyCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        raw_likert_score = request.data.get("raw_likert_score")
        if raw_likert_score is not None:
            try:
                raw_likert_score = int(raw_likert_score)
            except (TypeError, ValueError):
                return Response({"detail": "raw_likert_score must be an integer between 1 and 5"}, status=400)

        try:
            session = simulate_survey_completion(
                user=request.user,
                raw_likert_score=raw_likert_score,
            )
        except (SessionError, LicenceError) as exc:
            return Response({"detail": str(exc)}, status=400)

        return Response(
            {
                "session_id": session.id,
                "status": session.status,
                "questions_answered": Question.objects.filter(assessment=session.assessment).count(),
            }
        )


class SessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id: int):
        session = AssessmentSession.objects.select_related("assessment", "respondent").get(id=session_id)
        if session.respondent_id != request.user.id:
            return Response({"detail": "Forbidden"}, status=403)

        total = Question.objects.filter(assessment=session.assessment).count()
        answered = ResponseModel.objects.filter(session=session).count()
        progress = (answered / total) if total else 0.0

        questions = Question.objects.filter(assessment=session.assessment).select_related("area", "subarea")
        responses = ResponseModel.objects.filter(session=session)

        return Response(
            {
                "session": {
                    "id": session.id,
                    "status": session.status,
                    "started_at": session.started_at,
                    "completed_at": session.completed_at,
                    "last_activity_at": session.last_activity_at,
                    "progress": progress,
                },
                "questions": QuestionSerializer(questions, many=True).data,
                "responses": ResponseSerializer(responses, many=True).data,
            }
        )


class SaveResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id: int):
        session = AssessmentSession.objects.select_related("assessment", "respondent").get(id=session_id)
        if session.respondent_id != request.user.id:
            return Response({"detail": "Forbidden"}, status=403)

        payload = SaveResponseRequestSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        question = Question.objects.get(id=payload.validated_data["question_id"])
        response = save_response(
            session=session,
            question=question,
            raw_likert_score=payload.validated_data["raw_likert_score"],
        )
        return Response(
            {
                "question_id": response.question_id,
                "raw_likert_score": response.raw_likert_score,
                "effective_likert_score": response.effective_likert_score,
                "saved": True,
            }
        )


class CompleteSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id: int):
        session = AssessmentSession.objects.select_related("respondent").get(id=session_id)
        if session.respondent_id != request.user.id:
            return Response({"detail": "Forbidden"}, status=403)

        out = complete_session(session=session)
        domain_results = out["domain_results_by_name"].values()
        flags = out["triggered_flags"]

        return Response(
            {
                "session_id": session.id,
                "status": "COMPLETED",
                "domain_results": [
                    {
                        "domain": r.domain.name,
                        "score": r.score,
                        "threshold": r.threshold,
                        "triggered": r.triggered,
                    }
                    for r in domain_results
                ],
                "triggered_flags": [
                    {"flag": f.flag, "insight": f.insight_snapshot} for f in flags
                ],
            }
        )


class AssignLicenceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in {UserRole.ORG_ADMIN, UserRole.SUPER_ADMIN}:
            return Response({"detail": "Forbidden"}, status=403)

        licence_id = request.data.get("licence_id")
        user_id = request.data.get("user_id")
        if not licence_id or not user_id:
            return Response({"detail": "licence_id and user_id required"}, status=400)

        licence = Licence.objects.select_related("organisation").get(id=licence_id)
        user = User.objects.get(id=user_id)

        if request.user.role != UserRole.SUPER_ADMIN and licence.organisation_id != request.user.organisation_id:
            return Response({"detail": "Forbidden"}, status=403)
        if request.user.role != UserRole.SUPER_ADMIN and user.organisation_id != request.user.organisation_id:
            return Response({"detail": "Forbidden"}, status=403)

        if licence.status not in {LicenceStatus.AVAILABLE, LicenceStatus.ASSIGNED}:
            return Response({"detail": f"Licence not assignable (status={licence.status})"}, status=400)

        licence.assigned_to = user
        licence.assigned_by = request.user
        licence.status = LicenceStatus.ASSIGNED
        licence.save(update_fields=["assigned_to", "assigned_by", "status"])
        return Response({"assigned": True, "licence_id": licence.id, "user_id": user.id})


class PurchaseLicenceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        licence = purchase_licence_for_user(user=request.user)
        return Response(
            {
                "purchased": True,
                "licence": LicenceMiniSerializer(licence).data,
            }
        )


class ActivateLicenceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payload = ActivateLicenceRequestSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        code = payload.validated_data["code"].strip()

        if not code:
            return Response({"detail": "code required"}, status=400)
        if request.user.organisation_id is None:
            return Response({"detail": "User has no organisation"}, status=400)

        licence = (
            Licence.objects.select_related("organisation")
            .filter(code=code)
            .exclude(status__in=[LicenceStatus.REVOKED, LicenceStatus.EXPIRED, LicenceStatus.CONSUMED])
            .first()
        )
        if not licence:
            return Response({"detail": "Invalid licence code"}, status=404)

        if licence.organisation_id != request.user.organisation_id and request.user.role != UserRole.SUPER_ADMIN:
            return Response({"detail": "Forbidden"}, status=403)

        if licence.assigned_to_id and licence.assigned_to_id != request.user.id:
            return Response({"detail": "Licence already assigned"}, status=400)

        if licence.status not in {LicenceStatus.AVAILABLE, LicenceStatus.ASSIGNED}:
            return Response({"detail": f"Licence not activatable (status={licence.status})"}, status=400)

        licence.assigned_to = request.user
        licence.assigned_by = None
        licence.status = LicenceStatus.ASSIGNED
        if not licence.assigned_at:
            from django.utils import timezone

            licence.assigned_at = timezone.now()
        licence.save(update_fields=["assigned_to", "assigned_by", "status", "assigned_at"])

        return Response({"activated": True, "licence": LicenceMiniSerializer(licence).data})
