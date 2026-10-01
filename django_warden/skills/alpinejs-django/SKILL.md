---
name: alpinejs-django
description: Use when adding, refactoring, or debugging Alpine.js ephemeral client state in Django templates, coordinating with HTMX swaps, CSP compliance, and keyboard accessibility.
license: MIT
metadata:
  source: https://github.com/LVTD-LLC/skills/tree/main/skills/alpinejs-django
  version: "1.0.0"
  displayName: Alpine.js Django
  category: Frontend
  tags: alpinejs,django,frontend,htmx,csp
---

# Alpine.js with Django and HTMX

Use this skill for local, ephemeral browser state in Django-rendered templates (dropdowns,
modals, tabs, disclosures, client toggles). Django views and models remain the source of
truth for data and authorization; HTMX manages server requests and DOM swaps.

## Resource Routing

Consult [HTMX and CSP](references/htmx-csp.md) when:
- Coordinating Alpine state across HTMX swap targets or handling `HX-Trigger` events.
- Configuring component lifecycle (`init()` and `destroy()`) under DOM replacement.
- Enforcing Content Security Policy (CSP) compliance without `unsafe-eval`.

## Architecture and State Boundaries

- **Django**: Owns data persistence, session authorization, business rules, and HTML generation.
- **HTMX**: Owns network requests, server round trips, and replacing DOM fragments.
- **Alpine**: Owns transient client-side UI state (e.g., menu open/close, client filters).

Keep persistent Alpine components outside of HTMX replacement targets to prevent state resets.
An event handler must be inside an Alpine scope that owns the referenced method.
A row beside a modal cannot call that modal's `open()` directly. Give the trigger
its own scope and dispatch an explicit event, or use an existing shared ancestor.

## Component Initialization and Lifecycle

- Inspect how Alpine is loaded. A self-starting CDN build must not be started again;
  a module build needs one explicit start after registrations. Register Alpine.data
  before start (or in alpine:init before the CDN script runs).
- Keep dynamic IDs unique when components/json_script nodes repeat on a page.

- Alpine initializes elements containing `x-data` automatically on DOM insertion. Do not call
  `Alpine.start()` inside HTMX event callbacks.
- For components requiring custom setup or event cleanup, register reusable components via
  `Alpine.data()` and implement standard `init()` and `destroy()` methods.
- Note: `$cleanup` is not a standard API in `x-init`; component cleanup should be handled in `destroy()`.

## Core Directives

- `x-show`: Toggles CSS `display: none` for frequent visibility changes while preserving DOM presence.
- `x-if`: Use on `<template x-if="...">` when elements must be conditionally mounted/unmounted.
- `x-text`: Always use `x-text` for rendering dynamic strings.
- `x-cloak`: Apply to elements hidden by default to prevent pre-init flickering. Ensure
  `[x-cloak] { display: none !important; }` is included in the base CSS.

## Data Passing from Django

- Never output raw user data with `|safe` inside Alpine attributes.
- For scalar configuration, read from data attributes:
  `<div data-limit="{{ page_size }}" x-data="{ limit: Number($el.dataset.limit) }">`
- For structured data, serialize with Django's `json_script` and read the JSON node in `init()`.

## Accessibility and Verification

- Use native `<button type="button">` triggers; bind `:aria-expanded` and `:aria-controls`.
- Dismiss overlays with `@keydown.escape.window` and `@click.outside`.
- Restore focus to the trigger element when closing modals or popovers.
- Preserve any public DOM hooks on the specified element type: an input ID belongs
  on the input, not its surrounding div. Verify hooks against rendered DOM before
  relying on them in events or browser tests.
- Automated Django tests cover HTML markup; interactive behaviors (focus traps, Escape closing)
must be verified in an active browser session.

Upstream attribution: [license notice](references/upstream-license.md).
