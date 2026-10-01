---
name: django-testing
description: Write or diagnose Django regression tests for models, forms, views, permissions, query behavior, transactions, tasks, and server-rendered interactions. Use for focused testing work or evaluating behavior that spans HTML and the browser; not a trigger to run the full suite for every edit.
metadata:
  version: "1.0.0"
---

# Django testing

Test an observable contract, including how it can fail. Read the relevant code,
existing tests and repository test instructions before choosing tools or fixtures.
Examples use django.test and the focused Django runner. Follow the repository's
approved runner; an incidental dependency does not authorize a runner migration.

## Choose what proves the change

1. Identify the input, visible result and failure mode. Include access denied,
   invalid input, empty input and rollback when they matter to this change.
2. Use SimpleTestCase for no-database behavior, TestCase for isolated ORM/HTTP work,
   and TransactionTestCase when real commit/locking semantics are required.
3. Keep test data small but discriminating: two different users/tenants, another
   object's identifier, multiple related rows, or a privileged field in a payload.
4. Assert state after mutations and negative requests, not just a status code.
   Avoid tests that only match the wording or reproduce the implementation.
5. Execute the corresponding test module. Diagnose failures in scope; do not change
   unrelated code or weaken assertions to obtain a pass.

## Reference routing

- HTTP, permissions, query counts, transactions, tasks:
  [Django runner patterns](references/django-runner.md).
- HTMX/Alpine/Tailwind interaction and empirical skill evaluation:
  [Browser and evaluation cases](references/browser-cases.md).
- Project boundaries or isolated source-slice checks:
  [Project integration](references/project-integration.md).

## Essential distinctions

- The default Django Client disables CSRF checks. A passing POST test alone does
  not prove CSRF; use Client(enforce_csrf_checks=True) for that contract.
- A rendered fragment test does not prove the browser performed a swap or retained
  focus. Use browser execution for JavaScript behavior and compiled CSS for styling.
- Bind POST even when empty; regression tests should send an empty dictionary when
  that case can be confused with GET/unbound form handling.
- Assert access control for both full-page and fragment requests. A hidden button
  is not authorization. Test that rejected writes leave the object unchanged.
- `TestCase` normally rolls back instead of committing. Capture/execute on_commit
  callbacks explicitly or use real transactions as required by the test.
- Patching a task method is not proof that rollback suppresses the callback. Exercise
  both commit and rollback boundaries when that is the behavior being changed.
- Test query growth with representative related data; derive the count from the
  query contract, not from a universal number. Include template rendering.

Add regression tests for changed behavior and follow the repository's coverage and
complexity requirements. For the native runner, use
`python manage.py test app.tests.test_module` for the focused module. Use the
project's wrappers/flags where required and run broader gates when its contract
requires them. Do not weaken governance or coverage checks to hide failures.
Report commands, results and any unverified browser/database behavior precisely.
