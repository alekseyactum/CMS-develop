# CMS stale refresh database migrations

On 14 October 2026 the owner authorized the database migrations following the dormant backend rollout.
The ten migrations were applied sequentially: develop first, then release. Feature activation, content
publication, frontend deployment, IAM/secrets changes and schedule activation were not included.

## Applied scope

The package creates 15 service tables, adds `recovery_revision` to the new dispatch-progress table,
and inserts three initial service rows. Existing page/section content and publication mode are not
changed. Migration IDs: `202610120001`, `202610120002`, and `202610130001` through `202610130008`.

The initial rows are two consistency barriers at revision zero and the refresh control row at revision
one. Its four delay values are 1,800,000 milliseconds (30 minutes); `automatic_paused=false` is the
product setting for eventual activation, not an enabled runtime worker. Capture/read/worker/command
flags remain separately disabled.

## Execution evidence

| Environment | Read-only before | Apply execution | Read-only after |
| --- | --- | --- | --- |
| develop | `cms-back-develop-migrate-v8sf4` | `cms-back-develop-migrate-qdwhp` | `cms-back-develop-migrate-hwg4n` |
| release | `cms-back-release-migrate-krqm4` | `cms-back-release-migrate-d2z5n` | `cms-back-release-migrate-wh5fw` |

Develop apply completed successfully at `2026-10-14T03:50:22.287016Z`; release at
`2026-10-14T03:53:06.402501Z`. Both used their already-deployed image, respectively builds
`2520ca38-e051-467d-b08e-deda165e89f4` and `664324e0-d9ee-44bb-82fb-668537d500e9`, with the normal command
`node dist/migrations/run-migrations.js`. No application rebuild or redeployment was necessary.

Before application both ledgers contained exactly the 46 expected previous migrations, all ten target
migrations were pending and none of the 15 target tables existed. This check was mandatory because
the normal runner applies all registered pending migrations. Only one applying execution ran per
environment; jobs have one task and no automatic retry.

The inspection executions used temporary per-execution arguments on the existing migration jobs.
Their database queries were SELECT-only. They did not alter the saved job configuration. The manifest
was derived from the deployed migration functions using a mock connection, never by sending their DDL
to the database during inspection.

## Verification

Both post-migration inspections passed: 56 ledger entries, zero pending migrations, all 15 tables and
101 columns present, expected indexes and named constraints present and enforced. Constraint totals
are 15 primary keys, 2 unique constraints, 11 foreign keys and 14 CHECK constraints. Exactly the three
expected initial service rows exist; source events, demands, executions and other queue data are empty.
No content backfill was run.

Local migration regression tests passed again: 32/32 in each checkout. The SELECT-only inspector also
passed five in-memory success/failure scenarios before its results were accepted. The schema inspector
checks table engine/collation, exact column names and required index/constraint names; it is not a
general-purpose comparison of every column type or CHECK expression. The clean before-state and
reviewed deployed DDL are the basis for this fresh-schema acceptance.

Authenticated health/readiness returned 200 in both environments, with database `ok` and unchanged
source/build identities. Release queue access returned the expected 503 `REFRESH_READ_NOT_ENABLED`;
the Ukrainian lawyer matrix returned 200 with 24 rows. Develop administrative access still returns
403 `CMS_USER_NOT_FOUND` for the actual operator, so full live develop admin acceptance is not claimed.

Both API revisions and 100-percent traffic assignments are unchanged. Refresh settings remain absent
from the service environments; both old one-minute schedules remain `PAUSED`. A bounded ERROR-or-higher
API log query after migration returned no entries. No IAM, secret, saved job or service configuration
was changed. The develop migration job's pre-existing APP_BUILD_ID/APP_COMMIT_SHA labels are older than
its image; the image tag and executed migration registry, not those labels, were used to identify code.

Local-only inspection helper SHA-256:
`46d12b11246fcdbfa310ceb402a63a3520cc1e0f354e61f4fcc568caee4418ba`.
Temporary helpers and compiled outputs were not included in source commits.

## Recovery and activation boundary

MySQL DDL is not transactionally reversible with the migration ledger. No failure or partial migration
occurred. Preserve these additive tables and migration records if the application is rolled back;
do not run blind down-migrations or delete service state.

Cloud SQL inventory confirmed enabled backups/binlogs and seven-day transaction-log retention for
both `develop-eu` and `site-release`. No backup/PITR settings were changed.

Application rollback references remain in the [backend rollout record](stale-refresh-backend-rollout-2026-10-14.md).
The remaining backend step is separately authorized activation after exact-writer readiness, actual
cache topology and dispatch authentication are checked. The CMS interface belongs to Yuri; the
five-minute protected caller belongs to the ERP backend developer.
