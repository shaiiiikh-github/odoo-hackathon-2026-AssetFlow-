# AssetFlow Backend — Full Build (Phases 1–4)

Enterprise Asset & Resource Management System — FastAPI + async SQLAlchemy 2.0 + PostgreSQL.

This is the complete backend: auth & master data, asset registration/lifecycle,
allocation & transfer workflows, resource booking, maintenance workflow, and
audit cycles — all wired into one running app. No test suite is included by
request; everything else (migrations, models, services, routers, DI, error
handling) is complete and runnable.

## Run it

```bash
cp .env.example .env          # edit DATABASE_URL / JWT_SECRET_KEY
pip install -e ".[dev]"
alembic upgrade head
uvicorn src.main:app --reload
```

Interactive API docs at `http://localhost:8000/docs` (Swagger) or `/redoc`.

Requires PostgreSQL. Migration 0003 enables the `btree_gist` extension
(`CREATE EXTENSION IF NOT EXISTS btree_gist`) — this needs a DB role with
`CREATE EXTENSION` privilege the first time it runs (superuser, or grant
`CREATEDB`/extension rights ahead of time on managed Postgres).

## What's implemented, by phase

**Phase 1 — Auth & Master Data**
- Signup (Employee-only, no self-assigned roles) / login / refresh / session validation
- Admin-only Organization Setup: Departments (with hierarchy), Asset Categories, Employee Directory
- Role promotion (Employee → Department Head / Asset Manager) — the only place roles are assigned

**Phase 2 — Asset Registration & Directory**
- Register assets with auto-generated Asset Tag, full search/filter, lifecycle status
- `AssetStateMachine` — the single source of truth for legal status transitions
- Per-asset state-transition history

**Phase 3 — Allocation & Resource Booking**
- Direct allocation with the "already held by X → offer Transfer Request" conflict rule
- Transfer Request → Approve/Reject workflow, atomic re-allocation on approval
- Time-slot resource booking with zero-race overlap prevention via a PostgreSQL
  `EXCLUDE USING gist` constraint (not just an app-level check — see migration `0003`)
- Overdue-allocation query for the Dashboard/Notifications feed

**Phase 4 — Maintenance & Audits**
- Maintenance workflow: `PENDING -> APPROVED/REJECTED -> TECHNICIAN_ASSIGNED -> IN_PROGRESS -> RESOLVED`,
  with the asset flipping to `UNDER_MAINTENANCE` on approval and back to `AVAILABLE` on resolution
- Audit cycles: create (Admin), assign auditors, auditors submit findings
  (`VERIFIED`/`MISSING`/`DAMAGED`, upserted per asset), live discrepancy report
- Closing a cycle locks it and — in the same transaction — pushes `MISSING` findings to
  asset status `LOST` and `DAMAGED` findings to asset condition `DAMAGED`

## Concurrency strategy, in one place

| Scenario | Mechanism | Why |
|---|---|---|
| Allocate/return/maintenance-approve on one asset | `SELECT ... FOR UPDATE` on the asset row | One hot row, short critical section — pessimistic lock is simplest and correct |
| Two simultaneous allocations of the same asset | Partial unique index `uq_active_allocation_per_asset` (DB backstop) | Guarantees correctness even if an app-layer lock is ever bypassed |
| Overlapping resource bookings | `EXCLUDE USING gist (asset_id WITH =, time_range WITH &&)` | Locking the asset would serialize *all* bookings for a resource; the exclusion constraint only blocks genuinely conflicting rows, so unrelated time slots proceed concurrently |
| Two open maintenance requests for one asset | Partial unique index `uq_open_maintenance_per_asset` | Same pattern as allocation — keeps "approval means one unambiguous asset flip" true |
| Auditor re-submitting a finding | `INSERT ... ON CONFLICT (cycle_id, asset_id) DO UPDATE` | Atomic upsert, no read-then-write race |
| Closing an audit cycle (many assets) | Lock cycle row first, then lock every affected asset row in ascending id order | Fixed lock ordering across all multi-lock operations is what makes deadlocks structurally impossible, even against concurrent allocation/maintenance calls on the same assets |

## Cross-module orchestration — clean separation of concerns

`AllocationService`, `MaintenanceService`, and `AuditService` each import
`AssetStateMachine` and mutate `Asset` entities directly via `uow.assets` —
none of them import `AssetService` or each other. The dependency graph among
application services is flat (every service depends only on domain code +
`IUnitOfWork`), so there's no circular import between modules, even though all
three touch the asset lifecycle.

## Dependency Injection — how it's wired

There is no custom DI container. FastAPI's native `Depends()` graph is the
composition root, resolved per-request:

```
get_unit_of_work()                 -> SqlAlchemyUnitOfWork (composition root)
        |
        +- get_current_user(creds, uow)      -> validates JWT + re-fetches User from DB
        |       |
        |       +- require_roles(Role.ADMIN) -> 403s before the handler body ever runs
        |
        +- get_*_service(uow) -> constructs the Service with that request's UoW injected
```

Every service constructor takes an `IUnitOfWork`, never a concrete session —
swap `get_unit_of_work()` in `auth_middleware.py` to change persistence backend
app-wide, with zero changes to any service or router.

## Project layout

```
src/
  domain/            entities, enums, state machines, domain exceptions - zero framework deps
  application/        services (use cases) + repository interfaces + IUnitOfWork
  infrastructure/      SQLAlchemy models, repository implementations, JWT/password hashing, session/UoW
  presentation/        FastAPI routers, Pydantic schemas, DI wiring, auth middleware, error handler
alembic/versions/      0001 auth & master data, 0002 assets, 0003 allocation & booking, 0004 maintenance & audits
```

## Full endpoint list

See `/docs` once running, or `app.openapi()` - 38 routes across auth, organization
setup, employee directory, assets, allocation/transfer, booking, maintenance, and audits.

## Not included (by request)

No automated test suite. Everything else - migrations, models, services, routers,
error handling, and DI - is complete and has been verified to import cleanly and
build a valid FastAPI route table end-to-end.
