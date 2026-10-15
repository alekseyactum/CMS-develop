# Review office city rollout

Date: 2026-10-15.

## Scope

The owner approved deploying the backend review office city change to develop and release.
The contract is defined in [the reference data model](reference-data-and-runtime-model.md#review-office-city-in-public-cards).

National practice, service and problem review cards expose the linked office region's trimmed
`public_name` in the exact page locale as `officeCity`. Missing relations or translations produce
`null`, without a fallback to another locale, office name, address or lawyer location. Regional and
personal lawyer pages always return `null`. This is the office city, not the author's residence.

Selection, ordering, review limits, aggregate rating and author JSON-LD remain unchanged. The same
projection covers fresh runtime inspection, preview, publication and scoped review refresh. City
changes are captured transactionally and reach national consumers in affected locales with the
normal review delay; they do not publish unrelated sections or authoring drafts. Old snapshots
without the field remain readable; missing and null are equivalent for no-op comparison.

No frontend change, database migration, content write, forced page rebuild, new queue, scheduler,
IAM, secret, runtime mode or deployment pipeline change is included. The existing build updates the
service and job images but does not execute migration or publication jobs. Deployment alone does
not rewrite existing snapshots; the city appears when reviews are next assembled normally.

## Source

| Environment | Feature commit | Previous commit | Previous ready revision |
| --- | --- | --- | --- |
| develop | `a39fb63310533e6a7530a377f1b3eeb7df128f24` | `0cfc74c3935611e6e3affe4c6b251bed064e24fe` | `cms-back-develop-00322-68d` |
| release | `426316c7f4b6dcda41ed7e2a1398d1d9f411c0aa` | `ffad853892b00f44e51371efde26a229e2f457fc` | `cms-back-release-00111-sz6` |

Each feature commit contains exactly 19 source, test and backend documentation files. Release
received a focused cherry-pick; stable patch IDs match. Existing environment-specific differences
were retained. Working branches are `codex/lawyer-profile-direct-practice` and
`codex/lawyer-profile-direct-practice-release`; deployment branches are `develop` and `release`.

## Local verification

Both commits passed the production TypeScript build and complete test-source compilation after
their working-branch push. Regression covered 137 spec files across runtime-resolvers, stale-refresh,
reference-data, structured-data, section-publication, sections-persistence and page-payloads.

- Develop: 1,941 passed, one existing opt-in database test skipped, no failures.
- Release: 1,940 passed, the same database test skipped, no failures. The baseline contains one fewer test.
- Independent focused audit: 49 tests passed, including old/new event envelopes, writer transactions,
  national/regional/lawyer projection, missing/null no-op and scoped publication. These overlap the
  regression totals.

## Deployment verification

| Environment | Successful build | Ready revision |
| --- | --- | --- |
| develop | `dd23d4ad-69f0-4c83-bcf7-73ca520a9d2d` | `cms-back-develop-00323-7pp` |
| release | `cf0af669-4e41-4d73-ae44-60d0f68d02fd` | `cms-back-release-00112-plp` |

Develop was deployed and checked before release. Both ready revisions receive 100% traffic. The
exact `^develop$` and `^release$` Git triggers ran the existing pipeline; no trigger was changed.

Develop authenticated health/readiness returned 200, the expected commit/build and database status
`ok`. Admin review inspection was unavailable to the actual operator with 403 `CMS_USER_NOT_FOUND`;
no alternate identity or permission change was used.

Release authenticated health/readiness also returned 200 with the expected commit/build and database
status `ok`. Read-only Ukrainian runtime inspection confirmed:

- National practice page `6767a5f9-7826-4e68-bc43-8fa603469787`: 64 review items, all with a non-empty,
  trimmed `officeCity` string.
- Lawyer page `06d0300a-0205-4687-9aee-71dc6a93603e`: 15 review items, all with `officeCity: null`.
- Another inspected lawyer page had no reviews. No created regional practice, service or problem
  page was available in the bounded catalog checks; those contexts and RU/EN behavior are covered
  by local tests, not this live acceptance.

Inspection used the actual operator and GET requests only. No content or source data was modified.

Both publication-effect schedules remain `PAUSED`. Safe publication/refresh flags are unchanged:
`CMS_PAGE_REFRESH_READ_ENABLED=true`; no activation flag was added. Migration and publication jobs
received their environment's new build image without execution. Latest executions remain
`cms-back-develop-migrate-ngj5c`, `cms-back-release-migrate-fb2jm`,
`cms-back-develop-publication-effects-wpvl4` and `cms-back-release-publication-effects-wmpc5`.

The initial bounded ERROR-level log checks returned no entries. A subsequent smoke request for the
entire unfiltered service matrix returned 500; Cloud Run logged `Response size was too large`.
The bounded `/api/admin/pages?pageType=...&locale=uk&limit=100&offset=0` catalog and individual
runtime inspection requests succeeded. This exposed an unbounded-matrix response-size limitation,
not a failed review query. This rollout does not change the matrix implementation or fix that
limitation. A bounded check of the preceding revision's recent logs did not establish whether that
request had failed previously; no old revision was activated to reproduce it.

## Rollback boundary

Compatibility is asymmetric. The new backend reads old snapshots and events, but the preceding
backend's closed validators reject cards containing `officeCity` and the paired
`membershipChanged`/`officeCityLocales` extension to `review_scope` events. Once such data exists,
do not simply revert to the previous image: retain compatible readers in a forward fix, or explicitly
authorize pausing refresh until a compatible reader is restored. Do not delete events, strip fields
or mass-republish content to accommodate an old reader. No rollback has been performed.

## Manual check

Inspect a fresh national practice, service or problem review section with a linked office and an
available region translation. Confirm `officeCity` matches the page locale. Inspect the corresponding
regional page and a lawyer page: their review items must contain `officeCity: null`. Missing office,
region or localized name also yields null. The frontend should display only a non-empty supplied
value and tolerate the absent field in an older snapshot. Frontend rendering remains separate work.
