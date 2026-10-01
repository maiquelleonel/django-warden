# 🛡️ django-warden

An opinionated AI skill, watchdog, and custom system checks framework to scale Django projects from zero to millions of users.

`django-warden` ensures that human developers and Gemini CLI assistants write clean, performant, and secure Django code. It combines static LLM instructions (the Warden Skill) with dynamic, active Django system checks and Model Context Protocol (MCP) tooling, embodying battle-tested industry guidelines.

## 🚀 Features

- **Example App:** Check out [gpurent](https://github.com/maiquelleonel/gpurent), a production-grade Django example project configured with `django-warden` demonstrating thin views, service layers, and zero-N+1 active auditing.
- **Active System Checks:** Detects missing database indexes on common search/lookup fields and dangerous infinite recursive signal save loops (Windmill loops) at startup.
- **Windmill Loop Protection:** Provides a `@prevent_windmill_loops` decorator to safely handle internal signals.
- **AI Skill Integration:** Comes pre-packaged with an AI System Prompt (`SKILL.md`) that teaches the Gemini CLI assistant how to write code according to "The Django Way."
- **First-Class MCP Integration:** Fully compatible with `django-ai-boost` (for framework introspection) and `codebase-memory-mcp` (for advanced codebase graph-based memory), enabling the Gemini CLI assistant to run architectural integrity audits instantly and perform high-precision semantic searches. You can visualize and navigate your project's codebase graph using the companion web UI [codebase-memory-mcp-ui](https://github.com/DeusData/codebase-memory-mcp-ui).

## 🧩 Opinionated Architecture Philosophy

`django-warden` is designed to guide a Django project from **day zero to millions of clients**, enforcing architectural boundaries that keep codebases decoupling-friendly, highly testable, and robust under scale:

- **Lean Models & Thin Views:** Views should only handle HTTP concerns. Models should only handle data structure and simple properties.
- **Services vs. Orchestrators (SOLID):**
  - `services/` contains pure, third-party API protocol wrappers (e.g. Stripe, WhatsApp API) with no local business logic.
  - `orchestrators/` (or `use_cases/`) houses multi-model business workflows, transactions, and complex state machines.
- **Anti-God Objects:** Actively prevents models and views from accumulating unrelated features, facilitating transition to DRF or Django Ninja seamlessly.
- **Proactive AI Consent:** Instructs AI assistants to collaborate through explicit interactive verification and gain developer approval before mutating code.

## 📦 Installation & Setup

1. Add `django-warden` to your project dependencies:

```bash
uv add django-warden
```

2. Add `"django_warden"` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "django_warden",
]
```

3. Run the architectural audit:

```bash
python manage.py warden_audit
# or: uv run python manage.py warden_audit
```

✨ **Zero-Config AI Setup:** Running `warden_audit` (or starting the development server with `DEBUG = True`) automatically provisions the Warden Skill (`SKILL.md`) and configures the Model Context Protocol (MCP) integrations in both `.gemini/` and `.claude/` directories. On your next session with Gemini CLI, Claude Code, or compatible AI agents, the skill and tools will be immediately active and ready to enforce "The Django Way"!

## Companion Django skills

The package also distributes six focused guides, with their supporting references:

- `django-backend`: app ownership, validation, queries, transactions and workflows.
- `django-templates`: DTL, shared UI, Admin overrides, accessible forms and Tailwind.
- `django-htmx`: full-page/fragment contracts, forms, swaps, events and history.
- `alpinejs-django`: local UI state, lifecycle, CSP and keyboard/focus behavior.
- `django-web-security`: authorization, CSRF, XSS, CSP, uploads and private caching.
- `django-testing`: focused Django tests, transaction evidence and browser verification.

Their maintained source is `django_warden/skills/`, included in both wheel and
source distributions. Bootstrap copies Markdown literally, including Django/HTML
examples and license notices. Django 6 features in the guides are version-gated;
installing the catalog does not add HTMX, Alpine, Tailwind or a task backend.

The catalog uses the existing assistant-directory discovery. Existing hidden
directories containing `skills/` are detected, including `.agents/` and `.codex/`;
directories with `settings.json` are also detected, potentially including `.vscode/`.
An empty project still defaults to `.gemini/` and `.claude/`. Shared skill symlinks
inside the project are preserved and their resolved destination is processed once.
Companion files resolving outside the project are skipped with a warning.
Assistant activation and MCP configuration compatibility depend on the client;
this extension does not change the existing settings-generation behavior.

After upgrading the package, run `python manage.py warden_audit` (or use the normal
DEBUG bootstrap) to refresh the catalog. An unchanged managed file is updated
using its recorded hash in `<skill>/.django-warden.json`. Repeated runs leave
identical bytes and modification times intact. If a same-named skill has different
unmanaged content, a local edit, or an invalid ownership manifest, the whole
companion skill is preserved and a warning identifies the conflict. Other skills
continue to install. This protection applies to the new companions; the existing
core `django-warden/SKILL.md` keeps its established overwrite behavior.

Keep project policy in a separate local skill and the repository's active
instructions. Before adopting a companion over an existing custom copy, review
the differences, retain local rules in that separate skill, and move the old
directory to a backup outside the discovered skill folders. Bootstrap then creates
a managed copy. Identical existing package files can be adopted automatically.
Extra local files and files removed from a later package are not deleted; review
obsolete references manually during upgrades. Their previous hashes remain recorded
so a later release can safely reintroduce an unchanged file. Missing files still in
the package are restored. Files are replaced atomically; a failed write is logged
and bootstrap can be retried after resolving the error. The entire multi-file
upgrade is not a transaction. Replacement preserves existing file permissions;
new public package documentation uses mode 0644 on POSIX systems.

Each adapted skill retains its attribution and full license notice in
`references/upstream-license.md`.

## 🤖 Global Installation (Optional)

If you want the skill available globally across all your projects on your machine (without installing the package in each one), you can copy or download `SKILL.md` directly into your global agent folder:

```bash
# Global setup for Gemini CLI
mkdir -p ~/.gemini/skills/django-warden
curl -fsSL https://raw.githubusercontent.com/maiquelleonel/django-warden/master/SKILL.md -o ~/.gemini/skills/django-warden/SKILL.md

# Global setup for Claude Code
mkdir -p ~/.claude/skills/django-warden
curl -fsSL https://raw.githubusercontent.com/maiquelleonel/django-warden/master/SKILL.md -o ~/.claude/skills/django-warden/SKILL.md
```

Or if you have this repository cloned locally:

```bash
mkdir -p ~/.gemini/skills/django-warden && cp SKILL.md ~/.gemini/skills/django-warden/SKILL.md
```

## 📜 License

MIT License.
