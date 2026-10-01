# Reviewing and evolving project standards

Use when the user asks to review architecture, revise conventions or plan a new
capability whose boundaries are not settled. Review authorization need not be
requested again when the task already provides it. A review is not automatic
authorization to migrate data, replace infrastructure or refactor unrelated flows.

## Separate evidence, constraints and recommendation

For each important decision record:

- Current behavior: source paths, data ownership, callers and side effects.
- Active constraint: framework behavior, security requirement, business invariant
  or local convention. Label which it is; a directory name is not a Django law.
- Recommendation: two reasonable options where the tradeoff matters, chosen owner,
  dependency direction, benefit and implementation/migration impact.
- Verification: a behavior or counterexample that can reject the recommendation.

Do not make users approve a vague direction before doing the scoped investigation.
Do not silently turn a proposed standard into a description of current code.
With excerpts, distinguish "not shown here" from "absent from the system". Confirm
migrations, constraints, normalization callers and runtime configuration before
claiming their absence or describing a hypothetical failure as an observed incident.

## Defaults for a growing Django full-stack project

Prefer a modular monolith while the problem fits it: cohesive domain apps, native
ORM/validation, explicit cross-app workflows and a shared presentation layer.
Distribution, an event bus or extra persistence abstractions need a demonstrated
requirement; file size or an architectural diagram alone is not that requirement.

Keep identity separate from collection/execution history. Before changing an upsert,
check uniqueness, normalization, field precedence, provenance and relationship
cardinality. Two reciprocal foreign keys are not proof that both sides stay in sync.
An updated consolidated record is not automatically an immutable snapshot/history.
Check uniqueness on the model actually being upserted; a unique field on the source
model is not a uniqueness guarantee on the destination. A lookup using a URL does
not prove that URLs are normalized. A max_length mismatch warrants validation of
accepted input and database behavior, not an assumption of silent truncation or an
automatic schema expansion. For all-or-nothing reciprocal links, define and test
the transaction boundary around both writes, alongside identity constraints.
Use an explicit validation/mapping policy for length mismatches. Do not silently
truncate identity fields or business data just to fit the destination column.

Trace effects triggered by save/delete, including signals and background jobs.
Avoid holding database locks across slow external calls where a short claim/work/
finalize sequence can provide the required consistency. That sequence needs explicit
state, conflict and retry handling; do not move code out of atomic mechanically.

For task dispatch, inspect the actual queue/transaction semantics. Distinguish
transactional insertion from external delivery, rollback from cancellation and
on_commit registration from durable publication. Preserve the active contract
unless the task authorizes changing it; do not claim all backends behave alike.

Choose a UI owner deliberately. Project-level templates may suffice for shared
markup. A focused UI app can own reusable presentation behavior when justified,
without becoming a second owner of customer records or other domain identities.

## Revisit absolutes with observable criteria

- Select related data that is actually consumed; measure queries including render.
- update_fields limits a write but does not solve every concurrency case.
- Performance rules about properties/tags should prevent hidden query growth;
  preserve stricter local rules during ordinary implementation.
- Coverage percentage depends on the measured files and branches. A global gate
  cannot prove coverage of excluded files or every changed line.
- Tools provide evidence; a missing MCP is an unavailable capability, not proof
  that the proposed architecture is wrong. Report the verification gap precisely.

Propose governance changes separately from implementation changes. Never weaken a
gate to hide a failure. Reuse approved decisions, avoid cosmetic bulk renames and
start with the next affected workflow instead of a whole-project rewrite.

## Sources

Framework references checked 2026-09-09; these defaults are design recommendations.

- [Django philosophy](https://docs.djangoproject.com/en/6.0/misc/design-philosophies/)
- [Applications](https://docs.djangoproject.com/en/6.0/ref/applications/)
- [Database optimization](https://docs.djangoproject.com/en/6.0/topics/db/optimization/)
- [Transactions](https://docs.djangoproject.com/en/6.0/topics/db/transactions/)
