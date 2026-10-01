# Tailwind CSS Integration Reference

Reference Date: 2026-09-08
Sources:
- Detecting Classes in Source Files: https://tailwindcss.com/docs/detecting-classes-in-source-files
- Content Configuration (Tailwind v3): https://v3.tailwindcss.com/docs/content-configuration

## Pipeline Detection: Tailwind v3 vs. v4

Inspect project configuration files to detect the installed Tailwind setup without forcing migration:
- **Tailwind v3**: Configured via `tailwind.config.js` using the `content` array.
- **Tailwind v4**: Uses CSS-first setup starting with `@import "tailwindcss";`. Legacy JavaScript configuration files can still be loaded via the `@config "./tailwind.config.js";` directive.

Do not mandate migrating between versions if a working pipeline is in place.

## Content Scanning Roots and Boundaries

Tailwind detects complete class tokens from source text:

1. **Included Scan Roots**: Scans must cover active HTML templates as well as active JavaScript and CSS source files across apps:
   - `./templates/**/*.html`
   - `./<app>/templates/**/*.html`
   - `./static/**/*.js`
   - `./<app>/static/**/*.js`
   These are examples, not permission to read ignored paths. Include only allowed
   active sources in the actual pipeline; check whether root /static is generated.
2. **Exclusion Rules**: Scanner paths must strictly respect `.gitignore` and exclude generated or runtime directories:
   `node_modules/`, `staticfiles/`, `media/`, `venv/`, `.venv/`, `.git/`, and Python caches.
3. **Complete Class Names**: Never assemble Tailwind class names dynamically:
   ```html
   <!-- INCORRECT: Dynamic string interpolation cannot be detected by scanner -->
   <div class="bg-{{ status_color }}-500"></div>

   <!-- CORRECT: Statically identifiable class tokens -->
   {% if status == "error" %}
     <div class="bg-red-500"></div>
   {% else %}
     <div class="bg-blue-500"></div>
   {% endif %}
   ```

## Dedicated Compilation and Verification

- **Use the Dedicated CSS Build**: A development command can start unrelated long-running processes. Identify the project's dedicated CSS build command (e.g., `npm run build:css` or a static asset build target).
- **Verify Compiled Output**: Confirming that a class name appears in an HTML template is not sufficient; verify that the compiled CSS bundle contains the generated style rules.

## Styling Variants and Theme Policy

- **Interactive States**: Use standard variant prefixes (`hover:`, `focus:`, `focus-visible:ring-2`, `disabled:opacity-50`).
- **Error States**: Conditionally apply standard error utilities (`border-red-500 text-red-700`) when `field.errors` is present.
- **Dark Mode Policy**: Do not apply universal dark mode utilities (`dark:...`) unless the project has explicitly enabled and configured dark mode support.
