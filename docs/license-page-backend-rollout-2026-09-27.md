# License page backend rollout — 2026-09-27

## Authorization and source

Completed backend-only rollout to develop and release, explicitly approved by the owner.
Mandatory playbook preflight passed for project `composite-ally-360719`, region `europe-central2`.

Repository: `re-actum/cms-back`.
Source commit: `020a86c448897d6f5f21ad4bb93c322447a7f009`.
Feature branch: `codex/license-page-backend`.
Previous common develop/release commit: `c085375539cfebb62438c02729d6ddf8fb185f1b`.

Develop was deployed and verified first, then the exact same source commit was promoted to release
by a normal fast-forward push. Existing repository push triggers ran the existing pipelines.
Remote feature/develop/release heads all match the source commit; the backend worktree is clean.

## Delivered scope

- UK-only `lawyer_license_page`, national route `/license`.
- SEO plus seven required, non-disableable page-owned sections: hero, roles, model, support,
  formats, expectations and application. Content sections publish with the page.
- Authoring/workbench validation, media hydration and readiness guards, publication/rebuild support.
- CMS navigation targets the UK page from every CMS language; no RU/EN authoring variants.
- Career banners may target the published UK License page across locales.
- Server-owned CTA/form descriptors. Application submission remains disabled with a null endpoint;
  actual email and ERP delivery is a separate prelaunch task.
- Generic independent section publication guards persisted page-owned/with-page bindings against
  a client-supplied schema bypass.

No frontend deployment, database migration, database/content edit, page publication/rebuild,
redirect creation/activation, IAM, secret/environment, domain or pipeline changes were performed.
Existing pipelines update migration-job image/config; they did not execute migration jobs.

## Deployment evidence

| Service | Successful build | Ready revision / traffic | Previous ready revision |
| --- | --- | --- | --- |
| cms-back-develop | `fdaaecc8-9e18-4487-b2f7-d210b7f6fdc2` | `cms-back-develop-00298-8d5` / 100% | `cms-back-develop-00297-zr9` |
| cms-back-release | `bc538d8e-5685-4603-9029-70eaeae1e9c8` | `cms-back-release-00087-znd` / 100% | `cms-back-release-00086-jbs` |

Develop build finished at `2026-09-27T16:58:58.724767Z`.
Release build finished at `2026-09-27T17:04:41.110659Z`.

## Verification and limitations

- Before push and again after push on the exact source commit: typecheck, production build and
  full test suite passed. 1,113 tests / 124 suites, zero failures/skips.
- Both environments: GET `/api/health` => 200/ok; GET `/api/ready` => 200/ready with database ok.
  Reported commit and build IDs match the source and the corresponding successful pipeline.
- Develop admin schema read returned 403 `CMS_USER_NOT_FOUND` for the actual operator.
  No identity or CMS-role changes were made; successful live admin-functional smoke is not claimed
  for develop.
- Release admin schema read returned 200: only locale uk, route /license, no regional routes,
  eight required non-disableable slots (SEO plus seven content slots).
- Release UK License workbench read returned 200 with one row and locales [uk].
  RU and EN reads each returned 400 `PAGE_WORKBENCH_LOCALE_UNSUPPORTED`.
  These were read-only matrix requests, not authoring/bootstrap/editor requests.
- Release navigation reads in UK/RU/EN each returned exactly one License item with
  href `/uk/admin/pages/lawyer_license_page`, target.locale uk and a UK workbench endpoint.
  These navigation reads did not request diagnostic indicators.
- Post-smoke severity >= ERROR queries scoped to each new revision over a bounded 15-minute
  freshness window returned no entries. This is point-in-time evidence, not continuous monitoring.

No test fixtures, publications or content edits were created for smoke. A completed frontend page,
published content, live image delivery, application sending and HTTP language redirects are not
claimed by this deployment.

## Handoff / manual verification

In CMS, open the License workbench from each content language; it must target UK. The frontend
editor and site rendering remain Yuriy's task. After that integration, create and fill the UK page,
validate SEO and seven sections, preview and publish it using the normal page workflow.
Once the target is published, explicitly prepare and activate the two registry redirects
`/ru/license` and `/en/license` to `/license`, after checking existing route ownership.
Deployment alone does not create these rules. Keep form submission unavailable until the separately
agreed email/ERP integration is implemented.

Backend contract and requirements are committed in cms-back:
`docs/license-page-backend-contract-2026-09-27.md` and
`docs/license-page-backend-requirements-2026-09-27.md`.

## Rollback

Preferred rollback: reviewed git revert of the source commit through the existing develop
verification and same-SHA release-promotion pipelines. This rollout has no database/content changes
to restore. Emergency traffic rollback requires explicit approval and may use the previous ready
revisions listed above, followed by a git-based correction.
