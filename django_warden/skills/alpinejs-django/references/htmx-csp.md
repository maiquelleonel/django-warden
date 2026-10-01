# HTMX Integration, Lifecycle, and CSP Reference

Reference Date: 2026-09-08
Sources:
- Alpine.js CSP: https://alpinejs.dev/advanced/csp
- Alpine.js Lifecycle and Alpine.data: https://alpinejs.dev/globals/alpine-data
- HTMX Documentation: https://htmx.org/docs/

## Shell Boundaries and HTMX Swaps

To prevent losing client-side UI state during HTMX updates, keep the Alpine component root
outside the target element that HTMX replaces:

```html
<div x-data="{ filterOpen: false }">
  <button type="button" @click="filterOpen = !filterOpen" :aria-expanded="filterOpen.toString()">
    Toggle Filters
  </button>

  <!-- Real form element triggering HTMX request -->
  <form id="filters" hx-get="{% url 'people:candidate-list' %}" hx-target="#results-target" hx-trigger="change">
    <input type="text" name="q" placeholder="Search candidates...">
  </form>

  <!-- HTMX swaps only the inner content -->
  <div id="results-target">
    {% include "people/_candidate_list.html" %}
  </div>
</div>
```

When HTMX inserts swapped markup containing `x-data`, Alpine initializes the new elements
automatically via DOM mutation observers. Do not call `Alpine.start()` after swaps.

## Component Lifecycle and Listener Cleanup

When components attach global event listeners or timers, declare them via `Alpine.data()` and
use the `init()` and `destroy()` lifecycle hooks:

```javascript
document.addEventListener('alpine:init', () => {
  Alpine.data('filterController', () => ({
    activeFilter: 'all',
    _handler: null,
    init() {
      this._handler = (e) => this.handleExternalUpdate(e);
      window.addEventListener('resize', this._handler);
    },
    destroy() {
      if (this._handler) {
        window.removeEventListener('resize', this._handler);
      }
    },
    handleExternalUpdate(e) {
      // response logic
    }
  }));
});
```

Avoid using `$cleanup` inside template `x-init` blocks; cleanup callbacks are part of the directive
extension API (`Alpine.directive`), not the standard component scope.

## Event Communication Between Django, HTMX, and Alpine

### 1. Server to Alpine via HX-Trigger
Custom event names must match exactly between the server header and the client listener:
```python
# Django view response
response = render(request, "people/_status_badge.html", {"status": "active"})
response["HX-Trigger"] = "candidate-updated"
return response
```
In Alpine template:
```html
<div x-data="{ notified: false }" @candidate-updated.window="notified = true">
```
Custom event names do not automatically convert between camelCase and kebab-case.

### Sibling components

A trigger outside the modal's x-data cannot access its methods. For independent
scopes, the trigger can use its own `x-data` and dispatch a named event with the
object/trigger identifier; the persistent modal listens with `.window`. Both sides
must exist and use exactly the same event name. A bare `@click="open()"` on an
unscoped row will not call a method declared only on a sibling modal.

### 2. HTMX Lifecycle Events
Identify the installed HTMX version. The following names apply to 1.9/2.x;
check the matching version documentation before using them with a different major. In HTML template attributes, use
kebab-case listeners (`@htmx:after-swap.window` or `@htmx:after-settle.window`), as HTML attributes
are case-insensitive. HTMX v1.9 supports kebab-case variants.

## Content Security Policy (CSP) Compliance

Strict CSP environments disallow `unsafe-eval`, preventing Alpine's default runtime from
compiling arbitrary inline expressions:

- **Build Requirement**: Use `@alpinejs/csp` instead of the standard build.
- **Expression Syntax**: `@alpinejs/csp` supports a defined subset of inline expressions (for example simple lookups
  and method invocations; nested property assignments may be unsupported). Verify supported syntax against official CSP docs.
- **Reusability**: Use `Alpine.data()` to encapsulate component logic in registered scripts rather than
  relying on complex inline template expressions.

## Data Security and XSS Protection

- Use Django's `json_script` to safely embed data into `<script type="application/json">` tags.
- While `json_script` prevents script-tag breakout at render time, it does not guarantee safe display
  once parsed by JavaScript. Always display dynamic strings with `x-text` rather than injecting unescaped HTML.

## Focus Management and Interactive Verification

- When opening an overlay or modal, record the triggering element:
  `this.lastFocused = document.activeElement`.
- When closing via Escape or backdrop click, return focus: `this.lastFocused?.focus()`.
- If a save replaces the row containing the original trigger, that element becomes
  detached. Retain a stable trigger ID and resolve the new element after the swap
  before focusing it; do not rely only on the old DOM reference. Coordinate event
  timing with the actual HTMX response contract.
- Verify modal focus retention and keyboard navigation in an interactive browser session; Django unit
  tests only validate rendered markup.
