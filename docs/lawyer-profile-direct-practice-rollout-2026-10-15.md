# Lawyer profile direct-practice qualification rollout

Date: 2026-10-15.

## Approved scope

The user approved pushing and deploying the backend fix to develop and release. Only the profile's
`practices[]` selector changes: active, resolved, visible direct practice qualifications with score >= 3.
Service/problem qualifications must not qualify their parent practice or increase its displayed score.
Both internal and external child IDs must be null. Other qualification consumers retain their rules;
the backend document `docs/lawyer-page-runtime-backend.md` lists those consumers.

No frontend changes, schema migrations, ERP sync, page publication, snapshot rebuild, IAM/secret
changes or scheduler activation are included. Existing snapshots keep their captured practice lists
until an explicit refresh/republication; fresh runtime inspection/preview uses the new selector.

## Source and rollout

| Environment | Previous source | Fix commit | Build | Ready revision |
| --- | --- | --- | --- | --- |
| develop | `fbae293a8f51d9adde8da5f00d58e8a4aeef723a` | `88dd9b65f4a71f3bfa2e04d1d5a766b41d9cd68e` | `4ee78987-e41a-4304-8b54-5604ad439923` | `cms-back-develop-00321-s8w` |
| release | `1043fac2ac842b7ae8fff2f20cf2a53093b9b305` | `0a2d436fd32f23e551f00423551a30f49c438959` | `64ccd6a6-937c-400d-b9c1-16c5847e3ef8` | `cms-back-release-00110-lhf` |

Both commits contain exactly three backend files: runtime selector, regression tests and backend
contract documentation. Release received the focused cherry-pick, not a merge of develop.
Existing GitHub push triggers and unmodified Cloud Build configurations perform deployment.
Governing playbook preflight passed for the authorized operator and project `composite-ally-360719`.

## Verification

- TypeScript test compilation, production compilation and 142 focused tests passed on both branches.
- Tests cover direct-practice predicates in UK/RU/EN and the published-profile selection refresh path.
- Before push, an additional local in-memory SQL fixture check passed 15 scenarios in each locale;
  this is a logic check, not a claim of live MySQL integration coverage.
- Develop build succeeded; the new revision receives 100% traffic. `/api/health` and `/api/ready`
  returned 200 with the expected commit/build, database ready.
- Develop admin matrix returned 403 `CMS_USER_NOT_FOUND` for the actual operator; no alternate identity
  or permission changes were used. Live functional inspection is therefore limited to release.
- Release build succeeded; the new revision receives 100% traffic. `/api/health` and `/api/ready`
  returned 200 with the expected commit/build, database ready.
- Before the release deploy, read-only runtime inspection of lawyer 243 returned practices 82/1/4/10
  with scores 4/4/4/3. Sports was already absent from that fresh runtime response; the screenshot is not
  treated as a same-time baseline.
- After deploy, the same UA profile returned practices 1/4/10/82 with direct scores 4/4/3/3. In particular,
  practice 82 no longer receives the aggregated score 4. Sports is absent. Page ID:
  `54aaabf4-5077-4326-aaf2-521cb2ddee38`. Published snapshot ID stayed
  `ee6b0eec-0a71-4b37-a9ce-ce472a5610f9`; it was not replaced by this rollout.
- Release matrices returned 200 in UK/RU/EN. Lawyer 243 has no created RU/EN page (`page: null`), so
  those runtime-profile inspections could not be exercised live. The initial smoke stopped on that
  missing-page assertion; a follow-up read by stable source ID confirmed this is absent test data, not
  an API failure. No page was created to bypass the limitation. Locale selectors are covered locally.
- Bounded post-deploy ERROR-level log checks found no records for either new service revision.

## Rollback baseline

| Environment | Previous revision | Previous image tag / build |
| --- | --- | --- |
| develop | `cms-back-develop-00320-p4j` | `f1d676f2-8d17-405c-9cf2-56ea78638ea2` |
| release | `cms-back-release-00109-w2c` | `d9a4ae98-eacb-498b-897b-ff840aeb3853` |

Preferred rollback is a focused revert of the environment's fix commit followed by its existing build
trigger, preserving subsequent upstream changes. No rollback has been requested or performed.

Before deployment, latest migration executions were `cms-back-develop-migrate-ngj5c` and
`cms-back-release-migrate-fb2jm`; latest publication-effects executions were
`cms-back-develop-publication-effects-wpvl4` and `cms-back-release-publication-effects-wmpc5`.
Post-rollout checks confirmed all four execution IDs unchanged, with job images updated to their
environment's new build and the expected Node migration/publication-effects entrypoints preserved.
Both `cms-back-*-publication-effects-1m` schedules remain `PAUSED`. No migration or publication job ran.

## Manual check

Open a new preview of lawyer 243. The practice list should use only direct scores >= 3. A practice with
direct score 1 must not appear because a child service/problem has a higher score. Verify a current
preview separately from an already published snapshot; deployment alone does not replace snapshots.
