# Queries, transactions and side effects

## Queries

Evaluate when a QuerySet runs and which relations presentation accesses. Filter,
order and aggregate in the database where that is the operation required. Use
`select_related` for consumed single-valued relations and `prefetch_related` for
consumed collections. A prefetch does not cover a subsequent different `.filter()`.
Use `exists()` for an existence check when the objects are not also needed.
Check query growth with representative list sizes, including rendering.

## Writes and concurrency

- `save(update_fields=[...])` changes selected columns on an existing object;
  an empty iterable skips saving. It is not optimistic locking.
- `F()` can express a relative database update without a Python read/modify/write
  race. Uniqueness constraints protect uniqueness; conditional updates can enforce
  an expected state. Check the affected row count when the business rule needs it.
- For serialized read/modify/write operations, consider `select_for_update()` inside
  `atomic()` on a supporting database, with consistent locking order. SQLite cannot
  prove PostgreSQL row-locking behavior. Do not claim a concurrency test passed
  based only on SQLite.
- `atomic()` ensures a database transaction boundary, not serialized access by itself.
  Use an inner atomic block/savepoint when catching an expected database exception
  and continuing queries in an enclosing transaction.
- Bulk updates skip model save hooks. Bulk deletes still dispatch delete signals;
  inspect cascades and custom delete behavior before changing an operation to bulk.

## Signals

Prefer an explicit workflow when the caller needs to know the operation happened.
Use signals when they fit the existing integration boundary. A receiver saving the
same object needs an actual escape condition; passing update_fields alone does not
stop recursion unless a receiver inspects it. Avoid slow HTTP or model calls in a
signal. Do not swallow every exception: specify which failure may be tolerated.

Signal exceptions do not guarantee all earlier writes are rolled back. That depends
on transaction boundaries and whether the writes have already committed.

## Tasks after commit

Confirm the installed task API and backend. For Django 6 task objects with enqueue:

```python
from functools import partial
from django.db import transaction

transaction.on_commit(partial(send_notification.enqueue, object_id))
```

Register in the transaction containing the relevant write. Bind callback arguments
at registration; callbacks closing over a changing loop variable can act on the
wrong object. Pass stable identifiers, and reload data according to the intended
snapshot/fresh-state semantics. Rollback discards callbacks registered in that scope.
Outside a transaction an on_commit callback runs immediately.

Treat retries and duplicate execution explicitly for externally visible effects.
Do not enqueue before commit just to make an immediate-backend test pass.

## Sources

Checked 2026-09-08, Django 6.0:

- [QuerySet API](https://docs.djangoproject.com/en/6.0/ref/models/querysets/)
- [Model saving and validation](https://docs.djangoproject.com/en/6.0/ref/models/instances/)
- [Transactions and on_commit](https://docs.djangoproject.com/en/6.0/topics/db/transactions/)
- [Tasks](https://docs.djangoproject.com/en/6.0/topics/tasks/)
- [Database optimization](https://docs.djangoproject.com/en/6.0/topics/db/optimization/)
