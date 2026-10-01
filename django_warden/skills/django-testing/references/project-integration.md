# Checking applicability to the project

Use for a project change or to evaluate whether instructions fit the real project.
Read the affected source and active contract. Recommendations may revise current
conventions when requested; do not present them as already implemented.

## Discriminating cases

- A new UI prefix receives 403: trace middleware and URL resolution as well as auth.
  A prefix allowlist is not a login/permission mechanism. Test allowed and
  rejected paths and the endpoint's actual authorization separately.
- Two Admin template overrides share a name: inspect loader order and block.super,
  then render both contributions. Same-name extends can skip the current origin;
  do not grade the second override as dead solely from its path.
- A new writer saves a domain identity: inspect signals/jobs, identity keys, overwrite
  policy and reciprocal links. Test failure/rollback consistency; update_fields
  alone does not make multiple writes atomic or solve concurrent identity matching.
- A task is enqueued in atomic: inspect the real backend's transaction/delivery
  semantics. Test commit and rollback, and distinguish never-enqueued from cancelled.
  An injected on_commit callback is useful evidence but not a production queue test.
- Coverage looks complete: check measured modules/exclusions and changed behavior.
  A global percentage with excluded modules cannot establish 100% of all new logic.

## Evidence levels

An isolated source slice can test a template override chain or a middleware class
without starting the full application. Label the slice, stubs and settings: it does
not prove the production deployment is secure or that every app initializes.
Do not execute application startup merely to read metadata when it has file-generation
side effects; prefer allowed source inspection and scoped isolated checks.

Use the actual test runner with focused dotted module names. Exercise browser
behavior when JavaScript participates. Use PostgreSQL for PostgreSQL-specific
locking semantics. If the required environment/MCP is unavailable, say exactly
what remains unverified rather than treating a synthetic fixture as full coverage.

Separate the first generated result from an assisted repair. Keep task inputs,
oracle expectations and package hashes; do not expose the oracle to the executor.
Correct a defective evaluator only with a documented reason, not to manufacture a pass.

## Sources

- [Django testing tools](https://docs.djangoproject.com/en/6.0/topics/testing/tools/)
- [Django template overrides](https://docs.djangoproject.com/en/6.0/howto/overriding-templates/)
- [Django transactions](https://docs.djangoproject.com/en/6.0/topics/db/transactions/)

Reviewed 2026-09-09. The project's exact source paths/policies must be reconfirmed for a
new implementation; this reference gives verification criteria, not frozen schema.
