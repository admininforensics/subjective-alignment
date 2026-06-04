import secrets

from django.contrib import admin
from django.db import transaction

from apps.licensing.models import AssessmentSession, Licence


@admin.action(description="Generate licence codes for selected licences")
def generate_licence_codes(modeladmin, request, queryset):
    with transaction.atomic():
        for lic in queryset.select_for_update():
            if lic.code:
                continue
            # Short, human-shareable. Still high entropy.
            lic.code = secrets.token_urlsafe(16)[:22].upper()
            lic.save(update_fields=["code"])


@admin.register(Licence)
class LicenceAdmin(admin.ModelAdmin):
    list_display = ["id", "code", "organisation", "assessment", "status", "assigned_to", "purchased_at"]
    list_filter = ["status", "organisation"]
    search_fields = ["code", "assigned_to__email", "organisation__name"]
    actions = [generate_licence_codes]
    readonly_fields = ["assigned_at", "consumed_at", "purchased_at"]

    def get_changeform_initial_data(self, request):
        return {"status": "AVAILABLE"}


@admin.register(AssessmentSession)
class AssessmentSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "licence", "respondent", "status", "started_at", "completed_at", "last_activity_at"]
    list_filter = ["status"]
    search_fields = ["respondent__email", "licence__code"]
