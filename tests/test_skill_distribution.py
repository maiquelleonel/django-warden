import json
import os
import tempfile
from pathlib import Path
from unittest import skipIf
from unittest.mock import patch

from django.test import SimpleTestCase

from django_warden.ai_builder import ensure_ai_structure
from django_warden.skill_distribution import MANIFEST_NAME, SKILL_SOURCE, _write_atomic, install_companion_skills

SKILLS = {
    "alpinejs-django",
    "django-backend",
    "django-htmx",
    "django-templates",
    "django-testing",
    "django-web-security",
}


class CompanionSkillTests(SimpleTestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.target = self.base / ".claude" / "skills"

    def install(self):
        return install_companion_skills(str(self.base), [".claude"])

    def test_bootstrap_copies_complete_catalog_and_references_as_bytes(self):
        targets, created, settings_created = ensure_ai_structure(
            str(self.base), {"project_name": "example", "settings_module": "example.settings"}
        )
        self.assertTrue(created)
        self.assertTrue(settings_created)
        self.assertEqual({p.parent.name for p in SKILL_SOURCE.glob("*/SKILL.md")}, SKILLS)
        for target in targets:
            for source in SKILL_SOURCE.rglob("*.md"):
                with self.subTest(target=target, file=source.relative_to(SKILL_SOURCE)):
                    installed = self.base / target / "skills" / source.relative_to(SKILL_SOURCE)
                    self.assertEqual(installed.read_bytes(), source.read_bytes())

    def test_second_install_preserves_content_mtimes_and_reports_no_creation(self):
        self.assertTrue(self.install())
        before = {p: p.stat().st_mtime_ns for p in self.target.rglob("*") if p.is_file()}
        self.assertFalse(self.install())
        self.assertEqual(before, {p: p.stat().st_mtime_ns for p in before})

    def test_local_unowned_skill_is_preserved_as_a_whole(self):
        skill = self.target / "django-backend"
        skill.mkdir(parents=True)
        entrypoint = skill / "SKILL.md"
        entrypoint.write_text("Local instructions", encoding="utf-8")
        with self.assertLogs("django_warden.skill_distribution", level="WARNING") as logs:
            self.assertTrue(self.install())
        self.assertIn("Preserving locally maintained", logs.output[0])
        self.assertEqual(entrypoint.read_text(), "Local instructions")
        self.assertFalse((skill / "references").exists())
        self.assertFalse((skill / MANIFEST_NAME).exists())
        self.assertTrue((self.target / "django-htmx" / "SKILL.md").exists())

    def test_identical_unowned_files_can_be_adopted(self):
        skill = self.target / "django-backend"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_bytes((SKILL_SOURCE / "django-backend" / "SKILL.md").read_bytes())
        self.install()
        self.assertIn("SKILL.md", json.loads((skill / MANIFEST_NAME).read_text()))

    def test_existing_reference_conflict_prevents_partial_skill_install(self):
        skill = self.target / "django-backend"
        reference = skill / "references" / "architecture.md"
        reference.parent.mkdir(parents=True)
        reference.write_text("Local architecture", encoding="utf-8")
        with self.assertLogs("django_warden.skill_distribution", level="WARNING"):
            self.install()
        self.assertFalse((skill / "SKILL.md").exists())
        self.assertEqual(reference.read_text(), "Local architecture")

    def test_modified_managed_file_blocks_upgrade_without_losing_edits(self):
        self.install()
        file = self.target / "django-backend" / "SKILL.md"
        file.write_text("Changed locally", encoding="utf-8")
        with self.assertLogs("django_warden.skill_distribution", level="WARNING"):
            self.assertFalse(self.install())
        self.assertEqual(file.read_text(), "Changed locally")

    def test_package_upgrade_refreshes_managed_bytes_and_adds_references(self):
        source = self.base / "package" / "example"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("Version 1: {{ keep }}", encoding="utf-8")
        with patch("django_warden.skill_distribution.SKILL_SOURCE", source.parent):
            self.assertTrue(self.install())
            (source / "SKILL.md").write_text("Version 2: {% include 'literal.html' %}", encoding="utf-8")
            (source / "references").mkdir()
            (source / "references" / "details.md").write_text("New reference", encoding="utf-8")
            self.assertTrue(self.install())
            self.assertFalse(self.install())
        self.assertEqual((self.target / "example" / "SKILL.md").read_bytes(), (source / "SKILL.md").read_bytes())
        self.assertTrue((self.target / "example" / "references" / "details.md").exists())

    def test_removed_reference_retains_ownership_if_reintroduced(self):
        source = self.base / "package" / "example"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("Entry", encoding="utf-8")
        reference = source / "details.md"
        reference.write_text("Version 1", encoding="utf-8")
        with patch("django_warden.skill_distribution.SKILL_SOURCE", source.parent):
            self.install()
            reference.unlink()
            self.install()
            installed = self.target / "example" / "details.md"
            self.assertEqual(installed.read_text(), "Version 1")
            reference.write_text("Version 3", encoding="utf-8")
            self.install()
            self.assertEqual(installed.read_text(), "Version 3")

    def test_missing_managed_reference_is_restored(self):
        self.install()
        relative = Path("django-backend/references/architecture.md")
        installed = self.target / relative
        installed.unlink()
        self.assertTrue(self.install())
        self.assertEqual(installed.read_bytes(), (SKILL_SOURCE / relative).read_bytes())

    def test_atomic_replace_failure_preserves_previous_file_and_cleans_temporary(self):
        target = self.base / "guide.md"
        target.write_text("Previous", encoding="utf-8")
        with patch("django_warden.skill_distribution.os.replace", side_effect=OSError("interrupted")):
            with self.assertRaises(OSError):
                _write_atomic(target, b"New")
        self.assertEqual(target.read_text(), "Previous")
        self.assertEqual(list(self.base.iterdir()), [target])

    def test_atomic_write_preserves_an_internal_file_symlink(self):
        target = self.base / "guide.md"
        target.write_text("Previous", encoding="utf-8")
        link = self.base / "link.md"
        link.symlink_to(target)
        _write_atomic(link, b"New")
        self.assertTrue(link.is_symlink())
        self.assertEqual(target.read_bytes(), b"New")

    @skipIf(os.name == "nt", "POSIX file modes")
    def test_atomic_write_preserves_existing_permissions(self):
        target = self.base / "guide.md"
        target.write_text("Previous", encoding="utf-8")
        target.chmod(0o640)
        _write_atomic(target, b"New")
        self.assertEqual(target.stat().st_mode & 0o777, 0o640)

    @skipIf(os.name == "nt", "POSIX file modes")
    def test_new_package_documentation_is_readable_by_other_users(self):
        target = self.base / "guide.md"
        _write_atomic(target, b"Public package documentation")
        self.assertEqual(target.stat().st_mode & 0o777, 0o644)

    def test_custom_skills_and_unmanaged_extra_references_are_preserved(self):
        local = self.target / "local-project" / "SKILL.md"
        extra = self.target / "django-backend" / "references" / "local.md"
        for path in (local, extra):
            path.parent.mkdir(parents=True)
            path.write_text("Project-owned", encoding="utf-8")
        self.install()
        self.assertEqual(local.read_text(), "Project-owned")
        self.assertEqual(extra.read_text(), "Project-owned")

    def test_broken_or_non_object_manifest_preserves_skill_and_warns(self):
        self.install()
        manifest = self.target / "django-backend" / MANIFEST_NAME
        for content in ("{invalid", "[]"):
            with self.subTest(content=content):
                manifest.write_text(content, encoding="utf-8")
                with self.assertLogs("django_warden.skill_distribution", level="WARNING"):
                    self.assertFalse(self.install())
                self.assertEqual(manifest.read_text(), content)

    def test_shared_skill_symlink_is_preserved_and_installed_once(self):
        shared = self.base / ".agents" / "skills"
        shared.mkdir(parents=True)
        self.target.parent.mkdir()
        self.target.symlink_to(shared, target_is_directory=True)
        with patch("django_warden.skill_distribution._install_skill", return_value=True) as installer:
            install_companion_skills(str(self.base), [".claude", ".agents"])
        self.assertEqual(installer.call_count, len(SKILLS))
        self.install()
        self.assertTrue(self.target.is_symlink())
        self.assertTrue((shared / "django-backend" / "SKILL.md").exists())

    def test_external_directory_symlink_is_not_written(self):
        with tempfile.TemporaryDirectory() as outside:
            self.target.parent.mkdir()
            self.target.symlink_to(outside, target_is_directory=True)
            with self.assertLogs("django_warden.skill_distribution", level="WARNING"):
                self.assertFalse(self.install())
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_external_file_symlink_is_not_written(self):
        with tempfile.TemporaryDirectory() as outside:
            protected = Path(outside) / "protected.md"
            protected.write_text("Keep", encoding="utf-8")
            skill = self.target / "django-backend"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").symlink_to(protected)
            with self.assertLogs("django_warden.skill_distribution", level="WARNING"):
                self.install()
            self.assertEqual(protected.read_text(), "Keep")
            self.assertFalse((skill / MANIFEST_NAME).exists())

    def test_io_failure_is_visible_and_does_not_claim_installation(self):
        with patch("django_warden.skill_distribution._install_skill", side_effect=OSError("read only")):
            with self.assertLogs("django_warden.skill_distribution", level="WARNING") as logs:
                self.assertFalse(self.install())
        self.assertEqual(len(logs.output), len(SKILLS))

    def test_no_targets_has_no_side_effects(self):
        self.assertFalse(install_companion_skills(str(self.base), []))
        self.assertEqual(list(self.base.iterdir()), [])

    def test_repository_and_packaged_warden_guides_match(self):
        package = SKILL_SOURCE.parent
        root = package.parent / "SKILL.md"
        template = package / "templates" / "warden_ai" / "SKILL.md.tpl"
        self.assertEqual(root.read_bytes(), template.read_bytes())
