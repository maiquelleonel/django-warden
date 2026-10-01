"""Distribute packaged companion guides without rendering their code examples."""

import hashlib
import json
import logging
import os
import stat
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)
SKILL_SOURCE = Path(__file__).with_name("skills")
MANIFEST_NAME = ".django-warden.json"


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _write_atomic(path: Path, content: bytes) -> None:
    path = path.resolve()
    temporary = tempfile.NamedTemporaryFile(dir=path.parent, delete=False)
    try:
        with temporary:
            temporary.write(content)
        mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
        os.chmod(temporary.name, mode)
        os.replace(temporary.name, path)
    finally:
        Path(temporary.name).unlink(missing_ok=True)


def _read_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    hashes = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(hashes, dict):
        raise ValueError("Invalid skill ownership manifest")
    return hashes


def _check_destination(path: Path, base_dir: Path, content: bytes, previous_hash: str | None) -> None:
    if not path.resolve().is_relative_to(base_dir):
        raise ValueError(f"Skill path escapes the project: {path}")
    if path.exists():
        current = path.read_bytes()
        if current != content and _digest(current) != previous_hash:
            raise ValueError(f"Preserving locally maintained skill file: {path}")


def _install_skill(source: Path, destination: Path, base_dir: Path) -> bool:
    manifest = destination / MANIFEST_NAME
    if not manifest.resolve().is_relative_to(base_dir):
        raise ValueError(f"Skill manifest escapes the project: {manifest}")
    hashes = _read_manifest(manifest)
    files = {path.relative_to(source).as_posix(): path.read_bytes() for path in sorted(source.rglob("*.md"))}
    for name, content in files.items():
        _check_destination(destination / name, base_dir, content, hashes.get(name))

    created = False
    for name, content in files.items():
        path = destination / name
        existed = path.exists()
        path.parent.mkdir(parents=True, exist_ok=True)
        if not existed or path.read_bytes() != content:
            _write_atomic(path, content)
        created |= not existed
    manifest.parent.mkdir(parents=True, exist_ok=True)
    hashes.update({name: _digest(content) for name, content in files.items()})
    manifest_content = json.dumps(hashes, indent=2) + "\n"
    if not manifest.exists() or manifest.read_text(encoding="utf-8") != manifest_content:
        _write_atomic(manifest, manifest_content.encode("utf-8"))
    return created


def install_companion_skills(base_dir: str, targets: list[str]) -> bool:
    """Refresh unmodified managed files; preserve conflicting skills with a warning."""
    project = Path(base_dir).resolve()
    created = False
    destinations = {(project / target / "skills").resolve() for target in targets}
    for destination in sorted(destinations):
        for entrypoint in sorted(SKILL_SOURCE.glob("*/SKILL.md")):
            source = entrypoint.parent
            try:
                created |= _install_skill(source, destination / source.name, project)
            except (OSError, ValueError) as exc:
                logger.warning("Could not refresh companion skill %s: %s", source.name, exc)
    return created
