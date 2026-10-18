# CMS scoped roles rollout

Date: 2026-10-18. Status: backend migrated, pushed and deployed to develop and release; frontend adaptation remains pending.

The owner authorized migration, source push and deployment to develop and release, then explicitly
accepted a backend-first rollout despite the current CMS-front limitations. Existing user assignments
are not automatically converted. No content publication, SEO approval or frontend deployment is included.

## Source and baseline

| Environment | Implementation | Deployment head | Previous ready revision |
| --- | --- | --- | --- |
| develop | `8a50de537e3b6a16f66879d88ec9a161a7e89687` | `ab81e3132517f9fe907349105f59acb430cc29ca` | `cms-back-develop-00336-7bs` |
| release | `d1f5ac94188aaf2bd9e64b5e2e6d1f2ac64275c3` | `4c98e479b65b042509ea399fea6bdc3494e46d2d` | `cms-back-release-00126-k2r` |

Release uses focused cherry-picks. Its existing JSON-LD differences and environment configuration
are preserved. Existing exact-branch Cloud Build triggers are used; no pipeline or trigger is changed.
The governing playbook preflight passed before cloud access. Cloud SQL backups and binlogs are enabled
with seven retained backups and seven-day transaction-log retention on both instances.

## Migration

Only `202610180001` is authorized/applied by the bounded helper: it creates `cms_page_seo_approvals`
and records the migration. No backfill, synthetic approval or user-role reassignment is performed.

The operator runs the existing environment migration job using execution-only arguments. The old
image receives the locally compiled, hash-checked target and tested helper. Its saved configuration
is unchanged. The helper permits only the exact target DDL, checks the full 56-entry baseline,
fails on unexpected or partial schema, verifies columns/indexes/constraints and fresh-table emptiness,
then records completion once. Default inspection is SELECT-only.

| Environment | Before inspection | Applying execution | Result |
| --- | --- | --- | --- |
| develop | `cms-back-develop-migrate-j4rlj` | `cms-back-develop-migrate-wjhvh` | Applied; 57 ledger entries, valid schema, zero rows |
| release | `cms-back-release-migrate-fhgkf` | `cms-back-release-migrate-fqk5g` | Applied; 57 ledger entries, valid schema, zero rows |

Reviewed artifact SHA-256:

- Source migration: `afae0bf4cb2a31525e0228e483fe2e1a7e7f1dd06293d0d079bda10a2559c5b8`.
- Compiled migration: `e12e6e3ad9d3e3751a87e9c7662eda89eca0bfcd1fedf63b135e9486d0ef5474`.
- Operator helper: `a9d5d988153eb5de8cae4eaa92cb82533e085423ca7d645f19aae67454256708`.

## Verification

- Develop full suite: 3,621 passed, zero failed, one MySQL-fixture skip.
- Release full suite after source push: 3,604 passed, zero failed, one MySQL-fixture skip.
- Production builds and release runtime-module import passed.
- Focused authorization/SEO tests after source push: 50 passed; another 15 passed after develop push.
- Migration helper: 15 tests passed, including rejection, schema verification and idempotent rerun.
- Actual operator is an active release administrator. Develop returns the pre-existing
  `CMS_USER_NOT_FOUND`; no alternate identity or extra rights are used for smoke tests.

Develop build `0d3e864d-99a3-4214-8546-e954253c0869` succeeded at `2026-10-18T04:35:05.663378Z`.
Revision `cms-back-develop-00337-7gm` receives 100% traffic; authenticated health/readiness returned
200 with the expected commit and database `ok`. The bounded new-revision ERROR log query was empty.
Release build `9d1a5682-f523-4d3b-bd2c-489aaf833697` succeeded. Revision
`cms-back-release-00127-k7c` receives 100% traffic; authenticated health/readiness returned 200
with the expected commit and database `ok`. The bounded new-revision ERROR log query was empty.

Release read-only checks also passed for `/admin/me` with `cms-scoped-roles.v1`, six Ukrainian role
labels, unchanged active-user/admin counts and zero permissions for retired-only assignments.
An existing published Ukrainian lawyer page returned 200 from SEO-approval state (zero approvals)
and publication state (`canPrepareSeo=true`). Queue and workbench tree reads returned 200.
The initial home-page fixture query returned no records; the smoke used an existing lawyer page
instead of creating test content. No Save/Publish/approve/revoke command was used.

Each environment's migration and publication-effects jobs match its deployed service image.
Refresh worker/commands remain false in develop and true in release. Read remains enabled;
origin cache remains `no_store`, CDN mode `absent`. No schedule, IAM, secret, saved migration
command or frontend configuration was changed. Focused release tests after the deploy-bearing
push passed 30/30.

Unit tests and read-only smokes do not constitute browser acceptance of every role or a real
MySQL transaction-race test. Develop end-user acceptance remains limited by the operator's
pre-existing absent CMS account.

## Accepted frontend limitations

Remote CMS-front refs checked after fetch: develop `7cb91c1`, release `c2b0d20`.
Neither implements `cms-scoped-roles.v1`, SEO approval, or SEO-scoped publication. First publication
and SEO-only publication are unavailable through the current UI. Existing-page exact content
publication preserves published SEO; it cannot silently publish saved SEO changes.

User creation still seeds retired `editor`; reference selectors still use admin-only ERP APIs;
role labels still need the Ukrainian metadata label. These require CMS-front changes.
The deployed release frontend has `CMS_PUBLICATION_MODE=exact`; develop has no such setting and
defaults to legacy. Its legacy publication paths are denied by the new backend. No frontend mode
or runtime configuration is silently changed in this rollout.

Before rollout, release has seven active users: two administrators and five users with only retired
roles. The five assignments remain stored but grant no permissions under the new backend. Replacement
assignments require explicit agreement; they are not inferred from the retired broad roles.

## Recovery

Preserve the additive approval table and migration ledger on application rollback. Do not drop SEO
approval history or restore page snapshots. Prefer a reviewed revert/forward fix through the same
git-based deployment flow; the previous ready revisions above identify the application baseline.
If new roles are assigned later, an old-backend rollback needs a separately approved assignment
plan, because old code does not recognize the new keys. Never automatically restore broad roles.
