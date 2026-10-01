---
name: django-backend
description: Design Django app boundaries and implement or review models, querysets, forms, transactions, signals, and business workflows. Use for backend decisions and changes, including multi-app ownership and scheduled work. Complements the generated django-warden; not a frontend layout or general infrastructure guide.
metadata:
  version: "1.0.0"
---

# Django backend

Use Django's native data and validation mechanisms, with the existing repository
contract governing local architecture. Read the file to change before editing.
Preserve unrelated behavior and work within the authorized task.
When the task asks for architecture review, current conventions are reviewable.
Distinguish what the code does, what the contract requires and what you recommend;
do not treat a proposed pattern as already adopted. An ordinary code change does
not implicitly authorize that wider review or a repository-wide refactor.

## Choose the relevant reference

- App ownership, dependencies, cross-app workflows: [architecture](references/architecture.md).
- Reviewing standards or long-term structure: [evolution](references/evolution.md).
- Query behavior, writes, concurrency, signals and tasks: [data integrity](references/data-integrity.md).
- Project-specific constraints: read the consuming repository's instructions and
  local companion skills. Do not impose another project's conventions.

## Implementation decisions

1. Identify the data owner and the permission boundary. Reuse the existing app,
   model and request path when the task fits; do not reorganize apps for a field change.
2. Use Forms/ModelForms for HTML input and DRF Serializers for API input. Explicitly
   allow writable fields and assign ownership from authenticated context.
   Django `form.is_valid()` takes no `raise_exception`; DRF's method can.
3. Put reusable database expressions in QuerySets/Managers. Load only relationships
   actually consumed, using `select_related`/`prefetch_related` appropriately.
   Measure query behavior; do not require the same query count for every view.
4. Scope object reads and mutations using the actual permission policy and model
   relationships, including related-object choices and admin paths. Do not invent
   a user/tenant field to fit an example; identify a missing policy explicitly.
5. Persist local invariants and coordinate multi-step changes at the proper boundary.
   Select atomic transactions, database constraints or conditional updates according
   to the failure/concurrency case; none is a universal replacement for the others.
6. Keep external protocols outside data models. Set timeouts, use settings for
   credentials and schedule side effects after the commit when required.
7. Test the changed behavior and relevant failure cases using the repository runner.
   For dedicated test work, `django-testing` provides deeper patterns if available;
   completing ordinary changes does not depend on another skill being installed.

## Easy-to-miss behavior

- Bind a form on POST even when its data is empty. Include `request.FILES` for uploads.
- `Model.save()` does not automatically call `full_clean()`. Choose and test the
  validation boundary instead of assuming a database write validates every field.
- `update_fields` limits written columns; it does not prevent concurrent lost updates.
  Include fields whose `pre_save()` must run, such as an intended `auto_now` update.
- `QuerySet.update()` skips instance `save()` and save signals. `QuerySet.delete()`
  skips an overridden instance `delete()` but emits delete signals and handles cascades.
- A property or template lookup can trigger a query. Supply annotated/prefetched data
  deliberately rather than hiding database access behind presentation attributes.
- Use timezone-aware values through `django.utils.timezone` for application timestamps.
- A callback after commit is not a durable delivery guarantee. Retries/idempotence
  depend on the task's actual delivery contract.

This guide complements `django-warden`. Maintain both in the package source;
bootstrap refreshes distributed copies. Keep project-specific guidance in a
separate local skill and preserve the consuming repository's active contract.
