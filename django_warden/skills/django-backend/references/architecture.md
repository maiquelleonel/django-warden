# App and workflow boundaries

Use when choosing ownership or coordinating work between Django apps. These are
design criteria; Django does not mandate a services/orchestrators directory split.
For a review of established conventions, also use [evolution](evolution.md).

## Identify ownership before adding a layer

- Name the domain that owns each model and its invariants. A model does not move
  merely because a second app displays its data.
- Keep reusable query operations with the owning QuerySet/Manager. A repository
  or unit-of-work wrapper is not needed to access the Django ORM.
- Follow dependency direction deliberately. A shared visual component should not
  import domain models to fetch its own data; callers provide its display context.
- Coordinate cross-app work at an existing workflow boundary. If none fits, explain
  the proposed owner and dependencies before creating one; do not introduce a
  universal shared app just because two consumers exist. A focused technical/UI
  app is reasonable when it owns reusable tags, assets or other explicit behavior;
  sharing domain data alone does not require moving the owning models into it.
- Use app-qualified model references and URL namespaces where appropriate. Avoid
  import-time queries, circular imports and work in AppConfig.ready that depends
  on mutable database state.

## Separate the decisions

Models represent data and local invariants. Forms/serializers validate inputs and
adapt them for writes. Views/admin handle HTTP/presentation and call the existing
domain boundary. External clients handle transport/authentication/timeouts for
third parties. Multi-step workflows coordinate those components and transactions.

For a small CRUD change, a ModelForm and a thin view can be sufficient. For a
cross-app transaction or state machine, make the workflow explicit. Do not add
a service, DTO or interface solely to make a simple operation look layered.

Admin is suited to internal model-centric work. A process-oriented interface can
use ordinary Django views and an independent shared shell while reusing the same
domain operations. Do not make a new UI call an Admin view as its business API,
or assume it inherits staff/object permissions because it resembles Admin.

When a workflow crosses a database and an external service, document the possible
partial failure. An atomic database transaction cannot roll back an HTTP request.
Use the existing task/delivery mechanism and idempotence strategy; introduce a new
delivery architecture only when the task's guarantees require it and are in scope.

## Evidence to check

- Can the requested change stay inside current ownership?
- Is the permission rule enforced at the actual data access path?
- Are dependencies one-way, and can components be tested without unrelated apps?
- Is UI reuse achieved with explicit context and namespaced templates/URLs?
- Are workflow state transitions and failure behavior testable?

## Sources

Checked 2026-09-08; local conventions take precedence where explicitly specified.

- [Django 6 applications](https://docs.djangoproject.com/en/6.0/ref/applications/)
- [Django 6 managers](https://docs.djangoproject.com/en/6.0/topics/db/managers/)
- [Django 6 URL namespaces](https://docs.djangoproject.com/en/6.0/topics/http/urls/#url-namespaces)
- [Django 6 model forms](https://docs.djangoproject.com/en/6.0/topics/forms/modelforms/)
- [Django 6 Admin scope](https://docs.djangoproject.com/en/6.0/ref/contrib/admin/)
- [Django design philosophies](https://docs.djangoproject.com/en/6.0/misc/design-philosophies/)
