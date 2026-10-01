# Django view patterns

## Representation and validation

Choose the representation only after authentication and scoped data access. A
native Django implementation does not require installing django-htmx:

```python
is_htmx = request.headers.get("HX-Request") == "true"
form = EditForm(
    request.POST if request.method == "POST" else None,
    request.FILES if request.method == "POST" else None,
    instance=object_,
)
```

This is a fragment of an existing view; EditForm and object_ come from the actual
application. Do not paste it as a complete endpoint. For non-upload forms the
files argument is unnecessary. An empty POST is bound and displays required errors.

Use Forms/ModelForms for HTML and Serializers for an API. Only DRF supports
is_valid(raise_exception=True); Django Forms use is_valid(). Allow writable fields
explicitly and supply ownership from request context, including foreign-key choices.

On valid normal POST, follow the existing redirect-after-write contract. On an
HTMX success, return the specified fragment, navigation response or event. Do not
require HX-Trigger for every successful operation. On invalid input, return a
bound form to a target that exists in that representation; do not swap a document
shell into a form region or remove the target ID accidentally.

## Redirects and session expiry

For HTMX 1.9/2.x, HX-Redirect on a non-3xx response performs full navigation;
HX-Location has different partial-navigation semantics. The browser follows HTTP
3xx redirects before HTMX handles the final response, so attaching HX-* headers
to a 302 is not equivalent. Validate exact behavior for the loaded version.

If an expired session redirects a fragment request to login, avoid inserting the
login page into a panel. Reuse the application's established auth/HTMX integration;
when authorized to change it, return a safe local navigation response appropriate
to that client. Do not copy an unvalidated next URL into redirect headers.

## Helpers and caching

If django-htmx is installed and integrated, use its relevant HTTP helpers for
redirects, triggers, retargeting and history. Otherwise standard HttpResponse
headers are sufficient; do not install a dependency just for a header.

For a cacheable public view varying by HX-Request, combine Vary with the cache
boundary in the correct decorator order; preserve Vary even on an initial normal
response. For user-specific or nonce-bearing HTML, a representation split alone
does not prevent disclosure or replay. Choose private/no-store/keying policy
according to the data and verify the actual response headers.

## Sources

Checked 2026-09-08:

- [Forms API, Django 6.0](https://docs.djangoproject.com/en/6.0/ref/forms/api/)
- [HTMX docs](https://htmx.org/docs/)
- [HTMX response headers](https://htmx.org/reference/)
- [Optional django-htmx HTTP helpers](https://django-htmx.readthedocs.io/en/latest/http.html)
