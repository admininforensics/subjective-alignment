from django.test import TestCase, override_settings

from apps.accounts.models import User, UserRole
from apps.assessments.models import Assessment
from apps.licensing.models import Licence, LicenceStatus
from apps.licensing.services import ensure_testing_licence, get_dashboard_info
from apps.organisations.models import Organisation


@override_settings(SKIP_LICENCE_REQUIREMENT=True)
class SkipLicenceRequirementTests(TestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="Test Org")
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="pw",
            organisation=self.org,
            role=UserRole.RESPONDENT,
        )
        Assessment.objects.create(name="Test Assessment", version="1.0", is_active=True)

    def test_ensure_testing_licence_auto_assigns(self):
        self.assertFalse(Licence.objects.filter(assigned_to=self.user).exists())
        ensure_testing_licence(self.user)
        licence = Licence.objects.get(assigned_to=self.user)
        self.assertEqual(licence.status, LicenceStatus.ASSIGNED)

    def test_dashboard_info_includes_auto_licence(self):
        info = get_dashboard_info(self.user)
        self.assertIsNotNone(info.assigned_licence)
