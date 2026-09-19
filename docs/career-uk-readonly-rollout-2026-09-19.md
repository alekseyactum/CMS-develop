# Career Ukrainian/read-only backend rollout — 2026-09-19

Owner approved commit, push, backend deployment and rebuilding existing published career pages in
develop/release. Frontends, ERP callers/events, IAM, secrets, DNS and schema migrations are out of scope.
Required GCP preflight passed for `composite-ally-360719`, region `europe-central2`.

## Source and checks

- Backend: `re-actum/cms-back`, commit `4f407b33ced6232676898e12187648d7ffd38574`.
- Atomic push to `develop`, `release`, `codex/career-uk-readonly`; no force-push.
- Base `651d1cc43d1fa430d6d04e4ffaef63fbc0e3be70` includes the latest unrelated navigation fix.
- Requirements commit `a83b287` in `CMS-develop:codex/tz-2-to-tz-3-handoff`.
- Full local suite: 1001/1001 tests, typecheck and build passed on the updated base.
- Operator helper: 9/9 tests. Post-push scoped regressions: 81/81 plus 9/9 helper tests.
- Backend working tree clean after push. Unrelated CMS/playbook work excluded.

The backend uses Ukrainian ERP vacancy title/description/location on all page locales, rejects CMS
translation writes and ignores client vacancy runtime overrides. Page-owned copy remains localized.
Import records source/refresh intent but never publishes. Manual publication/rebuild uses current
source without additional implicit refresh; rollback restores the selected historical snapshot.
Explicit refresh now allocates fresh snapshot-section-reference IDs instead of copying old PKs.

## Deployment evidence

Existing git triggers only; no duplicate manual build, pipeline change or manual service update.

| Environment | Build | Previous revision | Result / new revision |
| --- | --- | --- | --- |
| develop | `194d1711-6a0b-4d63-a9c9-e7cdcfda1566` | `cms-back-develop-00293-7mw` | SUCCESS; `cms-back-develop-00294-xxq` |
| release | `cd1810d5-7b4f-484f-bcf0-3cc041941465` | `cms-back-release-00082-ctj` | SUCCESS; `cms-back-release-00083-929` |

Both builds completed around 16:10 UTC. Both ready revisions receive 100% traffic. Authenticated
health/ready passed on the exact expected commit/build with database status `ok`; image tags match
the corresponding successful builds. Bounded post-deploy ERROR checks returned zero entries.

## Controlled content refresh

Before rollout the release admin catalog returned zero career pages. Develop admin API returned
`403 CMS_USER_NOT_FOUND` for the actual operator identity; no alternate user, role or permission was used.
Server-side inspection/refresh uses the existing environment-specific operator job and runtime IAM,
with an execution-only `node -e` override for `scripts/career-published-refresh.cjs`. Default migration
arguments are not run; no migration is needed for this change.

The helper defaults to read-only inspect, checks exact DB/commit and produces a content-free manifest.
Execute requires the unchanged inspection hash. It targets published non-regional career pages with
an active vacancy runtime slot; absent/unpublished/disabled pages stay untouched. It verifies source,
other content, semantic refs and structured data, and reports old/new snapshot IDs. Zero targets means
no writes.

Read-only inspect executions succeeded:

- Develop: `cms-back-develop-migrate-ltl72`, two published pages, UK and RU, three vacancies each;
  manifest `24c2e7538f701e99bffaa743368b31cc1bfd1d8eddba422dab7ef2d7bd060be0`.
- Release: `cms-back-release-migrate-49ngv`, zero career pages/vacancies and empty refresh queue;
  manifest `9e4c68bf7ed1dfdf679bb4df731d314d1bf06ec886f0f48aeebcedf7b7017f64`.
  No execute/write was performed on release; no new page was created or published.

Develop execute `cms-back-develop-migrate-fsgrp` succeeded at 16:14:55 UTC with `verified:true`,
`changedCount:2`. Exact rollback points:

| Route | Page ID | Old snapshot | New snapshot |
| --- | --- | --- | --- |
| `/career` | `adb0e047-d01d-4fa9-a0e9-99cc5191b9b1` | `ca8cd5ac-78dd-4aee-b949-a330da19fed8` (#2) | `cc35a4bd-e52d-4f0f-9e09-30d7a92a870d` (#3) |
| `/ru/career` | `30563e30-8e43-4b92-818b-c6fa54d7df7b` | `0fd9819f-ed61-4c74-aae1-58d038e18421` (#1) | `968377ef-3e73-428e-9484-c16113871ecb` (#2) |

The helper verified equal Ukrainian ERP runtime on both pages and identical hashes for every other
published content field, semantic section refs and structured-data dependencies. Source content did
not change during execution. No draft or unrelated page was published. All refresh locales are now
non-pending without errors: UK generation 5/5, RU 14/14, EN 5/5 (unchanged). RU's previous failed
generation was acknowledged by successful processing, not by manually clearing its error.

Public backend API smoke independently confirmed both new snapshot IDs and three identical Ukrainian
vacancies (`contentLocale:uk`); form locales remain UK/RU respectively. Release `/career`, `/ru/career`
and `/en/career` correctly return `404 PUBLIC_PAGE_SNAPSHOT_NOT_FOUND`. No UI/cache claims are made.

The develop migration job inherits old `APP_COMMIT_SHA` metadata because its existing pipeline updates
only the image. For each operator execution, first verify the job image equals the newly deployed
service image/build, then pass matching build/commit metadata for that execution only. Permanent job
configuration is not changed to work around this. A commit environment variable alone is not image proof.

## Rollback

Code: reviewed revert through the same pipelines, preserving tables and all historical content.
Emergency traffic rollback to the prior revisions above requires approval.
Content: retain each old snapshot; restore through the normal snapshot lifecycle or an operator CAS
rollback with `expectedCurrentSnapshotId` equal to the snapshot created by this refresh. Do not overwrite
a later editor publication. Do not delete snapshots or reset generation counters to hide failures.

Frontend follow-up belongs to Yuri: remove vacancy edit/translation controls, show Ukrainian source
read-only and do not portray `pending` as an automatic background job. No frontend deploy in this task.
