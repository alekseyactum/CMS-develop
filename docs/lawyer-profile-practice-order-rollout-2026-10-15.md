# Lawyer profile practice ordering rollout

Date: 2026-10-15.

## Scope

The owner approved deploying the localized practice ordering change to CMS-back develop and release.
The profile's `practices[]` list now sorts by its displayed title in the page locale (UK/RU/EN), then
score descending for collation-equivalent titles, then internal ID. Practice `sortOrder` no longer
controls this profile-only list. Existing title fallbacks, direct-practice qualification rules,
visibility and score >= 3 are preserved. The 100-item cap follows ordering; unselected rows do not
undergo public-route validation.

Selection refresh applies the same ordering after retaining captured practice titles, so unrelated
live name changes do not enter the published page. Other practice/lawyer lists and profile-only text
refresh retain their existing behavior. Backend contract documentation is in
`cms-back/docs/lawyer-page-runtime-backend.md`.

No frontend change, migration, content write, page publication/rebuild, scheduling, IAM, secret,
publication-mode or pipeline change is included. Deployment alone does not rewrite existing snapshots
or mark them stale; the new ordering appears in fresh previews and newly assembled publications.

## Source and deployment

| Environment | Fix commit | Build | Ready revision |
| --- | --- | --- | --- |
| develop | `0cfc74c3935611e6e3affe4c6b251bed064e24fe` | `b01d1f0e-733e-49c0-b1b2-edc39d9f8631` | `cms-back-develop-00322-68d` |
| release | `ffad853892b00f44e51371efde26a229e2f457fc` | `52e888b2-28d2-44f2-83d7-94f8c593a5b5` | `cms-back-release-00111-sz6` |

Both commits contain exactly six files: one shared sorter, runtime and selection-refresh changes,
their tests, and backend documentation. Release received only this focused change, preserving its
existing whitespace-tolerant SQL test assertion. Both codex branches and the deployment branches were
pushed. The unchanged Cloud Build triggers match exactly `^develop$` and `^release$`.

## Verification

Mandatory playbook preflight passed. Both exact commits passed production/test compilation and 266
targeted tests. The tests and production builds passed again after each environment's push. Coverage
includes all three locales, title fallback, numeric score/ID ties, capped selection, invalid unselected
rows, retained snapshot labels, replay no-op, and unrelated list/profile refresh boundaries.

Develop build succeeded and its ready revision receives 100% traffic. Authenticated `/api/health` and
`/api/ready` returned 200 with the expected commit/build and database status `ok`. Profile inspection
was unavailable to the actual operator: the admin matrix returned 403 `CMS_USER_NOT_FOUND`; no identity
substitution or permission change was used. A bounded ERROR-level log check for that revision returned
no entries.

Release build succeeded and its ready revision receives 100% traffic. Authenticated health/readiness
returned 200 with the expected commit/build and database status `ok`. Read-only runtime inspection of
the Ukrainian profile for lawyer 243 returned four practices in the approved localized title order,
all with scores >= 3. RU/EN matrices returned 200 but had no visible created lawyer page available for
inspection; locale behavior is covered locally. A bounded ERROR-level log check for the new revision
returned no entries.

No migration or publication job was executed. Latest executions remain
`cms-back-develop-migrate-ngj5c`, `cms-back-release-migrate-fb2jm`,
`cms-back-develop-publication-effects-wpvl4`, and `cms-back-release-publication-effects-wmpc5`.
Their images are updated by the normal build, without running the jobs.

## Rollback

| Environment | Previous source | Previous ready revision | Previous image build |
| --- | --- | --- | --- |
| develop | `88dd9b65f4a71f3bfa2e04d1d5a766b41d9cd68e` | `cms-back-develop-00321-s8w` | `4ee78987-e41a-4304-8b54-5604ad439923` |
| release | `0a2d436fd32f23e551f00423551a30f49c438959` | `cms-back-release-00110-lhf` | `64ccd6a6-937c-400d-b9c1-16c5847e3ef8` |

Preferred code rollback is a focused revert through the existing deployment pipeline, preserving newer
unrelated commits. No rollback or data restoration has been performed. Previously assembled snapshots
remain immutable; changing their captured order requires the normal explicit publication workflow.

## Manual check

Open a fresh lawyer-page preview. Compare the visible practice titles alphabetically in the selected
language; a higher score must not move a differently named practice ahead of the alphabetic order.
For equal names, higher scores come first. Compare published pages only after their explicit rebuild.
