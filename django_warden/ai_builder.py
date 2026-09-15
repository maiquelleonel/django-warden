import json
import os

from django.template import Context, Engine


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


def _get_target_directories(base_dir: str, create_defaults_if_empty: bool = True) -> list[str]:
    """
    Discovers AI assistant directories in base_dir.
    Looks for standard AI folders (.gemini, .claude, .cursor, .zed) or any hidden
    folder containing a 'skills' subfolder or 'settings.json'.
    """
    known_ai_dirs = [".gemini", ".claude", ".cursor", ".zed"]
    targets = []

    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if not os.path.isdir(path) or not name.startswith("."):
            continue

        if name in known_ai_dirs:
            targets.append(path)
            continue

        skills_dir = os.path.join(path, "skills")
        settings_file = os.path.join(path, "settings.json")
        if os.path.isdir(skills_dir) or os.path.isfile(settings_file):
            targets.append(path)

    if not targets and create_defaults_if_empty:
        targets = [
            os.path.join(base_dir, ".gemini"),
            os.path.join(base_dir, ".claude"),
        ]

    return sorted(targets)


def _write_skill_file(target_path: str, skill_content: str) -> bool:
    """
    Creates or updates the SKILL.md file inside the target directory.
    """
    skills_dir = os.path.join(target_path, "skills", "django-warden")
    os.makedirs(skills_dir, exist_ok=True)
    skill_file = os.path.join(skills_dir, "SKILL.md")

    created = not os.path.exists(skill_file)
    with open(skill_file, "w", encoding="utf-8") as f:
        f.write(skill_content)
    return created


def _is_zed_directory(target_path: str) -> bool:
    """Returns True if the target path is a Zed configuration folder."""
    return os.path.basename(os.path.normpath(target_path)) == ".zed"


def _merge_existing_settings(existing_data: dict, new_data: dict, is_zed: bool = False) -> dict:
    """
    Merges MCP configuration into existing settings preserving unrelated keys.
    Uses 'context_servers' for Zed and 'mcpServers' for all other editors.
    """
    merged = dict(existing_data)
    key = "context_servers" if is_zed else "mcpServers"
    raw_incoming = new_data.get("mcpServers", new_data.get("context_servers", {}))

    if is_zed:
        incoming_servers = {}
        for server_name, server_cfg in raw_incoming.items():
            if isinstance(server_cfg, dict):
                zed_cfg = dict(server_cfg)
                if "command" in zed_cfg and zed_cfg["command"] == "django-ai-boost":
                    zed_cfg["command"] = "uv"
                    zed_cfg["args"] = ["run", "django-ai-boost"] + zed_cfg.get("args", [])
                incoming_servers[server_name] = zed_cfg
            else:
                incoming_servers[server_name] = server_cfg
    else:
        incoming_servers = raw_incoming

    current_servers = merged.get(key, {})
    if not isinstance(current_servers, dict):
        current_servers = {}

    current_servers.update(incoming_servers)
    merged[key] = current_servers

    if is_zed and "mcpServers" in merged:
        del merged["mcpServers"]

    return merged


def _merge_or_create_settings(target_path: str, settings_content: str) -> bool:
    """
    Creates or merges the settings.json file inside the target directory.
    """
    os.makedirs(target_path, exist_ok=True)
    settings_file = os.path.join(target_path, "settings.json")
    is_zed = _is_zed_directory(target_path)

    try:
        new_data = json.loads(settings_content)
    except json.JSONDecodeError:
        new_data = {}

    if not os.path.exists(settings_file):
        final_data = _merge_existing_settings({}, new_data, is_zed=is_zed)
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=2)
            f.write(chr(10))
        return True

    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            if not isinstance(existing_data, dict):
                existing_data = {}
    except (json.JSONDecodeError, OSError):
        existing_data = {}

    merged_data = _merge_existing_settings(existing_data, new_data, is_zed=is_zed)

    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=2)
        f.write(chr(10))

    return False


def ensure_ai_structure(base_dir: str, context_data: dict) -> tuple[list[str], bool, bool]:
    """
    Discovers AI assistant directories and ensures they have the latest
    SKILL.md and settings.json configurations.
    """
    skill_tpl = get_template_content("SKILL.md.tpl")
    settings_tpl = get_template_content("settings.json.tpl")

    engine = Engine()
    ctx = Context(context_data)
    rendered_skill = engine.from_string(skill_tpl).render(ctx)
    rendered_settings = engine.from_string(settings_tpl).render(ctx)

    targets = _get_target_directories(base_dir)
    skill_created_any = False
    settings_created_any = False

    for target in targets:
        skill_created = _write_skill_file(target, rendered_skill)
        if skill_created:
            skill_created_any = True

        settings_created = _merge_or_create_settings(target, rendered_settings)
        if settings_created:
            settings_created_any = True

    return targets, skill_created_any, settings_created_any
