# Targets, events and history

## Keep an explicit DOM contract

- Give each target one unique ID. outerHTML replaces the target itself; return a
  root with the same intended ID. innerHTML replaces only its children.
- Keep the persistent Alpine state owner outside any replaced element. A trigger
  outside that scope cannot call the owner's methods directly; use an explicit
  event between separate scopes or an existing shared ancestor.
- For a form reused in modal and full-page views, make the enhancement target valid
  in both cases. An hx-target pointing to an absent modal breaks the full-page form.
- Preserve ordinary action/method/href for the required fallback. Include csrf_token,
  and pass csrf_token/form explicitly if an include uses only.
- Return list plus pagination/filter controls together when ordering or totals
  change. OOB updates may update adjacent regions, but do not invent duplicate IDs.

## Events and focus

Custom event names must match exactly in HX-Trigger and the listener. Prefer simple
lowercase names such as profile-saved. Use the version's appropriate immediate,
after-swap or after-settle trigger depending on whether the new DOM is required.

If saving replaces the row containing the opener, the old DOM node is detached.
Remember a stable trigger ID and resolve the new element after the swap before
returning focus. Repeated invalid/successful swaps must not duplicate listeners.
For HTMX 1.9/2.x, kebab-case lifecycle variants work with lowercased HTML attributes;
consult the version's documentation before applying these names to another major.

A server event reports a fact; Alpine changes local UI in response. Do not mirror
the entire server model into a store merely to close a modal.

## History and frequent requests

Use pushed URLs only for navigable state. Direct load, refresh and back/forward
must produce the expected page; handle history-restore requests according to the
loaded HTMX version and current configuration. Do not prescribe a configuration
key across all versions. Avoid storing sensitive fragments in client history;
HTMX 1.9/2.x supports hx-history="false" for this purpose.

Debounce/throttle search inputs where needed. Stop polling on completion, errors
that cannot recover, or when the component is no longer active. A success response
does not universally require an event, and a pending UI does not replace server
idempotence or transaction rules.

## Sources

Checked 2026-09-08:

- [HTMX documentation](https://htmx.org/docs/)
- [HTMX events and response headers](https://htmx.org/reference/)
- [Alpine lifecycle](https://alpinejs.dev/essentials/lifecycle)
