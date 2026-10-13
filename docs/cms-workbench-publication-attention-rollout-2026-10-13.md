# CMS workbench publication attention rollout

## Approval and scope

The owner explicitly requested push and deployment to develop and release on 2026-10-13. Scope is
backend only: additive `publicationState` for current matrix rows, cells, composite groups and runtime
inspection. Validation counters and publication capabilities are unchanged. The existing lawyer-source
stale comparison additionally records known affected slot keys; unscoped historic reasons stay on the
page. Unknown freshness coverage remains explicit.

No schema migration, content save, page publication/rebuild, frontend deployment, secret/IAM change,
pipeline edit, scheduler activation or publication-mode transition is included. Reads used for smoke
do not call reference list/detail GETs that create translation skeletons. Operator identity is not
substituted when administrative access is denied.

The agreed UI policy is in [the authoring task](cms-front-page-authoring-task.md#matrix-publication-accent-contract).
The API contract accompanies the backend feature in `docs/workbench-publication-state-2026-10-13.md`.
Frontend integration remains necessary; deploying this additive backend field alone does not change
the visible rails or remove the frontend's validation-color override.

## Sources and promotion

| Environment | Previous source | Deployed candidate |
| --- | --- | --- |
| develop | `5a29eb004f662ba211dfb6385990254e6ad1bb7b` | `b68ee8b3822b90ab2f5db1105e8cbd1770ebb488` |
| release | `954aa0607b93800bc26e30991a4b70bb8cc146bc` | `ce31fce38ddc73b7bd96280fcc24e110ea32f27f` |

Repository: `re-actum/cms-back`. Working branches:
`codex/workbench-publication-attention` and `codex/workbench-publication-attention-release`.
Both working branches and the corresponding environment branches were pushed without force.
Specification commit `2abb42d` was already pushed to `alekseyactum/CMS-develop`, branch
`codex/tz-2-to-tz-3-handoff`.

Release is a focused cherry-pick, not a merge of develop. Compatibility adjustments preserve the
release baseline: no develop-only structured-data DTO imports or `withStructuredDataCoverage` call,
and no fallback to develop's catalog `structuredDataStale` flag. Both environments still consume the
existing explicit runtime stale-reason records. No pipeline, migration or dependency file changed.

## Preflight and verification

The governing playbook preflight passed for the approved operator and `composite-ally-360719` before
cloud reads. Existing Cloud Build triggers were verified as exact `^develop$` and `^release$` filters,
using their existing environment YAML files in `europe-central2`. The two one-minute publication
schedulers were `PAUSED` before deployment.

Local verification:

- Develop production/test compilation passed. Full post-push suite: 2276 passed, 1 existing opt-in
  skip, 0 failed (2277 tests). Profiled feature suites also passed 267 tests before promotion.
- Release production/test compilation passed. Full suite: 2258 passed, 1 existing opt-in skip,
  0 failed (2259 tests). Post-push focused suites passed 253 tests.
- Full suites ran with loopback access for existing local HTTP tests. No real database is used by
  these test doubles. Earlier sandbox-only HTTP failures were successfully rerun outside the sandbox.
- Whitespace checks passed. Frontend/editor acceptance is not claimed by backend tests.

## Develop acceptance

Build `ad583d62-220b-42af-baa5-9369fd8cd88b` succeeded at `2026-10-13T17:23:41.868671Z`.
Ready revision `cms-back-develop-00315-rfh` has 100 percent traffic and the expected source SHA.
Authenticated `/api/health` and `/api/ready` returned 200, matching source/build IDs and database `ok`.
Live OpenAPI exposes `WorkbenchPublicationStateDto`, its reasons and all five states, with the field
on row, cell and runtime inspection models.

The actual operator's lawyer-matrix GET returned 403. No additional access was granted and no other
identity was supplied. Live develop administrative acceptance remains unverified. A bounded
ERROR-or-higher query for this revision returned no entries at verification time.

## Release acceptance

Build `271eca4d-f848-4c4b-b346-46d858666738` succeeded at `2026-10-13T17:32:15.000183Z`.
Ready revision `cms-back-release-00104-9rj` has 100 percent traffic and the expected source SHA.
Authenticated health/readiness returned 200, matching source/build IDs and database `ok`. Live OpenAPI
exposes the new models and row/cell/inspection fields.

The actual operator's lawyer matrices returned 200 for `uk`, `ru` and `en`. Each had 24 rows and 120
cells; every row and cell carried `publicationState`. No validation-heading reason leaked into the
publication reasons. Ukrainian rows comprised 21 `needs_attention` and 3 `published`; the two other
locales each reported 24 `missing_structure` rows. No row reported unavailable snapshot metadata.

The six observed Ukrainian warning cells each had the separate publication reason
`FIRST_PUBLICATION_REQUIRED`; none had unexplained publication attention. There was no published
warning-bearing cell in the observed data, so that specific green-with-warning scenario is covered
by local tests, not claimed as a positive live-data test. One read-only `lawyer_profile` runtime
inspection returned `publicationState.state: published`, zero validation issues, and a normalized row.
No payload contents, names or record identifiers were logged.

Both environments' migration and publication-worker jobs use their matching successful build images
and retain their saved Node entry commands. No job was executed. Both publication schedules remain
`PAUSED`. A bounded ERROR-or-higher query for the new release revision returned no entries at
verification time. Log checks are point-in-time smoke, not continuous monitoring or a load test.

## Rollback

Immediate pre-rollout ready revisions:

- Develop: `cms-back-develop-00314-gm9`, build `af579b7f-bfcc-4548-90ab-714f59bf8d66`.
- Release: `cms-back-release-00103-xb2`, build `87226864-5f01-44c3-aea9-0e1f7cae6b1c`.

Prefer an approved focused git revert or forward fix through the same deployment pipelines. Emergency
traffic rollback requires explicit approval. No schema/data restore or secret rotation is needed for
this change. Retain existing media keys, publication mode, content and paused schedules. Newly recorded
optional stale-reason metadata is backward compatible; do not delete it to roll back the API.
