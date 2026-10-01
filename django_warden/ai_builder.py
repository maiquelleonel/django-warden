import json
import os

from django.template import Context, Engine

from django_warden.skill_distribution import install_companion_skills


def get_template_content(template_name: str) -> str:
    """
    Reads the content of a template file from the packaged templates,
    or directly from repository root if running in local source tree.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if template_name == "SKILL.md.tpl":
        root_skill = os.path.join(current_dir, "..", "SKILL.md")
        if os.path.isfile(root_skill):
            with open(root_skill, "r", encoding="utf-8") as f:
                return f.read()

    template_path = os.path.join(current_dir, "templates", "warden_ai", template_name)
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


KNOWN_AI_DIRECTORIES = [".gemini", ".claude"]
DEFAULT_AI_DIRECTORIES = [".gemini", ".claude"]


def _get_target_directories(base_dir: str, create_defaults_if_empty: bool = True) -> list[str]:
    """
    Determines all active target directories for AI instructions and MCP settings.
    Scans base_dir for any known AI assistant directory or any hidden directory
    containing a 'skills' subfolder or 'settings.json' file.
    """
    base_dir = str(base_dir)
    detected = set()

    # 1. Check for presence of known AI assistant directories
    for directory_name in KNOWN_AI_DIRECTORIES:
        if os.path.isdir(os.path.join(base_dir, directory_name)):
            detected.add(directory_name)

    # 2. Dynamically discover any other hidden directory with a 'skills' folder or 'settings.json'
    try:
        if os.path.exists(base_dir):
            for entry in os.listdir(base_dir):
                entry_path = os.path.join(base_dir, entry)
                if os.path.isdir(entry_path) and entry.startswith("."):
                    skills_path = os.path.join(entry_path, "skills")
                    settings_file = os.path.join(entry_path, "settings.json")
                    if os.path.isdir(skills_path) or os.path.exists(settings_file):
                        detected.add(entry)
    except OSError:
        pass

    # If no AI folder was found, optionally provision the default primary assistants
    if not detected and create_defaults_if_empty:
        detected.update(DEFAULT_AI_DIRECTORIES)

    return sorted(detected)


def _write_skill_file(target_path: str, rendered_skill: str) -> bool:
    """
    Writes the SKILL.md file to target_path/skills/django-warden/SKILL.md.
    Returns True if a new file was created.
    """
    if not rendered_skill:
        return False

    skill_dir = os.path.join(target_path, "skills", "django-warden")
    os.makedirs(skill_dir, exist_ok=True)
    skill_file_path = os.path.join(skill_dir, "SKILL.md")
    skill_existed = os.path.exists(skill_file_path)

    try:
        with open(skill_file_path, "w", encoding="utf-8") as f:
            f.write(rendered_skill)
        return not skill_existed
    except Exception:
        return False


def _merge_or_create_settings(target_path: str, new_settings: dict) -> bool:
    """
    Merges or creates settings.json under target_path/settings.json.
    Returns True if a new settings file was created.
    """
    if new_settings is None:
        return False

    settings_file_path = os.path.join(target_path, "settings.json")
    settings_existed = os.path.exists(settings_file_path)

    try:
        if settings_existed:
            _merge_existing_settings(settings_file_path, new_settings)
            return False
        else:
            os.makedirs(os.path.dirname(settings_file_path), exist_ok=True)
            with open(settings_file_path, "w", encoding="utf-8") as f:
                json.dump(new_settings, f, indent=2)
            return True
    except Exception:
        return False


def _merge_existing_settings(settings_file_path: str, new_settings: dict):
    """
    Safely merges new_settings into an existing settings.json file.
    """
    with open(settings_file_path, "r", encoding="utf-8") as f:
        try:
            existing_settings = json.load(f)
            if not isinstance(existing_settings, dict):
                existing_settings = {}
        except json.JSONDecodeError:
            existing_settings = {}

    existing_mcp = existing_settings.setdefault("mcpServers", {})
    if isinstance(existing_mcp, dict) and "mcpServers" in new_settings:
        existing_mcp.update(new_settings["mcpServers"])

    with open(settings_file_path, "w", encoding="utf-8") as f:
        json.dump(existing_settings, f, indent=2)


def ensure_ai_structure(base_dir: str, context: dict) -> tuple[list[str], bool, bool]:
    """
    Ensures that the directory structure and AI instruction files are set up.
    Can write to multiple directories (e.g., both .gemini and .claude if they exist).
    Returns (targets_processed, any_skill_created, any_settings_created).
    """
    targets = _get_target_directories(base_dir)
    any_skill_created = False
    any_settings_created = False

    # Render skill template
    try:
        skill_template = get_template_content("SKILL.md.tpl")
        engine = Engine()
        template = engine.from_string(skill_template)
        rendered_skill = template.render(Context(context))
    except Exception:
        rendered_skill = ""

    # Render settings template
    try:
        json_template = get_template_content("settings.json.tpl")
        engine = Engine()
        template_json = engine.from_string(json_template)
        rendered_json_str = template_json.render(Context(context))
        new_settings = json.loads(rendered_json_str)
    except Exception:
        new_settings = None

    for target_dir in targets:
        target_path = os.path.join(base_dir, target_dir)
        if _write_skill_file(target_path, rendered_skill):
            any_skill_created = True
        if _merge_or_create_settings(target_path, new_settings):
            any_settings_created = True

    any_skill_created |= install_companion_skills(base_dir, targets)
    return targets, any_skill_created, any_settings_created
