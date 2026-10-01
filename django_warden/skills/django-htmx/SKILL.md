---
name: django-htmx
description: Implement or debug Django HTML interactions using HTMX, including form submissions, partial responses, search, pagination, swaps, polling, history and response events. Use for the server/browser interaction contract, not a general template redesign or client-only toggle.
license: MIT
metadata:
  version: "1.0.0"
  source: https://github.com/LVTD-LLC/skills/tree/main/skills/django-htmx
---

# Django and HTMX

Keep Django in charge of authorization, validation and durable state. HTMX requests
HTML and updates the relevant DOM; Alpine handles local state. Read the affected
view, templates and loaded client version before implementing an interaction.

## Read the relevant reference

- Forms, representation selection, redirects: [view patterns](references/django-view-patterns.md).
- Targets, events, history and Alpine: [interaction patterns](references/template-interaction-patterns.md).
- Security and regression evidence: [testing](references/testing-security.md).

## Per-interaction workflow

1. Define the normal browser path and the enhanced path: request method, URL,
   permission scope, valid/invalid response and the element receiving that response.
2. Reuse the existing endpoint when permissions/data are the same. Use a dedicated
   endpoint if the operation has a distinct contract; avoid a catch-all dispatcher.
3. Run authentication and scoped object access before branching on HX-Request.
   The header is controlled by the caller and is not an authorization signal.
4. Bind Forms on POST even with empty data. Use the same validation for both paths.
   Include request.FILES for uploads; never infer POST from whether data is truthy.
5. Return the correct HTML shape. An outerHTML response must preserve the intended
   root/ID. A full page and its fragment should reuse the same presentation source.
6. Keep real method/action/href values for the required non-JavaScript path.
   Targets must also exist when a reusable form is served as a complete page.
7. Verify full/fragment responses and browser interaction, including invalid input,
   repeated swaps, permission denial and any history/focus behavior.

## Integration and versions

- In native Django, compare request.headers.get("HX-Request") with "true". Header
  presence alone is insufficient. django-htmx's request.htmx and HTTP helpers are
  conditional on the dependency/middleware actually being present.
- Discover script version per page, including Admin Media and template includes;
  do not migrate or assume the same version everywhere without checking.
- For 1.9/2.x defaults, render an invalid form with 200 unless error-status swapping
  is explicitly configured. Other versions/configurations can differ.
- The browser follows HTTP 3xx transparently: HX headers on that intermediate
  response are not processed by HTMX, while headers on the final response are.
  Choose the redirect strategy deliberately.
- Add Vary: HX-Request when the same cacheable URL varies by representation.
  This does not isolate private data; choose the appropriate cache policy too.
- Preserve CSRF and escaping in every feature, without requiring a security skill.
  Do not return user-controlled hx-* attributes or executable HTML unsanitized.
- Bind event listeners once, stop polling when complete and debounce frequent input.
  Do not restart Alpine after a swap or replace its persistent state owner.

Do not assume a starter layout, existing npm script, csrf bootstrap, or extra
skills that are not supplied. Optional django-web-security deepens a security
review; django-testing deepens testing. Neither is required to apply these rules.

Upstream attribution: [license notice](references/upstream-license.md).
