# HTMX security and testing

## Preserve feature-level protections

Scope objects and related choices before both full-page and fragment access. Test
another authenticated user's identifier, not only anonymous requests. Reject writes
without valid CSRF; the default Django Client disables those checks.

Keep autoescaping on. User-controlled rich HTML needs a deliberate sanitizer policy
including active attributes such as hx-*, hx-on*, URLs and script-bearing content.
A harmless-looking attribute can initiate a request. Prefer text and normal form
fields over js: expressions in hx-headers/hx-vals.

History caching, HTTP caching and authorization are separate decisions. Vary does
not authorize a response. Treat session expiry and login navigation explicitly.
CSP must match the actual HTMX/Alpine builds; never relax a policy just to pass a test.

## Focused Django tests

Use TestCase methods with fixtures created by the test, not pytest-injected
client/user parameters. In a fixture with self.user and self.object prepared:

```python
from django.test import Client

client = Client(enforce_csrf_checks=True)
client.force_login(self.user)
response = client.post(
    edit_url, {"title": "Changed"}, headers={"HX-Request": "true"}
)
self.assertEqual(response.status_code, 403)
```

edit_url is the endpoint under test. Check unchanged database state on rejection;
add a successful token-bearing path, using the application's CSRF configuration.

Cover the full page and fragment, empty/invalid POST, headers/status for the
declared contract, scoped list reads, denied writes and correct root markup.
Do not fix a universal query count or require HX-Trigger for every view.

Django assertions establish HTML and headers, not DOM swaps or focus. Use browser
checks for a complete interaction: open, invalid submit, valid submit, re-open,
Escape/Tab/focus return, repeated swaps and the required JavaScript-free path.

## Sources

Checked 2026-09-08:

- [Django 6.0 testing tools](https://docs.djangoproject.com/en/6.0/topics/testing/tools/)
- [HTMX security and request handling](https://htmx.org/docs/)
- [Alpine CSP build](https://alpinejs.dev/advanced/csp)
