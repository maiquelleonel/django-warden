# Web boundaries

## Access, validation and sessions

Start from the affected endpoint and its intended audience. Scope list and object
queries to permitted users/tenants before disclosure or mutation. Related-object
choices need the same check. Use explicit writable fields, assign ownership from
request context and assert denied writes leave data unchanged.

Django authentication and CSRF middleware do different jobs. Do not exempt an
endpoint from CSRF because HTMX calls it. For tests, Client(enforce_csrf_checks=True)
exercises CSRF; default Client does not. Keep session rotation provided by login.
For a custom password-change flow, evaluate update_session_auth_hash and the
intended handling of current/other sessions.

## HTML, scripts and CSP

Autoescaping is appropriate for text/HTML contexts, not arbitrary JavaScript/URL
contexts. Prefer json_script or escaped data attributes for structured/scalar data,
then safe text output. Rich HTML needs a deliberate sanitizer and URL/attribute
policy, including active HTMX attributes. Avoid trusted status derived only from a
database field: that field may originate from user input or an external service.

Django 6 native CSP uses ContentSecurityPolicyMiddleware and SECURE_CSP or
SECURE_CSP_REPORT_ONLY. CSP.NONCE and the csp template context processor supply
matching policy/template nonces. Preserve existing configuration; report-only is
useful for a gradual change but does not enforce the candidate policy.

The standard Alpine build needs expression evaluation incompatible with a policy
without unsafe-eval. Use the CSP build when that constraint applies and verify its
supported expression subset; do not claim all inline expressions are forbidden.
Registration with Alpine.data is useful for reusable logic, not proof of build type.

HTMX evaluation-dependent features and injected indicator styles also need review.
Prefer external styles and non-executable fragment data. If scripts/nonces must be
inserted dynamically, verify their relationship to the live document policy rather
than assuming a fragment response's new nonce matches the page. Test in-browser.

## Cache and nonce lifetime

Vary: HX-Request separates representations; it does not isolate users. Choose an
explicit cache key/private/no-store policy matching authorization and sensitivity.
Private caches may still reuse responses. For nonce-bearing pages, avoid response
reuse unless the delivery architecture safely supplies a fresh nonce for every
response. Django never_cache provides a conservative policy; do not treat a lone
Cache-Control: private as equivalent to no-store.

Client-side HTMX history is separate from HTTP cache. Sensitive content may need
history exclusion using the loaded version's mechanism as well as server controls.

## Uploads

Choose permitted size/types and where validation happens. Check size at the edge
before accepting a large request and at the form/application boundary. An extension
allowlist is only an initial filter; content checks depend on the actual threat.
Use safe storage naming and prevent path traversal. basename alone is not sufficient.

FILE_UPLOAD_MAX_MEMORY_SIZE is a memory/disk threshold, not an upload-size cap.
DATA_UPLOAD_MAX_MEMORY_SIZE excludes uploaded file data. Enforce actual per-file/
request limits; DATA_UPLOAD_MAX_NUMBER_FILES limits file count, not bytes per file.
For asynchronous scanning, quarantine the
object and prevent access until its status permits serving; enqueue after commit.

Serve private objects through authorization or constrained signed access. Use
appropriate attachment/content-type/nosniff controls and consider a separate origin
for untrusted active content. Serving a malicious file with the right filename is
not a validation success.

## Verification and sources

Exercise denied users, forged fields/related IDs, invalid CSRF, injected text and
unauthorized downloads. Check headers and real browser policy behavior; do not claim
a test passed when its required environment was unavailable.

Sources checked 2026-09-08:

- [Django 6 security](https://docs.djangoproject.com/en/6.0/topics/security/)
- [Django 6 CSP](https://docs.djangoproject.com/en/6.0/ref/csp/)
- [Django settings: uploads](https://docs.djangoproject.com/en/6.0/ref/settings/#data-upload-max-memory-size)
- [Django 6 testing](https://docs.djangoproject.com/en/6.0/topics/testing/tools/)
- [Alpine CSP](https://alpinejs.dev/advanced/csp)
- [HTMX](https://htmx.org/docs/)
