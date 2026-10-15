# Editorial images and contributors rollout

Date: 2026-10-15.

## Scope

The owner approved deploying the editorial detail media and contributor fix to CMS-back develop,
then release. The public contract is defined in
[the editorial specification](editorial-content-specification-2026-08-23.md).

Fresh blog, media and case page assembly adds image URLs and named contributor objects to the
public payload while retaining the authored media IDs and lawyer references. Preview, legacy
publication and rebuild use the same resolver. Exact publication freezes the resolved presentation
in the prepared plan and does not reread live media or lawyer data when committing it. Public
JSON-LD respects the same visible contributor set when structured data is enabled.

This rollout includes no migration, frontend change, source content edit, snapshot rewrite or forced
republication. Existing published snapshots retain their old payload. The frontend must consume the
new `imageUrl`, cover and contributor objects; deployment alone does not change an old renderer.
Later changes to lawyer names/photos do not yet trigger an automatic editorial-detail refresh.

## Source and local verification

| Environment | Feature commit | Previous commit | Previous ready revision |
| --- | --- | --- | --- |
| develop | `3dc2fdbb96feb0e888a88109ba1b68dd5d02911d` | `a39fb63310533e6a7530a377f1b3eeb7df128f24` | `cms-back-develop-00323-7pp` |
| release | `efdd96bcc63944e13773c8fa21a81bb608dd93d9` | `426316c7f4b6dcda41ed7e2a1398d1d9f411c0aa` | `cms-back-release-00112-plp` |

Each feature commit changes 13 source, test and backend documentation files. Release received a
focused cherry-pick; added and removed lines match for all 13 files. Two lifecycle files have
different surrounding code because develop already has a separate inspection feature. No whole
develop branch merge was performed. The specification was pushed as `99891f7` to the documentation
working branch `codex/tz-2-to-tz-3-handoff`; an unrelated local `AGENTS.md` edit was preserved.

Production and complete test-source compilation passed in both worktrees. After push, production
checks and five focused test files passed: develop 176 tests, release 169. The difference is seven
pre-existing develop-only inspection tests. Before commit, the full develop regression covered 257
test files and 3,120 tests: 3,119 passed and one opt-in database test was skipped. Three localhost
HTTP suites initially failed under the sandbox and passed outside it (26 tests); no code change was
needed. The later portability-only test adjustment passed complete compilation and the focused suites.

## Deployment verification

| Environment | Successful build | Ready revision |
| --- | --- | --- |
| develop | `587cdc79-68d1-4aee-ac3c-f6e44539ff81` | `cms-back-develop-00324-pvv` |
| release | `7f38fc5d-4055-4634-97e5-b199b4a816c3` | `cms-back-release-00113-jwx` |

The exact branch triggers deployed develop first, then release after develop health verification.
Both ready revisions receive 100% traffic. Authenticated `/api/health` and `/api/ready` returned 200,
the expected commit/build identifiers and database status `ok` in both environments. Bounded
ERROR-level log checks on the new revisions returned no entries.

Develop admin inspection returned 403 `CMS_USER_NOT_FOUND` for the actual operator; no alternate
identity or permission change was used. On release, bounded catalog reads and the read-only
`POST /api/admin/pages/{pageId}/preview` payload assembly succeeded for Ukrainian blog page
`d483b545-24f5-4411-ac6e-b09693679efb`: all five image blocks had resolved image URLs, the cover
resolved, and the payload contained one author and a legal reviewer. The smoke check recorded only
counts and identifiers, not signed URLs or credentials. It did not fetch image bytes or verify the
frontend renderer. No created media or case page was returned by the bounded catalog queries;
those paths remain covered by local tests rather than live acceptance.

The preview endpoint used here assembles a response without saving a preview ticket, section or
snapshot. No content was published. The pre-existing pipeline updated the service and migration/
publication-effect job images, but did not execute jobs. Latest job executions remain
`cms-back-develop-migrate-ngj5c`, `cms-back-release-migrate-fb2jm`,
`cms-back-develop-publication-effects-wpvl4` and `cms-back-release-publication-effects-wmpc5`.
Both old publication-effect schedules remain `PAUSED`. Runtime flags, IAM, secret references,
triggers and pipeline files were not changed.

## Rollback boundary

The previous ready revisions above are the rollback targets. No database rollback is required.
Compatibility of prepared exact plans is asymmetric: new code reads old plans, but the previous
binary cannot read a new capture containing `editorialPresentation`. Before rollback, finish or let
those plans expire, then prepare fresh plans on the compatible revision. A forward fix retaining
compatible readers is preferable if editors have active new plans. Do not delete plan data or strip
fields to make an old binary accept it. No rollback was performed.

## Branch differences after this change

There is no substantial release-only feature missing from develop. The real remaining functional
difference is develop-only JSON-LD readiness and coverage, introduced in `d67326f` on 2026-10-05 and
intentionally excluded from the 2026-10-06 release merge `459cf63`.

Develop additionally provides:

- `GET /api/admin/page-workbench/pages/{pageId}/structured-data-readiness`: explicit read-only
  validation of a publication candidate, without publishing it.
- `row.structuredData` coverage information in workbench rows and summaries. Ordinary reads do not
  trigger the expensive candidate assembly; explicit inspection returns its diagnostics and
  corresponding `canPublish` result.
- A `JSON_LD_STALE_DEPENDENCY` attention reason when the published structured-data stale flag is set
  and no runtime reason already explains it.
- The associated tests and documentation.

The exact tree difference is 17 files: 10 production TypeScript files, five tests and two documents.
Release's heading diagnostic `path` addition already has an equivalent in develop. SQL test
whitespace and test-order differences are not separate product features. Migrations, dependencies,
Docker/Cloud Build, editorial presentation, stale refresh, reference data and the main runtime
resolver match between these commits.

Runtime configuration also intentionally differs: JSON-LD is enabled for `home_page` only on release;
develop additionally enables practice collection, practice, service and problem pages. This rollout
does not expand either environment's enabled types; editorial JSON-LD remains disabled in both.

The next decision is whether to promote the current readiness/coverage implementation to release
as a separate scoped change. Check its read-only behavior, exact-publication compatibility, matrix
query cost and frontend handling of `not_checked` before promotion. No migration or content edit is
required by the current code difference. After alignment, a single develop-to-release promotion
path would avoid accumulating equivalent commits under different SHAs. No synchronization change
was included in this deployment.

## Manual acceptance

After the frontend mapper is updated, preview an article containing a body image, a cover and an
assigned visible lawyer. Confirm actual image URLs and the author's localized name; CMS authoring
must still save IDs rather than generated objects. Publish the same selection and compare its
snapshot with preview. Missing media or an unavailable contributor must not produce fabricated
URLs, private CMS user data or a substitute author. A case's coauthor must not be promoted when its
explicit primary author cannot be resolved.
