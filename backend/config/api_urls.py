from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import (
    LoginView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    SignupView,
)
from apps.assessments.views import CurrentAssessmentView
from apps.licensing.views import (
    ActivateLicenceView,
    AssignLicenceView,
    CompleteSessionView,
    DashboardView,
    DeleteCompletedSessionView,
    PurchaseLicenceView,
    RestartSessionView,
    SaveResponseView,
    SessionDetailView,
    StartSessionView,
)
from apps.organisations.views import OrganisationRespondentsView, OrganisationResultsView
from apps.results.views import ResultsDetailView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "auth/password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("assessment/current/", CurrentAssessmentView.as_view(), name="current-assessment"),
    path("sessions/start/", StartSessionView.as_view(), name="start-session"),
    path("sessions/restart/", RestartSessionView.as_view(), name="restart-session"),
    path("sessions/completed/", DeleteCompletedSessionView.as_view(), name="delete-completed-session"),
    path("sessions/<int:session_id>/", SessionDetailView.as_view(), name="session-detail"),
    path(
        "sessions/<int:session_id>/responses/",
        SaveResponseView.as_view(),
        name="session-save-response",
    ),
    path(
        "sessions/<int:session_id>/complete/",
        CompleteSessionView.as_view(),
        name="session-complete",
    ),
    path("results/<int:session_id>/", ResultsDetailView.as_view(), name="results-detail"),
    path(
        "organisation/respondents/",
        OrganisationRespondentsView.as_view(),
        name="org-respondents",
    ),
    path("organisation/results/", OrganisationResultsView.as_view(), name="org-results"),
    path("licences/assign/", AssignLicenceView.as_view(), name="assign-licence"),
    path("licences/purchase/", PurchaseLicenceView.as_view(), name="purchase-licence"),
    path("licences/activate/", ActivateLicenceView.as_view(), name="activate-licence"),
]

