# Shared UI Components and Partials Reference

Reference Date: 2026-09-08
Sources:
- Django 6.0 Template Partials: https://docs.djangoproject.com/en/6.0/ref/templates/language/#template-partials
- Django 6.0 Built-in Tags and Filters: https://docs.djangoproject.com/en/6.0/ref/templates/builtins/#include
- Django 6.0 json_script: https://docs.djangoproject.com/en/6.0/ref/templates/builtins/#json-script

## Component Locality and Boundaries

In multi-app architectures (such as `orders` and `catalog`), maintain clean domain locality:
1. **App-Specific Partials**: Keep templates inside their owning app (`catalog/templates/catalog/_item_card.html`).
2. **Generic Components**: Store domain-agnostic UI primitives (buttons, modals, badges) in `templates/components/`.
3. **Explicit Shared Owner**: Start with shared templates when sufficient. A focused
   UI app may own reusable tags/assets/components when justified; do not introduce
   a generic core app or move domain identities solely because markup is shared.

## Django 6 Native Partials vs. Includes

Determine whether the project is running Django 6+ before using native partials:

### 1. Django 6 Native Partials
Django 6 introduces built-in template partials directly in DTL without third-party packages.
Do not use `{% load partials %}` (which belongs to external packages), and do not pass `inline=True`:

```html
<div id="candidate-list">
  {% partialdef candidate_row inline %}
    <div class="py-2 border-b" id="candidate-{{ candidate.id }}">
      <span class="font-medium">{{ candidate.name }}</span>
    </div>
  {% endpartialdef %}
</div>

<!-- For a separate fragment response, render this template with #candidate_row. -->
```

### 2. Standard Includes with Context Isolation
When building reusable component includes, use `only` to prevent unintended variable leakage:
```html
{% include "components/_modal.html" with title="Confirm Action" id="confirm-modal" only %}
```

**Context Isolation:** `only` does not automatically inherit values supplied by outer
context processors, such as request or csrf_token. Those processors may still have
run for the outer render. Pass required values explicitly when rendering forms:
```html
{% include "components/_form_dialog.html" with form=form csrf_token=csrf_token action_url=submit_url only %}
```

## Form Accessibility Standards

Reusable form markup must adhere to accessibility standards:
- **Explicit Labels:** Pair inputs with `<label for="{{ field.id_for_label }}">`.
- **Error Binding:** Render `field.errors` associated via `aria-describedby="{{ field.auto_id }}_error"`.
- **Help Text:** Connect `field.help_text` via `aria-describedby` when present.
- **Unique Identifiers:** When rendering components in loops, append unique IDs: `id="action-menu-{{ item.id }}"`.

## ORM Query Prevention and Lazy Evaluation

While querysets passed from views evaluate lazily upon loop iteration in DTL, avoid secondary queries:
- Avoid properties that hide database queries; preserve stricter repository rules about model `@property`.
- Prepare all necessary relations in views using `select_related` and `prefetch_related`.
- Inspect total query count across full page rendering to ensure zero N+1 queries.

## Safe Client Data Serialization

Pass server-side data to client scripts using Django's `json_script`:
```html
{{ candidate_data|json_script:"candidate-data" }}
```
`json_script` escapes characters like `<` and `>` to prevent `<script>` breakout. However, it does not guarantee universal XSS immunity once parsed on the client; downstream JavaScript must always render text using safe DOM APIs or `x-text`.
