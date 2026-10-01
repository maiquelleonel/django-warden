# Django runner patterns

## HTTP and forms

Use TestCase methods and reverse() for project URLs. The exact response status and
redirect strategy come from the endpoint contract, not a universal test template.

```python
from django.test import Client, TestCase
from django.urls import reverse


class EditTests(TestCase):
    def test_missing_csrf_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.post(
            reverse("tasks:edit", args=[self.task.pk]),
            {"title": "Changed"},
            headers={"HX-Request": "true"},
        )
        self.assertEqual(response.status_code, 403)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Original")
```

This example assumes setUp creates self.user/self.task with title Original. It is
a pattern, not a standalone test to paste without adapting setup and URL names.
Do not use pytest-injected client/user arguments in free functions for this runner.

For a valid CSRF path, retrieve the form and send its token/cookie, respecting the
project's CSRF session/cookie configuration. Test missing or wrong tokens separately.
For authorization, log in a second user, attempt another user's URL and related
object assignment, and verify unchanged database state. Test lists for data leakage.

Test normal and HX requests to the same endpoint when it branches. Compare relevant
HTML semantics with assertContains/assertHTMLEqual or the parsed response. Do not
force template filenames when they are not a public contract. Check bound form
errors on empty POST and missing required fields; include upload data if applicable.

## Queries and writes

Use assertNumQueries around the operation that consumes/render results. Seed more
than one related row; a single object cannot expose N+1 growth reliably. Account
for authentication/session and pagination queries instead of guessing a global count.
Check refresh_from_db after update and failures. For database-specific locking,
run the focused test on the relevant database or explicitly report the limitation.

## Commit and tasks

```python
with self.captureOnCommitCallbacks(execute=True) as callbacks:
    perform_workflow()
self.assertEqual(len(callbacks), 1)
```

Check what the callback did as well as its count. Use a separate rolled-back atomic
scope to verify the callback is discarded. Patch the callable where the workflow
looks it up, not an unrelated import location.

For Django 6 tasks, use the immediate backend only for focused execution checks:

```python
from django.test import override_settings

with override_settings(TASKS={"default": {
    "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",
}}):
    # Enqueue a task and assert its immediate effects.
    pass
```

Replace pass with the actual action; this is a setup pattern. Do not replace
on_commit with immediate enqueue to satisfy the test, or imply the immediate
backend reproduces durable production delivery/retries. It does not support future
scheduling. Use the configured backend or an explicit test double for deferred
tasks; changing a capability flag does not validate scheduling. Preserve any
project-specific task fixtures in the consuming repository.

## Sources

Checked 2026-09-08, Django 6.0:

- [Testing tools](https://docs.djangoproject.com/en/6.0/topics/testing/tools/)
- [Writing and running tests](https://docs.djangoproject.com/en/6.0/topics/testing/overview/)
- [Transactions](https://docs.djangoproject.com/en/6.0/topics/db/transactions/)
- [Tasks](https://docs.djangoproject.com/en/6.0/topics/tasks/)
