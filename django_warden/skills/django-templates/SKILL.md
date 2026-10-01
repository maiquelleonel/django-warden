---
name: django-templates
description: Use when authoring, organizing, or refactoring Django templates, DTL layouts, native partials, shared UI components, accessible forms, or integrating Tailwind CSS across apps.
license: MIT
metadata:
  source: https://github.com/waldencui/claude-code-django/tree/main/.claude/skills/django-templates
  version: "1.0.0"
  displayName: Django Templates
  category: Frontend
  tags: django,templates,dtl,tailwind,htmx
---

# Django Template Patterns

Use this skill for server-rendered templates using Django Template Language (DTL),
accessible forms, reusable UI elements, and styling with Tailwind CSS. React and JSX
are outside this skill's scope; inspect the actual project stack before choosing it.

## Resource Routing

Consult companion references when handling specialized requirements:
- Read [shared UI](references/shared-ui.md) when designing cross-app shared UI components, building
  accessible form fields, handling isolated contexts (`include ... only`), or using
  Django 6+ template partials.
- Read [Tailwind](references/tailwind.md) when configuring Tailwind scan roots, debugging CSS compilation,
  or inspecting build commands.
- Read [Admin and application UI](references/admin-ui.md) when changing Admin
  overrides, choosing a shared UI owner or introducing process-oriented pages.

## Engine and Version Detection

Before implementing template features, detect the active Django version and template engine
configuration (`TEMPLATES` in settings):
- **Django 6+**: Native template partials (`{% partialdef %}`) are supported built-in.
- **Django 4/5**: Continue using standard `{% include %}` patterns.
- Do not force migration of existing `{% include %}` files to partials.

## Template Organization and Locality

Organize templates by responsibility using the established layout as the starting point:
- `templates/`: Site-wide layouts (`base.html`, error pages).
- `templates/components/`: Generic UI primitives (`_button.html`, `_badge.html`).
- `<app>/templates/<app>/`: App-scoped pages and partials (`orders/`, `catalog/`).

A focused UI app is an option when reusable presentation behavior warrants one;
do not create it merely because two apps share markup. When architecture review
is requested, evaluate alternatives explicitly rather than freezing today's layout.

Example naming conventions; preserve a working local convention unless changing it is in scope:
- Full pages: `list.html`, `detail.html`, `form.html`.
- HTMX/UI partials: prefix with underscore (e.g., `_candidate_rows.html`).

## Layouts, Partials, and Form Context

- Inspect the actual base template blocks; common names include `title`, `content`,
  `extra_head`, and `extra_js`. Do not assume a block exists or create a second bootstrap.
- In Django 6+, define inline reusable blocks with native partials:
  `{% partialdef item_card inline %}...{% endpartialdef %}`
- In includes with isolated context (`{% include "..." with ... only %}`), context processors
  may have run for the outer render, but their values are not inherited automatically
  by the fragment. Pass `form=form` and `csrf_token=csrf_token` explicitly if needed.
- Forms must render semantic labels, `field.errors`, and `field.help_text`.

## ORM Query Prevention

Querysets are evaluated when iterated during template rendering, which is normal.
However, templates must never trigger unexpected secondary queries:
- Do not access database-fetching model properties or methods in templates.
- Shared presentation tags should consume prepared context, avoiding hidden queries.
  If a domain-specific tag needs database access, make its owner/query contract
  explicit and measure rendering; preserve stricter local rules where present.
- Pre-fetch relations in views using `select_related()` and `prefetch_related()` to eliminate N+1 queries.

## Verification

Validate template changes using the repository's declared runner and focused tests.
For Django's native runner: `python manage.py test <app>.tests.<test_module>`.
Use project-specific wrappers and environment flags only when its contract requires
them. Run broader checks when required by that contract or the affected behavior.

Upstream attribution: [license notice](references/upstream-license.md).
