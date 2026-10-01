# Browser verification and skill evaluation

## Interaction evidence

Use the existing authorized browser runner. If unavailable, report the missing
verification and complete the independent Django/static checks. Do not call a
markup assertion proof of JavaScript behavior or quietly install a new stack.

For an HTMX/Alpine form, exercise:

1. Open the control with keyboard or pointer and check focus.
2. Submit invalid and empty input; see errors in the intended region with data retained.
3. Submit valid input; verify server persistence and the visible update/event.
4. Reopen, perform another swap and repeat; check for duplicate listeners, lost local
   state, missing target IDs or focus trapped in detached DOM.
5. Refresh/deep-link/back where history is part of the feature. Test the required
   non-JavaScript fallback using a real form action/method or ordinary link.

For Tailwind, compile the project's declared version and inspect the actual visual
states, not just class strings: focus, invalid, selected, responsive and dark mode
only if supported by this UI. Collect browser console errors and CSP violations.
An accessible modal also needs labeling, keyboard behavior and focus return.

Use deterministic assets and data where practical. Avoid live external APIs in an
interaction test; the test should fail because the implementation is wrong, not
because an unrelated third party changed or is unavailable.

## Evaluating these skills with models

Separate discovery from execution. Use natural requests without skill names first;
observe actual loading. Explicit invocation can diagnose a failed selection, but
does not turn it into a discovery pass. A required local Warden load is not a false
positive by itself; inspect which additional skills/references were used.

Compare fresh workspaces with equal tasks/tools/data and equivalent instructions.
For a neutral fixture use no package versus candidate. For a governed fixture keep
its active contract intact and compare current versus candidate; do not remove mandatory rules
to manufacture a control. Detect inherited skills/plugins before claiming isolation.

Keep the oracle, seeded-defect explanations, desired implementation and previous
answers out of the executor's context. Grade behavior independently after generation.
Use unseen variants after revisions so the final result is not only a memorized case.

Record actual model identity where returned, requested/confirmed effort, client
version, skill hashes, loaded files, generated diff, test output and limitations.
Use the models and effort levels agreed for the evaluation; do not substitute a
stronger authoring model for an implementation trial.

Compare per case/model, including negative routing requests. Functional/security
failures cannot be hidden by a better average. Change only instructions implicated
by observed failures; agree a revision budget and report assisted repairs separately.
Do not claim a small passing fixture establishes universal reliability or production
security. Preserve that distinction in the handoff.

## Sources

- [Django test client and browser distinction](https://docs.djangoproject.com/en/6.0/topics/testing/tools/)
- [HTMX documentation](https://htmx.org/docs/)
- [Alpine lifecycle](https://alpinejs.dev/essentials/lifecycle)
- [Tailwind source detection](https://tailwindcss.com/docs/detecting-classes-in-source-files)

Sources checked 2026-09-08; evaluation methodology here is the project's chosen
procedure, not a claim that these frameworks mandate a particular model benchmark.
