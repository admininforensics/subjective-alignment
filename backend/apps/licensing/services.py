from __future__ import annotations

import random
from dataclasses import dataclass

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.assessments.models import Assessment
from apps.assessments.models import Question
from apps.licensing.models import AssessmentSession, Licence, LicenceStatus, SessionStatus
from apps.organisations.models import Organisation
from apps.results.models import Response
from apps.results.report_service import generate_report
from apps.rules.services import evaluate_rules
from apps.scoring.services import effective_score, score_session


class LicenceError(ValueError):
    pass


class SessionError(ValueError):
    pass


def _assigned_licences_for_user(user: User):
    return (
        Licence.objects.filter(assigned_to=user)
        .exclude(status__in=[LicenceStatus.REVOKED, LicenceStatus.EXPIRED])
        .order_by("-purchased_at")
    )


DEV_ORGANISATION_NAME = "Local Development"


def _ensure_dev_organisation(user: User) -> None:
    """Attach a default org in local dev when licence checks are skipped."""
    if user.organisation_id is not None:
        return
    org, _ = Organisation.objects.get_or_create(name=DEV_ORGANISATION_NAME)
    user.organisation = org
    user.save(update_fields=["organisation_id"])


def ensure_testing_licence(user: User) -> None:
    """When SKIP_LICENCE_REQUIREMENT is on, grant a usable licence without activation."""
    if not settings.SKIP_LICENCE_REQUIREMENT:
        return

    _ensure_dev_licence(user)


def _ensure_dev_licence(user: User) -> None:
    _ensure_dev_organisation(user)

    has_usable = _assigned_licences_for_user(user).exclude(status=LicenceStatus.CONSUMED).exists()
    if not has_usable:
        purchase_licence_for_user(user=user)


def ensure_debug_licence(user: User) -> None:
    """When DEBUG is on, grant a usable licence for local dev tooling."""
    if not settings.DEBUG:
        return
    if not _assigned_licences_for_user(user).exists():
        _ensure_dev_licence(user)


@dataclass(frozen=True)
class DashboardInfo:
    assigned_licence: Licence | None
    session: AssessmentSession | None
    latest_completed_session: AssessmentSession | None
    progress: float | None


def get_dashboard_info(user: User) -> DashboardInfo:
    ensure_testing_licence(user)
    assigned_licence = _assigned_licences_for_user(user).first()

    session = None
    progress = None
    if assigned_licence:
        session = getattr(assigned_licence, "session", None)
        if session:
            total = Question.objects.filter(assessment=session.assessment).count()
            answered = Response.objects.filter(session=session).count()
            progress = (answered / total) if total else 0.0

    latest_completed_session = (
        AssessmentSession.objects.filter(respondent=user, status=SessionStatus.COMPLETED)
        .order_by("-completed_at")
        .first()
    )

    return DashboardInfo(
        assigned_licence=assigned_licence,
        session=session,
        latest_completed_session=latest_completed_session,
        progress=progress,
    )


@transaction.atomic
def purchase_licence_for_user(*, user: User) -> Licence:
    """
    Creates and assigns a licence to the given user for the current active assessment.

    Payment integration is intentionally out of scope for now; this is a stub that
    enables the product flow and can later be gated behind PayFast verification.
    """
    if user.organisation_id is None:
        raise LicenceError("User has no organisation")

    assessment = Assessment.objects.filter(is_active=True).order_by("-created_at").first()
    if not assessment:
        raise LicenceError("No active assessment available")

    licence = Licence.objects.create(
        organisation_id=user.organisation_id,
        assessment=assessment,
        assigned_to=user,
        assigned_by=None,
        status=LicenceStatus.ASSIGNED,
        assigned_at=timezone.now(),
    )
    return licence


@transaction.atomic
def start_session_for_user(user: User) -> AssessmentSession:
    ensure_testing_licence(user)
    licence = (
        Licence.objects.select_for_update()
        .filter(assigned_to=user)
        .exclude(status__in=[LicenceStatus.REVOKED, LicenceStatus.EXPIRED])
        .order_by("-purchased_at")
        .first()
    )
    if not licence:
        raise LicenceError("No assigned active licence")

    if licence.status == LicenceStatus.CONSUMED:
        raise LicenceError("Assigned licence already consumed")

    session = getattr(licence, "session", None)
    if session:
        if session.status in {SessionStatus.COMPLETED, SessionStatus.LOCKED}:
            raise SessionError("Session already completed")
        if session.status == SessionStatus.NOT_STARTED:
            session.status = SessionStatus.IN_PROGRESS
            session.started_at = session.started_at or timezone.now()
        session.last_activity_at = timezone.now()
        session.save(update_fields=["status", "started_at", "last_activity_at"])
    else:
        session = AssessmentSession.objects.create(
            licence=licence,
            respondent=user,
            assessment=licence.assessment,
            status=SessionStatus.IN_PROGRESS,
            started_at=timezone.now(),
            last_activity_at=timezone.now(),
        )

    licence.status = LicenceStatus.IN_PROGRESS
    licence.assigned_at = licence.assigned_at or timezone.now()
    licence.save(update_fields=["status", "assigned_at"])
    return session


@transaction.atomic
def save_response(*, session: AssessmentSession, question: Question, raw_likert_score: int) -> Response:
    session = AssessmentSession.objects.select_for_update().get(id=session.id)
    if session.status in {SessionStatus.COMPLETED, SessionStatus.LOCKED}:
        raise SessionError("Cannot edit a completed session")
    if session.respondent_id is None:
        raise SessionError("Session has no respondent")

    eff = effective_score(raw_likert_score, question.reverse_logic)
    response, _ = Response.objects.update_or_create(
        session=session,
        question=question,
        defaults={
            "raw_likert_score": raw_likert_score,
            "effective_likert_score": eff,
        },
    )
    session.status = SessionStatus.IN_PROGRESS
    session.last_activity_at = timezone.now()
    session.save(update_fields=["status", "last_activity_at"])
    return response


@transaction.atomic
def complete_session(*, session: AssessmentSession) -> dict:
    session = AssessmentSession.objects.select_for_update().select_related("licence").get(id=session.id)
    if session.status in {SessionStatus.COMPLETED, SessionStatus.LOCKED}:
        raise SessionError("Session already completed")

    domain_results_by_name = score_session(session)
    flags = evaluate_rules(session)
    generate_report(session=session)

    session.status = SessionStatus.COMPLETED
    session.completed_at = timezone.now()
    session.last_activity_at = timezone.now()
    session.save(update_fields=["status", "completed_at", "last_activity_at"])

    licence = Licence.objects.select_for_update().get(id=session.licence_id)
    licence.status = LicenceStatus.CONSUMED
    licence.consumed_at = timezone.now()
    licence.save(update_fields=["status", "consumed_at"])

    return {"domain_results_by_name": domain_results_by_name, "triggered_flags": flags}


@transaction.atomic
def delete_latest_completed_session(*, user: User) -> None:
    session = (
        AssessmentSession.objects.select_for_update()
        .filter(respondent=user, status=SessionStatus.COMPLETED)
        .order_by("-completed_at")
        .first()
    )
    if not session:
        raise SessionError("No completed assessment to delete")

    licence = Licence.objects.select_for_update().get(id=session.licence_id)
    session.delete()
    # Keep the licence so the user can start a new assessment (testing / retake flow).
    licence.status = LicenceStatus.ASSIGNED
    licence.consumed_at = None
    licence.save(update_fields=["status", "consumed_at"])


def can_simulate_survey(*, user: User) -> bool:
    """True when the user may use survey simulation (admin flag or local DEBUG)."""
    return bool(user.allow_survey_simulation or settings.DEBUG)


@transaction.atomic
def simulate_survey_completion(*, user: User, raw_likert_score: int | None = None) -> AssessmentSession:
    """Fill every question and complete the session. Testing helper for flagged users or DEBUG."""
    if not can_simulate_survey(user=user):
        raise SessionError("Survey simulation is not enabled for this account")

    if raw_likert_score is not None and (raw_likert_score < 1 or raw_likert_score > 5):
        raise SessionError("Likert score must be between 1 and 5")

    ensure_debug_licence(user)
    ensure_testing_licence(user)
    licence = (
        Licence.objects.select_for_update()
        .filter(assigned_to=user)
        .exclude(status__in=[LicenceStatus.REVOKED, LicenceStatus.EXPIRED])
        .order_by("-purchased_at")
        .first()
    )
    if not licence:
        raise LicenceError("No assigned active licence")

    if licence.status == LicenceStatus.CONSUMED:
        delete_latest_completed_session(user=user)
        licence.refresh_from_db()

    session = start_session_for_user(user)
    session = AssessmentSession.objects.select_for_update().get(id=session.id)

    questions = list(Question.objects.filter(assessment=session.assessment).order_by("order"))
    if not questions:
        raise SessionError("Assessment has no questions")

    Response.objects.filter(session=session).delete()
    responses = []
    for question in questions:
        score = raw_likert_score if raw_likert_score is not None else random.randint(1, 5)
        responses.append(
            Response(
                session=session,
                question=question,
                raw_likert_score=score,
                effective_likert_score=effective_score(score, question.reverse_logic),
            )
        )
    Response.objects.bulk_create(responses)

    session.last_activity_at = timezone.now()
    session.save(update_fields=["last_activity_at"])
    complete_session(session=session)
    return AssessmentSession.objects.get(id=session.id)


@transaction.atomic
def restart_in_progress_session(*, user: User) -> AssessmentSession:
    ensure_testing_licence(user)
    licence = (
        Licence.objects.select_for_update()
        .filter(assigned_to=user)
        .exclude(status__in=[LicenceStatus.REVOKED, LicenceStatus.EXPIRED, LicenceStatus.CONSUMED])
        .order_by("-purchased_at")
        .first()
    )
    if not licence:
        raise SessionError("No active assessment to restart")

    session = getattr(licence, "session", None)
    if session:
        if session.status in {SessionStatus.COMPLETED, SessionStatus.LOCKED}:
            raise SessionError("Completed assessments cannot be restarted. Delete the previous one first.")
        session.delete()

    licence.status = LicenceStatus.ASSIGNED
    licence.consumed_at = None
    licence.save(update_fields=["status", "consumed_at"])
    return start_session_for_user(user)


def can_view_session(*, actor: User, session: AssessmentSession) -> bool:
    if actor.role == UserRole.SUPER_ADMIN:
        return True
    if session.respondent_id == actor.id:
        return True
    if actor.role == UserRole.ORG_ADMIN and actor.organisation_id == session.respondent.organisation_id:
        return True
    if actor.role == UserRole.MANAGER:
        return actor.managed_assignments.filter(respondent_id=session.respondent_id).exists()
    return False

