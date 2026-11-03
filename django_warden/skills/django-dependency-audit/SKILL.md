---
name: django-dependency-audit
description: Audit, secure, and manage Python & Django supply-chain dependencies using pip-audit, uv, and pyproject.toml configuration. Use when checking for package vulnerabilities (CVEs), managing ignore lists, or performing safe dependency upgrades.
metadata:
  version: "1.0.0"
---

# Django Dependency Audit & Supply Chain Security

Guide and automate the auditing of Python and Django dependencies against known Common Vulnerabilities and Exposures (CVEs) and PyPI/OSV advisories, providing safe upgrade paths and auditable ignore lists.

## 🔒 Core Principles

1. **Deterministic Resolution via uv:** Always audit the resolved dependency tree using `uv export --no-hashes --format requirements-txt` piped into `pip-audit`. Avoid auditing unpopulated or isolated venvs without `pip`.
2. **Version-Controlled Ignore Lists:** Never ignore CVEs silently or via uncommitted CLI flags. Manage exceptions declaratively in `pyproject.toml` under `[tool.audit]`.
3. **Actionable Remediation Guidance:** When vulnerabilities are detected, clearly guide developers between updating packages (`just upgrade`) or registering a documented exception (`just audit-ignore`) if no upstream patch exists.
4. **Shift-Left Security:** Integrate dependency auditing into local pre-commit hooks and GitHub Actions CI before running unit tests.

---

## 🛠️ Architecture & Setup

### 1. `pyproject.toml` Configuration

Declare known exceptions with reasoning comments:

```toml
[tool.audit]
ignore-vulns = [
    "PYSEC-2026-2450", # django-mdeditor (no upstream patch available)
]
```

### 2. Standalone Audit Script (`scripts/audit.py`)

```python
import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path

PYPROJECT_PATH = Path("pyproject.toml")


def load_ignored_vulns() -> list[str]:
    if not PYPROJECT_PATH.exists():
        return []
    with open(PYPROJECT_PATH, "rb") as f:
        data = tomllib.load(f)
    return data.get("tool", {}).get("audit", {}).get("ignore-vulns", [])


def run_audit() -> int:
    ignored = load_ignored_vulns()
    ignore_args = []
    for vuln_id in ignored:
        ignore_args.extend(["--ignore-vuln", vuln_id])

    export_proc = subprocess.Popen(
        ["uv", "export", "--no-hashes", "--format", "requirements-txt"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    audit_cmd = ["uvx", "pip-audit", *ignore_args, "-r", "/dev/stdin"]
    audit_proc = subprocess.run(audit_cmd, stdin=export_proc.stdout)
    export_proc.stdout.close()
    export_proc.wait()

    if audit_proc.returncode != 0:
        print("
" + "=" * 70)
        print("🚨 VULNERABILIDADES DE SEGURANÇA ENCONTRADAS NAS DEPENDÊNCIAS!")
        print("=" * 70)
        print("Como resolver:")
        print("  1. Atualizar o pacote vulnerável para a versão corrigida (Fix Version):")
        print('     👉 just upgrade "<nome_do_pacote>==<versao_segura>"')
        print('     Exemplo: just upgrade "urllib3>=2.8.0"
')
        print("  2. Se o pacote ainda NÃO possui correção upstream disponível:")
        print("     👉 just audit-ignore <ID_DA_CVE>")
        print("     Exemplo: just audit-ignore PYSEC-2026-2450")
        print("=" * 70 + "
")

    return audit_proc.returncode


def add_ignored_vuln(vuln_id: str) -> int:
    if not PYPROJECT_PATH.exists():
        print(f"❌ {PYPROJECT_PATH} não encontrado.")
        return 1

    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    if f'"{vuln_id}"' in content:
        print(f"⚠️  {vuln_id} já está presente no {PYPROJECT_PATH}")
        return 0

    pattern = r"(\[tool\.audit\]\s*
\s*ignore-vulns\s*=\s*\[)"
    replacement = rf'
    "{vuln_id}",'
    new_content = re.sub(pattern, replacement, content)

    if new_content == content:
        print("❌ Seção [tool.audit] não encontrada no pyproject.toml")
        return 1

    PYPROJECT_PATH.write_text(new_content, encoding="utf-8")
    print(f"✅ Adicionado {vuln_id} a [tool.audit.ignore-vulns] no {PYPROJECT_PATH}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditoria de dependências e gerenciamento de CVEs ignoradas.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="Executa auditoria via pip-audit com base no pyproject.toml")

    ignore_parser = subparsers.add_parser("ignore", help="Adiciona ID de CVE ignorada ao pyproject.toml")
    ignore_parser.add_argument("vuln_id", help="ID da vulnerabilidade (ex: PYSEC-2026-2450)")

    args = parser.parse_args()

    if args.command == "check":
        sys.exit(run_audit())
    elif args.command == "ignore":
        sys.exit(add_ignored_vuln(args.vuln_id))


if __name__ == "__main__":
    main()
```

### 3. `Justfile` Recipes

```just
# Auditoria de segurança de dependências (CVEs) respeitando [tool.audit] do pyproject.toml
audit:
    uv run --no-sync python scripts/audit.py check

# Adiciona um ID de vulnerabilidade à lista ignore-vulns do pyproject.toml
audit-ignore vuln_id:
    uv run --no-sync python scripts/audit.py ignore {{ vuln_id }}
```

### 4. Integration with Pre-commit & CI

- **`.pre-commit-config.yaml`:**
  ```yaml
  - repo: local
    hooks:
      - id: audit
        name: Dependency security audit (pip-audit & [tool.audit])
        entry: uv run --no-sync python scripts/audit.py check
        language: system
        pass_filenames: false
        always_run: true
  ```

- **GitHub Actions (`.github/workflows/ci.yml`):**
  ```yaml
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup uv with Cache
        uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"
      - name: Run Dependency Audit
        run: uv run --no-sync python scripts/audit.py check
  ```
