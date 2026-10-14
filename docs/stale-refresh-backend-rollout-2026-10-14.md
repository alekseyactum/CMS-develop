# CMS stale refresh backend rollout

## Approval and scope

The owner authorized commit, push and backend deployment to develop and release on 14 October 2026.
This deploys the durable scoped-refresh implementation without activating it. All five source/cache
capture flags and all three read/worker/command flags remain absent or false. No shared migration,
page publication, content edit, frontend deployment, writer-mode transition, secret/IAM change or
scheduler activation is included. The existing pipeline updates job images but does not execute jobs.

Coverage includes reviews, lawyer profiles/cards/selections, editorial lists, published shared sections,
practice/service catalogs, regional-page links and physical offices. Refreshes use the published
snapshot and their approved source scope; drafts and unrelated content are not adopted. The product
contract is [stale page refresh](stale-page-refresh-contract-2026-10-12.md); backend integration details
are in `docs/stale-refresh-foundation.md` and `docs/stale-refresh-http-contract.md` in `re-actum/cms-back`.

## Source promotion

| Environment | Previous source | Deployed candidate |
| --- | --- | --- |
| develop | `b68ee8b3822b90ab2f5db1105e8cbd1770ebb488` | `47682519d7c3e1754527e7975ac569a78c32b025` |
| release | `ce31fce38ddc73b7bd96280fcc24e110ea32f27f` | `17ec4f3b8487469a5d8e26fb5a37e4b6b58d3b4d` |

Feature `ce5915e` was merged with the two current develop commits, preserving lawyer ordering and
workbench publication attention. Release uses the focused cherry-pick `8e929b3`, not a develop merge;
its pre-existing structured-data/workbench differences are retained. Bootstrap fix `4768251` maps to
release `17ec4f3`. Both working branches (`codex/stale-refresh-backend`, `codex/stale-refresh-release`)
and environment branches were pushed without force. Updated specification `f5ed295` was pushed to
the existing `codex/tz-2-to-tz-3-handoff` branch in `alekseyactum/CMS-develop`.

No deployment YAML, Dockerfile, package manifest or dependency lockfile changed. Temporary compiled
files and local operational scripts under `.codex_tmp` were excluded from commits.

## Verification

The governing playbook preflight passed before cloud reads. Live backend triggers used exact
`^develop$` and `^release$` branch filters. Both publication schedules were `PAUSED`.

Full application checks exposed eager imports from persistence/publication into graph and lifecycle
adapters. These adapters now load only on their execution paths. Fresh-process regressions verify two
import orders, real Nest injection tokens and application startup without database calls.

- Production and test TypeScript compilation passed in both environments.
- Clean develop full suite: 3,005 passed, one existing opt-in skip, zero failures.
- Clean release full suite: 2,987 passed, one existing opt-in skip, zero failures.
- Post-deploy-push cold-bootstrap/config/disabled-worker checks: 16 passed in each checkout.
- Suites ran from clean output directories in bounded groups. Initial attempts encountered the
  Windows argument-length limit and obsolete nested build outputs; those runs are not acceptance.
- The preceding implementation verification passed 30 scenarios against isolated local MySQL,
  including real transactions, concurrency, source capture, scoped publication and cache completion.
  No shared database was used for these tests. The ten new migrations were not executed in either
  environment as part of this rollout.

## Develop acceptance

Build `2520ca38-e051-467d-b08e-deda165e89f4` succeeded at `2026-10-14T03:13:02.237847Z`.
Ready revision `cms-back-develop-00316-dgg` receives 100 percent traffic. Authenticated `/api/health`
and `/api/ready` returned 200 with the exact source/build and database `ok`. OpenAPI exposes the new
read, command and internal dispatch routes. All new flags and dispatch/cache settings remain absent.

The actual operator's queue and lawyer-matrix reads returned 403 `CMS_USER_NOT_FOUND`. No identity
substitution or permission change was attempted; live develop administrative acceptance is not
claimed. A bounded ERROR-or-higher query for the new revision returned no entries at verification time.

## Release acceptance

Build `664324e0-d9ee-44bb-82fb-668537d500e9` succeeded at `2026-10-14T03:20:05.848173Z`.
Ready revision `cms-back-release-00105-hcm` receives 100 percent traffic. All new feature flags and
dispatch/cache settings remain absent. A bounded ERROR-or-higher query for this revision returned
no entries at verification time.

Authenticated `/api/health` and `/api/ready` returned 200 with the exact source/build and database `ok`.
OpenAPI exposes the six checked refresh routes. Queue read returned 503 `REFRESH_READ_NOT_ENABLED`,
confirming the disabled gate. The existing Ukrainian lawyer matrix returned 200 with 24 rows and
publication-state fields. These checks made no content writes.

## Jobs and schedules after deployment

The existing pipeline updated migration/publication job images to their respective builds. Commands
remain `node dist/migrations/run-migrations.js` and `node dist/section-publication/run-publication-effects.js`.
The latest executions are unchanged from the pre-rollout inventory:

| Job | Latest execution |
| --- | --- |
| `cms-back-develop-migrate` | `cms-back-develop-migrate-2tp55` |
| `cms-back-release-migrate` | `cms-back-release-migrate-vxngz` |
| `cms-back-develop-publication-effects` | `cms-back-develop-publication-effects-wpvl4` |
| `cms-back-release-publication-effects` | `cms-back-release-publication-effects-wmpc5` |

Both `cms-back-develop-publication-effects-1m` and `cms-back-release-publication-effects-1m` remain
`PAUSED`. No new refresh flags or dispatch/cache settings were added to the jobs.

## Rollback and activation boundary

Immediate pre-rollout application references:

| Environment | Ready revision | Build |
| --- | --- | --- |
| develop | `cms-back-develop-00315-rfh` | `ad583d62-220b-42af-baa5-9369fd8cd88b` |
| release | `cms-back-release-00104-9rj` | `271eca4d-f848-4c4b-b346-46d858666738` |

Prefer an approved focused git revert/forward fix through the existing pipeline. Emergency traffic
rollback needs explicit approval. This dormant rollout requires no schema/data rollback. Keep the
existing content, media keys, publication mode and paused schedules.

Activation is separate: authorize and verify the ten additive migrations, exact-writer readiness,
actual cache topology and dedicated dispatch authentication, then enable the agreed flags. The ERP
developer owns the five-minute caller; Yuri owns the single CMS queue/journal interface. No old
one-minute schedule was enabled as a substitute, and no CDN was provisioned or purged.
