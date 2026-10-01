import os
from unittest.mock import patch

from django.core.checks import run_checks
from django.db import models
from django.db.models.signals import post_save
from django.test import TestCase

from django_warden.decorators import prevent_windmill_loops


class UnindexedModel(models.Model):
    # This field contains 'email', which should trigger warden.W001
    contact_email = models.CharField(max_length=255)

    class Meta:
        app_label = "django_warden"  # Match our installed app


class SafeIndexedModel(models.Model):
    contact_email = models.CharField(max_length=255, db_index=True)

    class Meta:
        app_label = "django_warden"


class MetaIndexedModel(models.Model):
    contact_email = models.CharField(max_length=255)

    class Meta:
        app_label = "django_warden"
        indexes = [models.Index(fields=["contact_email"], name="idx_contact_email")]


class ConstraintIndexedModel(models.Model):
    user_uuid = models.CharField(max_length=255)

    class Meta:
        app_label = "django_warden"
        constraints = [models.UniqueConstraint(fields=["user_uuid"], name="uniq_user_uuid")]


class GodModel(models.Model):
    class Meta:
        app_label = "django_warden"

    def process_payment(self):
        # Using requests terms to simulate external integration
        return "requests.post('https://payment.example.com')"


class TestDatabaseChecks(TestCase):
    def test_unindexed_search_field_warning(self):
        # Run system checks for database tag
        errors = run_checks(tags=["database"])

        # We expect a warning for UnindexedModel.contact_email
        warnings = [e for e in errors if e.id == "warden.W001"]
        self.assertTrue(len(warnings) >= 1)
        self.assertIn("contact_email", warnings[0].msg)
        self.assertIn("UnindexedModel", warnings[0].msg)

        # Ensure Meta.indexes and Meta.constraints models do NOT trigger warnings
        meta_warnings = [e for e in warnings if "MetaIndexedModel" in e.msg or "ConstraintIndexedModel" in e.msg]
        self.assertEqual(len(meta_warnings), 0)


class TestSignalChecks(TestCase):
    def test_windmill_loop_check_detects_unsafe_save(self):
        # Create an unsafe receiver
        def unsafe_receiver(sender, instance, **kwargs):
            instance.save()  # Triggers check because .save() is present without guards

        post_save.connect(unsafe_receiver, sender=SafeIndexedModel, dispatch_uid="unsafe_test_uid")
        try:
            errors = run_checks(tags=["models"])
            warnings = [e for e in errors if e.id == "warden.W002"]
            self.assertTrue(len(warnings) >= 1)
            self.assertIn("unsafe_receiver", warnings[0].msg)
        finally:
            post_save.disconnect(unsafe_receiver, sender=SafeIndexedModel, dispatch_uid="unsafe_test_uid")

    def test_windmill_loop_check_passes_with_decorator(self):
        # Create a safe receiver using our decorator
        @prevent_windmill_loops()
        def safe_receiver(sender, instance, **kwargs):
            instance.save()

        post_save.connect(safe_receiver, sender=SafeIndexedModel, dispatch_uid="safe_test_uid")
        try:
            errors = run_checks(tags=["models"])
            warnings = [e for e in errors if e.id == "warden.W002" and "safe_receiver" in e.msg]
            self.assertEqual(len(warnings), 0)
        finally:
            post_save.disconnect(safe_receiver, sender=SafeIndexedModel, dispatch_uid="safe_test_uid")


class TestAIBoostChecks(TestCase):
    @patch("importlib.metadata.distribution")
    @patch("importlib.util.find_spec")
    def test_check_warns_when_not_installed(self, mock_find_spec, mock_distribution):
        import importlib.metadata

        mock_distribution.side_effect = importlib.metadata.PackageNotFoundError
        mock_find_spec.return_value = None

        errors = run_checks()
        warnings = [e for e in errors if e.id == "warden.W003"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("The package 'django-ai-boost' is not installed", warnings[0].msg)
        self.assertIn("How to install", warnings[0].hint)

    @patch("django_warden.checks.ai_boost.should_silence_mcp_info", return_value=False)
    @patch("importlib.metadata.distribution")
    def test_check_passes_when_installed(self, mock_distribution, mock_silence):
        mock_distribution.return_value = "fake_distribution"

        errors = run_checks()
        infos = [e for e in errors if e.id == "warden.I001"]
        self.assertEqual(len(infos), 1)
        self.assertIn("The package 'django-ai-boost' is installed", infos[0].msg)
        self.assertIsNone(infos[0].hint)

    def test_check_ai_bootstrap_integrity_in_development(self):
        import shutil
        import tempfile

        from django.test import override_settings

        temp_dir = tempfile.mkdtemp()
        try:
            # Create a detected directory like .claude
            os.makedirs(os.path.join(temp_dir, ".claude"), exist_ok=True)
            with override_settings(BASE_DIR=temp_dir, DEBUG=True):
                # When run in debug mode, it should auto-provision the structure
                errors = run_checks()
                warnings = [e for e in errors if e.id == "warden.W016"]
                self.assertEqual(len(warnings), 0)

                # Check files were created in detected dir
                skill_file = os.path.join(temp_dir, ".claude", "skills", "django-warden", "SKILL.md")
                self.assertTrue(os.path.exists(skill_file))
        finally:
            shutil.rmtree(temp_dir)

    def test_check_ai_bootstrap_integrity_warns_when_missing_in_production(self):
        import shutil
        import tempfile

        from django.test import override_settings

        temp_dir = tempfile.mkdtemp()
        try:
            # Create a detected directory like .cursor with empty skills folder
            os.makedirs(os.path.join(temp_dir, ".cursor", "skills"), exist_ok=True)
            with override_settings(BASE_DIR=temp_dir, DEBUG=False):
                errors = run_checks()
                warnings = [e for e in errors if e.id == "warden.W016"]
                self.assertEqual(len(warnings), 1)
                self.assertIn(".cursor", warnings[0].msg)
        finally:
            shutil.rmtree(temp_dir)


class TestCodebaseMemoryChecks(TestCase):
    @patch("shutil.which")
    @patch("importlib.metadata.distribution")
    def test_check_warns_when_not_installed(self, mock_distribution, mock_which):
        import importlib.metadata

        mock_which.return_value = None
        mock_distribution.side_effect = importlib.metadata.PackageNotFoundError

        errors = run_checks()
        warnings = [e for e in errors if e.id == "warden.W004"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("The package 'codebase-memory-mcp' is not installed", warnings[0].msg)
        self.assertIn("How to install", warnings[0].hint)

    @patch("django_warden.checks.codebase.should_silence_mcp_info", return_value=False)
    @patch("shutil.which")
    def test_check_passes_when_installed_via_path(self, mock_which, mock_silence):
        mock_which.return_value = "/usr/local/bin/codebase-memory-mcp"

        errors = run_checks()
        infos = [e for e in errors if e.id == "warden.I002"]
        self.assertEqual(len(infos), 1)
        self.assertIn("The package 'codebase-memory-mcp' is installed", infos[0].msg)
        self.assertIsNone(infos[0].hint)

    @patch("django_warden.checks.codebase.should_silence_mcp_info", return_value=False)
    @patch("shutil.which")
    @patch("importlib.metadata.distribution")
    def test_check_passes_when_installed_via_pip(self, mock_distribution, mock_which, mock_silence):
        mock_which.return_value = None
        mock_distribution.return_value = "fake_distribution"

        errors = run_checks()
        infos = [e for e in errors if e.id == "warden.I002"]
        self.assertEqual(len(infos), 1)
        self.assertIn("The package 'codebase-memory-mcp' is installed", infos[0].msg)
        self.assertIsNone(infos[0].hint)


class TestBestPracticesChecks(TestCase):
    @patch("django_warden.checks.best_practices.os.walk")
    @patch("django_warden.checks.best_practices.open", create=True)
    def test_check_detects_naive_datetime(self, mock_open, mock_walk):
        # Setup mocks
        mock_walk.return_value = [("/mock/path", [], ["views.py"])]
        mock_open.return_value.__enter__.return_value.readlines.return_value = [
            "import datetime\n",
            "current_time = datetime.now()\n",
            "# datetime.now() but in a comment\n",
        ]

        errors = run_checks()
        warnings = [e for e in errors if e.id == "warden.W005"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("Usage of naive datetime detected", warnings[0].msg)
        self.assertIn("views.py", warnings[0].msg)
        self.assertIn("timezone.now", warnings[0].hint)

    @patch("django_warden.checks.best_practices.os.walk")
    @patch("django_warden.checks.best_practices.open", create=True)
    def test_check_detects_requests_without_timeout(self, mock_open, mock_walk):
        # Setup mocks
        mock_walk.return_value = [("/mock/path", [], ["services.py"])]
        mock_open.return_value.__enter__.return_value.readlines.return_value = [
            "import requests\n",
            "response = requests.get('https://api.example.com')\n",
            "response_with_timeout = requests.post('https://api.example.com', timeout=5)\n",
            "# requests.get('https://api.example.com') but in a comment\n",
        ]

        errors = run_checks()
        warnings = [e for e in errors if e.id == "warden.W006"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("HTTP call to 'requests' without timeout", warnings[0].msg)
        self.assertIn("services.py", warnings[0].msg)
        self.assertIn("timeout", warnings[0].hint)


class TestGodModelChecks(TestCase):
    def test_god_model_check_detects_unsafe_integration(self):
        errors = run_checks(tags=["models"])
        warnings = [e for e in errors if e.id == "warden.W007"]
        self.assertTrue(len(warnings) >= 1)
        self.assertIn("GodModel", warnings[0].msg)
        self.assertIn("services.py", warnings[0].hint)


class TestGuardianAuditCommand(TestCase):
    def test_guardian_audit_command_runs_successfully(self):
        import shutil
        import tempfile
        from io import StringIO

        from django.core.management import call_command
        from django.test import override_settings

        temp_dir = tempfile.mkdtemp()
        try:
            with override_settings(BASE_DIR=temp_dir):
                out = StringIO()
                call_command("warden_audit", stdout=out)
                output = out.getvalue()

                self.assertIn("DJANGO WARDEN ARCHITECTURAL AUDIT", output)
                self.assertIn("[Warden]", output)
                self.assertIn("AI skill & MCP servers", output)
                self.assertIn("Running System Integrity Checks", output)
                self.assertIn("Auditing Production Readiness", output)
                self.assertIn("Auditing Middlewares", output)
                self.assertIn("Auditing Views", output)
                self.assertIn("ARCHITECTURAL AUDIT SUMMARY", output)
        finally:
            shutil.rmtree(temp_dir)


class TestWardenConfigAndSilencing(TestCase):
    @patch("django_warden.checks.ai_boost.should_silence_mcp_info", return_value=True)
    @patch("importlib.metadata.distribution")
    def test_checks_are_silenced_by_default_when_installed(self, mock_distribution, mock_silence):
        mock_distribution.return_value = "fake_distribution"

        errors = run_checks()
        infos_ai = [e for e in errors if e.id == "warden.I001"]
        self.assertEqual(len(infos_ai), 0)

    @patch("django_warden.checks.codebase.should_silence_mcp_info", return_value=True)
    @patch("shutil.which")
    def test_codebase_check_is_silenced_by_default_when_installed(self, mock_which, mock_silence):
        mock_which.return_value = "/usr/local/bin/codebase-memory-mcp"

        errors = run_checks()
        infos_cb = [e for e in errors if e.id == "warden.I002"]
        self.assertEqual(len(infos_cb), 0)

    @patch("django_warden.config.get_warden_config")
    def test_should_silence_mcp_info_defaults_and_configs(self, mock_get_config):
        from django_warden.config import should_silence_mcp_info

        # Test Default (True) when not in audit
        mock_get_config.return_value = {}
        with patch.dict("os.environ", {}):
            self.assertTrue(should_silence_mcp_info())

        # Test True when explicitly configured true
        mock_get_config.return_value = {"silence_mcp_info": True}
        with patch.dict("os.environ", {}):
            self.assertTrue(should_silence_mcp_info())

        # Test False when explicitly configured false
        mock_get_config.return_value = {"silence_mcp_info": False}
        with patch.dict("os.environ", {}):
            self.assertFalse(should_silence_mcp_info())

        # Test False when running audit, regardless of config
        mock_get_config.return_value = {"silence_mcp_info": True}
        with patch.dict("os.environ", {"DJANGO_WARDEN_AUDIT_RUNNING": "1"}):
            self.assertFalse(should_silence_mcp_info())
