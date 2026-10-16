# CMS stale refresh activation — 16 October 2026

## Authorization and boundary

The owner requested completion after the real ERP caller began receiving HTTP 200 `disabled`
from CMS release. The owner confirmed a write/publication-free window, including stopped local
backends using the shared databases. Existing history and content must be preserved.

ERP release calls were observed at 02:00, 02:05 and 02:10 UTC. No develop dispatch call was found
in the preceding day. One ERP runtime targets one configured CMS URL; release recurrence is not
evidence for develop. Develop remains capture-only until its own recurring caller is verified.
This task does not change ERP scheduling, IAM, secrets, schemas or public access.

## Preflight evidence

Governing playbook preflight passed for the expected operator and project. Both backend services
initially had only refresh reads/authentication configured; both CMS frontends defaulted to legacy.
All six CMS/backend/site services had one ready revision at 100% traffic, without old revision tags.
Both old publication-effects schedules remain paused.

Read-only inspections used temporary execution arguments on the existing migration jobs, **not**
the migration runner. Saved job definitions were not changed:

| Environment | Inspection execution | Result |
| --- | --- | --- |
| develop | `cms-back-develop-migrate-twzkc` | eligible; `legacy/0` |
| release | `cms-back-release-migrate-8kzfk` | eligible; `legacy/0` |

Both reports: zero old operations/plans/effects/transitions, one valid writer singleton, no missing
editorial locale groups, invalid current heads or editorial projection mismatches. These inspections
did not change writer mode or content. Release refresh queue and pending source-event counts were
zero; automatic pause was false, default source delays 30 minutes, expected caller interval 5 minutes.

## HTML cache decision

Exact deployed site sources: develop `d780ee59d10294eeaa8c344748a17994e714957f`, release
`e1391617cd43a99fbe5ab0f7f2961f129b4329c7`. Their page/layout/resolver fetches use no-store;
no persistent HTML caching override was found. Fresh cloud inventory found no serverless NEG or
domain mapping targeting either new site service. Existing CDN-enabled asset backends target the
old site, not these services. Sitemap and asset caches are separate from the HTML-page obligation.

Actual authorized-browser HTML headers remain unverified: the available in-app browser could not
open the protected site. The owner explicitly accepted proceeding on deployed-source/topology
evidence and will check the updated page. Configure origin `no_store` and CDN `absent`; do not
pretend a purge was sent. Adapter results should be `not_applicable`. Do not configure the existing
tag-revalidation endpoint as a page-refresh cache-delivery receiver.

## Capture-first deployment

The scoped backend change enables all five capture flags, read access and explicit cache modes.
Worker and manual commands remain false until the coordinated exact-mode transition. Normal
pipelines preserve these values; saved jobs do not inherit API flags. No startup operator is added.

| Environment | Commit | Build | Ready revision |
| --- | --- | --- | --- |
| develop | `0e40eccb53f4b1e35f9af48f9e7d935d5f36b367` | `7877c044-7546-480f-b56d-53d45e02897f` | `cms-back-develop-00326-8mw` |
| release | `2b9ff749d1d99668314b902246107edfc33c4356` | `2044ddad-360a-45b6-8f7a-d3cce15e69cb` | `cms-back-release-00115-z5f` |

Both builds succeeded and health/ready confirmed the expected sources, with databases healthy.
Both ready revisions serve 100% of traffic. The bounded release ERROR-log check returned no entries.
Operator and rollout tests passed 45/45 in each checkout after push.

CMS-front exact-mode configuration is prepared independently in each environment worktree, without
UI changes. Both targeted suites passed 8/8, changed-file formatting and ESLint passed, full ESLint
passed. Existing whole-repository formatting failures affect 899 develop and 843 release files;
unrelated files were not reformatted. Frontend deployment and exact cutover have not occurred.
The owner accepted the HTML-header verification limitation; the separate request to deploy the
configuration-only frontend change despite unrelated formatting failures is still awaiting an answer.
Do not infer that second approval from the first one. Worker and commands remain disabled and the
writer remains `legacy/0` in both environments. The final release-only admission patch is prepared
locally but is not committed or pushed; never deploy it before the guarded writer transition.

## Acceptance and rollback boundaries

An empty successful worker pass and heartbeat prove admission/recurrence, not source-to-page refresh.
Do not fabricate content changes solely to claim end-to-end acceptance. Observe a real subsequent
source event through demand, execution, journal and cache outcome, preserving unrelated drafts.
Dispatch is a bounded global run, not a page-scoped test command.

Before exact mode, capture-only deployment is reversible through the normal pipeline. After exact
mode, first stop new worker/command admission if necessary and preserve accepted work/history.
Do not restore only frontend legacy mode or an unfenced old backend. A writer-mode reversal requires
the separate reviewed drain/CAS/reconciliation procedure; the initial operator is not a rollback tool.
