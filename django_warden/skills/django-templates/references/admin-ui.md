# Admin, application pages and shared presentation

Use for existing Admin customizations or when choosing a home for new UI.

## Choose the surface by the workflow

Django Admin is designed for trusted internal, model-centric management. Keep it
where that fits. A process-oriented experience may warrant ordinary Django views,
forms and templates, with a separate shell and the same domain operations.
Do not duplicate models or business workflows merely to serve another presentation.

For shared markup, project-level templates and explicit include context can suffice.
For a real library of reusable template tags, assets and component behavior, a
focused UI app can be justified. Keep domain queries/ownership with their apps.
Do not add a component framework, bundle pipeline or UI app without a concrete need.

## Same-name override chains

An override can extend its own template name. During that extends resolution the
loader skips the current origin and can find the next override/native template.
block.super preserves the parent block. Two apps overriding admin/base_site.html
therefore need not hide one another wholesale: app order, loader order and block
names determine composition. Inspect and render the chain before consolidating it.

For example, one app may customize blockbots and another extrastyle, both with
block.super. A project-level override is a useful
option for common branding, but moving these files is a separate change with
regression checks for both apps, asset ordering and inherited content.

## A shared appearance does not share authorization

AdminSite.admin_view protects a custom view wrapped through the Admin site; adding
a link/button or a template extending Admin does not wrap an unrelated URL. Check
staff requirements, operation/object permissions and the actual data policy.
A staff check alone is not object authorization. Do not invent a tenant field.

Check any URL-prefix middleware when introducing a new top-level namespace.
Keep root URL configuration, namespaces, permission checks and full/fragment paths
consistent. Do not disable middleware broadly to make a new route work.

## Asset and interaction contract

Assign one owner for library loading on each page. Inspect ModelAdmin.Media as well
as template script tags: adding a library in both can initialize behavior twice.
Classic defer scripts run in document order; component registration must precede
the Alpine build that starts automatically. A later classic external defer script
in the body is still later; a synchronous inline body script can execute before
deferred head scripts. Distinguish script types instead of inferring order from
head/body position alone.
Put x-cloak rules in the compiled source, not only a generated CSS file.

Preserve public DOM hooks on the intended control type, labels, keyboard/focus and
the required full-page fallback. Shared forms must have valid targets in both modal
and full-page contexts. Verify repeated swaps in a browser, not only rendered HTML.

## Sources

Checked 2026-09-09:

- [Admin purpose and custom views](https://docs.djangoproject.com/en/6.0/ref/contrib/admin/)
- [Overriding templates](https://docs.djangoproject.com/en/6.0/howto/overriding-templates/)
- [Template language](https://docs.djangoproject.com/en/6.0/ref/templates/language/)
- [Alpine initialization](https://alpinejs.dev/essentials/lifecycle)
