from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import QuerySet

from apps.accounts.models import ManagerAssignment, User
from apps.assessments.models import (
    Area,
    Assessment,
    Domain,
    Question,
    QuestionDomainWeight,
    SubArea,
)
from apps.licensing.models import AssessmentSession, Licence
from apps.organisations.models import Organisation
from apps.results.models import DomainScoreResult, Response, TriggeredFlag
from apps.rules.models import Rule
from config.admin_site import admin_site


class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0
    can_delete = False
    fields = ("question_order", "question_text", "raw_likert_score", "effective_likert_score", "answered_at")
    readonly_fields = ("question_order", "question_text", "raw_likert_score", "effective_likert_score", "answered_at")
    ordering = ("question__order",)

    @admin.display(description="Order")
    def question_order(self, obj: Response) -> int:
        return obj.question.order

    @admin.display(description="Question")
    def question_text(self, obj: Response) -> str:
        return obj.question.text


class DomainScoreInline(admin.TabularInline):
    model = DomainScoreResult
    extra = 0
    can_delete = False
    fields = ("domain", "score", "threshold", "triggered")
    readonly_fields = ("domain", "score", "threshold", "triggered")
    ordering = ("domain__name",)


class TriggeredFlagInline(admin.TabularInline):
    model = TriggeredFlag
    extra = 0
    can_delete = False
    fields = ("flag", "triggered_at", "insight_snapshot")
    readonly_fields = ("flag", "triggered_at", "insight_snapshot")
    ordering = ("triggered_at",)


@admin.register(User, site=admin_site)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Subjective Alignment", {"fields": ("organisation", "role")}),
    )
    list_display = ("email", "username", "role", "organisation", "is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email", "username")


admin_site.register(Organisation)
admin_site.register(ManagerAssignment)

admin_site.register(Assessment)
admin_site.register(Area)
admin_site.register(SubArea)
admin_site.register(Domain)
admin_site.register(Question)
admin_site.register(QuestionDomainWeight)

@admin.register(Licence, site=admin_site)
class LicenceAdmin(admin.ModelAdmin):
    list_display = ["id", "code", "organisation", "assessment", "status", "assigned_to", "purchased_at"]
    list_filter = ["status", "organisation"]
    search_fields = ["code", "assigned_to__email", "organisation__name"]


@admin.register(AssessmentSession, site=admin_site)
class AssessmentSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "respondent", "assessment", "status", "started_at", "completed_at", "last_activity_at"]
    list_filter = ["status", "assessment"]
    search_fields = ["respondent__email", "licence__code"]
    date_hierarchy = "completed_at"
    inlines = [DomainScoreInline, TriggeredFlagInline, ResponseInline]

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).select_related("respondent", "assessment", "licence")

admin_site.register(Response)
admin_site.register(DomainScoreResult)
admin_site.register(TriggeredFlag)

admin_site.register(Rule)

