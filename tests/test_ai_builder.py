import json
import os
import shutil
import tempfile
from unittest import TestCase

from django_warden.ai_builder import ensure_ai_structure


class TestAIBuilder(TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.context = {"settings_module": "myproject.settings"}

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_ensure_ai_structure_creates_default_dirs(self):
        targets, skill_created, settings_created = ensure_ai_structure(self.test_dir, self.context)

        gemini_dir = os.path.join(self.test_dir, ".gemini")
        claude_dir = os.path.join(self.test_dir, ".claude")

        self.assertTrue(os.path.isdir(gemini_dir))
        self.assertTrue(os.path.isdir(claude_dir))

        gemini_skill = os.path.join(gemini_dir, "skills", "django-warden", "SKILL.md")
        claude_skill = os.path.join(claude_dir, "skills", "django-warden", "SKILL.md")

        self.assertTrue(os.path.isfile(gemini_skill))
        self.assertTrue(os.path.isfile(claude_skill))

        gemini_settings = os.path.join(gemini_dir, "settings.json")
        claude_settings = os.path.join(claude_dir, "settings.json")

        self.assertTrue(os.path.isfile(gemini_settings))
        self.assertTrue(os.path.isfile(claude_settings))

        with open(gemini_settings, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertIn("mcpServers", data)
            self.assertIn("django-ai-boost", data["mcpServers"])
            self.assertIn("codebase-memory-mcp", data["mcpServers"])
            self.assertEqual(data["mcpServers"]["django-ai-boost"]["args"][1], "myproject.settings")

        self.assertTrue(skill_created)
        self.assertTrue(settings_created)
        self.assertEqual(len(targets), 2)

    def test_ensure_ai_structure_zed_uses_context_servers(self):
        zed_dir = os.path.join(self.test_dir, ".zed")
        os.makedirs(zed_dir)

        zed_settings = os.path.join(zed_dir, "settings.json")
        with open(zed_settings, "w", encoding="utf-8") as f:
            json.dump({"theme": "One Dark", "context_servers": {"custom-mcp": {"command": "test"}}}, f)

        targets, _, _ = ensure_ai_structure(self.test_dir, self.context)

        with open(zed_settings, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["theme"], "One Dark")
            self.assertNotIn("mcpServers", data)
            self.assertIn("context_servers", data)
            self.assertIn("custom-mcp", data["context_servers"])
            self.assertIn("django-ai-boost", data["context_servers"])
            self.assertEqual(data["context_servers"]["django-ai-boost"]["command"], "uv")
            self.assertEqual(data["context_servers"]["django-ai-boost"]["args"][:2], ["run", "django-ai-boost"])

    def test_ensure_ai_structure_discovers_existing_dirs(self):
        custom_dir = os.path.join(self.test_dir, ".custom_ai")
        os.makedirs(os.path.join(custom_dir, "skills"))

        targets, skill_created, settings_created = ensure_ai_structure(self.test_dir, self.context)

        self.assertIn(".custom_ai", targets)
        self.assertTrue(os.path.isfile(os.path.join(custom_dir, "skills", "django-warden", "SKILL.md")))
        self.assertTrue(os.path.isfile(os.path.join(custom_dir, "settings.json")))

    def test_ensure_ai_structure_merges_settings(self):
        gemini_dir = os.path.join(self.test_dir, ".gemini")
        os.makedirs(gemini_dir)
        settings_file = os.path.join(gemini_dir, "settings.json")

        existing_content = {"theme": "dark", "mcpServers": {"custom-server": {"command": "custom-cmd"}}}
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(existing_content, f)

        targets, _, settings_created = ensure_ai_structure(self.test_dir, self.context)

        with open(settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["theme"], "dark")
        self.assertIn("custom-server", data["mcpServers"])
        self.assertIn("django-ai-boost", data["mcpServers"])
        self.assertIn("codebase-memory-mcp", data["mcpServers"])
