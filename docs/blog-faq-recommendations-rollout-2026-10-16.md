# Blog FAQ and recommendations backend rollout 2026 10 16

The approved backend changes are committed, pushed and deployed to develop and release. They add
optional Blog FAQ, Blog-only aside recommendations with scoped scheduled refresh, and a hard limit
of five publications on a lawyer page. This rollout changes neither frontend code nor existing
content and requires no database migration.

## Source and deployment evidence

| Environment | Backend commit | Successful build | Ready revision receiving 100 percent traffic |
| --- | --- | --- | --- |
| develop | `27cb4066813bcab72ed219aba978ba333430682c` | `a6be94e3-3039-475f-b050-bb37779920be` | `cms-back-develop-00327-g6q` |
| release | `0444045c0aef8195382d65721f3708542fe1e48d` | `7ecf50ba-be4c-4cae-9a27-c1ef540c9972` | `cms-back-release-00117-f4g` |

Develop completed at `2026-10-16T04:33:10.806029Z`; release completed at
`2026-10-16T04:38:42.702851Z`. Release received only the feature commit by cherry-pick. Both changes
contain the same 57-file patch, verified independently of branch-specific surrounding code. Build
configuration, migrations and package configuration were not changed. The working branches
`codex/lawyer-profile-direct-practice` and `codex/lawyer-profile-direct-practice-release` were also pushed.

The backend contract is [blog-faq-recommendations.md](https://github.com/re-actum/cms-back/blob/develop/docs/blog-faq-recommendations.md).
The product decisions remain in the [editorial specification](editorial-content-specification-2026-08-23.md)
and [implementation plan](editorial-content-implementation-plan-2026-08-23.md).

## Verified behavior and boundaries

- Production builds and test TypeScript compilation passed on both branches.
- Develop full suite: 3205 passed, no failures, one skipped; post-push focused suite: 182 passed.
- Release full suite: 3187 passed, no failures, one skipped; post-push focused suite: 176 passed.
- The skip is the existing opt-in MySQL review-diagnostics test without its test database configuration.
  Dedicated real-MySQL query/concurrency/load coverage was not run.
- Authenticated `/api/health` and `/api/ready` returned 200 in both environments with the expected
  commit/build and database readiness `ok`. Bounded ERROR-level log reads for each new revision
  returned zero entries during verification.
- Release `/api/admin/page-schemas/blog_page` returned 200. It includes `blog_faq`,
  `blog_recommendations` and `blog_recommendations_items` once each; FAQ is disabled by default and
  both editable sections publish with their owner page.
- Release `/api/admin/page-refresh/summary?locale=uk` returned 200 with commands enabled, automatic
  scheduling not paused and a healthy heartbeat. The observed scheduled tick was
  `2026-10-16T04:40:03.523Z`. At that observation there were 18 pending discovery events, no retry or
  attention events, and no queued or attention pages. This is a point-in-time observation, not proof
  of an end-to-end new-content refresh.
- The actual operator's develop admin reads returned 403 `CMS_USER_NOT_FOUND`. No impersonation,
  access change or content publication was used to bypass this membership boundary.

## Runtime settings preserved

Develop retains refresh read/capture enabled and worker/commands disabled. Release retains worker
and commands enabled. The existing `no_store` origin and `absent` CDN modes remain unchanged.
No dispatcher was invoked manually and no scheduler or writer mode was changed.

The Blog FAQ graph implementation does not enable Blog JSON-LD operationally: the existing page-type
allowlists exclude Blog in both environments. Develop still allows home and service-tree types;
release still allows home only. Enabling additional types is a separate runtime decision.

The normal builds updated migration-job and publication-effects-job images to their environment's
new build. Neither job was manually executed. Both old one-minute publication-effects schedules
remain `PAUSED`; they are distinct from the existing ERP-driven five-minute page-refresh dispatcher.
The develop migration job retains older APP source/build labels because its existing pipeline updates
only the image. Its image is current; label cleanup is not part of this feature rollout.

## Content adoption and scheduled refresh

Existing published snapshots are not rewritten. Normal article publication adopts the new sections;
normal lawyer-page publication or applicable scoped refresh adopts the five-card cap. Frontend editors
and renderers remain Yuri's integration task.

Recommendations contain at most three published Blog articles in the same locale; Cases and Media are
excluded. Automatic selection uses published thematic scope, including new candidates outside the
previous visible cards. Manual selection preserves order and does not fill gaps automatically.
Valid legacy articles lacking an immutable editorial-card capture are omitted with a diagnostic
before the limit; corrupt captures remain errors, with no live-reference or draft fallback.

The `blog_recommendations:v1` refresh consumer uses the existing queue, lease/CAS, journal, retry and
cache pipeline. It changes only recommendation cards and their captured source digest, preserving
body, FAQ, drafts, unpublished settings and editorial dates. Aside-only refresh does not generate a
new semantic article change or a refresh loop. The new consumer can discover historical related-content
events in bounded batches; legacy snapshots without the new slots are skipped, not automatically upgraded.

There is still no native page unpublish/archive command. A future command or authorized maintenance
removal must emit the editorial BEFORE-to-null event transactionally. Direct SQL removal is not an
automatic change-capture path.

Manual acceptance after frontend integration should publish a test article through the normal workflow,
check FAQ after the body and the three-card aside, then change a related published article and confirm
the existing scheduled queue refreshes only recommendations while preserving owner drafts. Check the
lawyer block with more than five eligible publications. These content writes are not part of this rollout.

## Rollback boundary

Previous revisions were `cms-back-develop-00326-8mw` (source `0e40eccb`) and
`cms-back-release-00116-2j7` (source `22418b9e`). No rollback was required.

Prefer a focused forward fix once new recommendation captures or refresh operations exist: the previous
binary does not know the new consumer/contract. Any emergency rollback must separately assess in-flight
operations and retain queue/history/content data. Do not reverse exact-writer mode, delete service tables
or disable the already-running release scheduler as an incidental part of a code rollback.
