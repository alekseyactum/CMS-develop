# Lawyer Pages Direct Navigation Deployment

## Scope

- User approved the analogous lawyer-pages navigation change on 2026-09-19.
- Repository: `re-actum/cms-back`.
- Commit: `651d1cc43d1fa430d6d04e4ffaef63fbc0e3be70`.
- Previous deploy commit: `0be3c1d7db0ecc2cee1eb28f0d00d240e1dd7f3a`.
- The `lawyer_pages` group is a direct link to `/pages/lawyer_page`, with
  an empty `items` array. Its title and `pages.read` permission are unchanged.
- Matrix diagnostics, attention, and publication counters now belong to the
  group itself, instead of its redundant child. No double counting.
- No frontend source changes or frontend deployments, database migrations, or
  content changes. The user reiterated the backend-only scope during rollout.
- Deployment uses the existing develop/release Cloud Build push triggers.
  Pipelines, IAM, secrets, and service configuration are not changed by this fix.

## Verification

- GCP preflight passed for `composite-ally-360719`.
- TypeScript test compilation passed.
- All 18 scoped admin-navigation tests passed, including after the develop push.
- The generated backend group was passed through the existing frontend adapter
  and route utilities for `uk`, `ru`, and `en`, with indicators on and off.
- Verified: leaf rendering, locale-aware route, active-item matching, permission
  metadata, unchanged counter values, no duplicate totals, and no lawyer summary
  request when indicators are disabled.
- The existing permission exclusion test passed.
- Before deployment, the release API returned one nested item, 22 errors, zero
  warnings, 23 possible lawyer pages, one published and 22 not created.

## Develop

- Cloud Build: `337ed717-e6f6-4f34-943c-b897a7723dc6`, `SUCCESS`.
- Active revision: `cms-back-develop-00293-7mw`, 100% traffic.
- Authenticated `/api/health`: `ok`, reporting commit `651d1cc43d1fa430d6d04e4ffaef63fbc0e3be70`.
- `/api/ready`: `ready`.
- `/api/admin/navigation?locale=uk` passed with `includeIndicators=false` and
  `true`: direct lawyer route, zero children, unchanged permission/target/endpoint.
- Counters: four possible pages, four published, no diagnostics. The users menu
  remains a direct link as a regression check.

## Release

- Pushed the same verified commit. Cloud Build:
  `30e6e57e-8196-4e2e-aa54-2b29e1701e37`, `SUCCESS`.
- Active revision: `cms-back-release-00082-ctj`, 100% traffic.
- Authenticated `/api/health`: `ok`, reporting commit `651d1cc43d1fa430d6d04e4ffaef63fbc0e3be70`.
- `/api/ready`: `ready`.
- `/api/admin/navigation?locale=uk` passed with `includeIndicators=false` and
  `true`: direct route, zero children, retained permission/target/endpoint.
- Counters match the predeployment baseline exactly: 22 errors, zero warnings,
  23 possible pages, one published, 22 not created, zero unpublished created
  pages, and no attention flags. These values now belong to the direct entry.
- The users entry remains a direct link as a regression check.
- Both deploy branches now point to the same backend commit. Existing pipelines
  update migration job images as part of deployment; no migration was executed.

## Rollback

Previous ready revisions, captured before deployment:

- Develop: `cms-back-develop-00292-89b`, 100% traffic.
- Release: `cms-back-release-00081-z7c`, 100% traffic.

Normal rollback: revert commit `651d1cc` on the affected deploy branch and let
its existing Cloud Build trigger deploy the revert. An explicitly approved urgent
rollback can route traffic to the previous ready revision, followed by a matching
Git revert. No database rollback is required.

## Manual Acceptance

Reload CMS and click the top-level lawyer-pages entry. It should open the existing
lawyer-page collection in one click, without an expand arrow or nested item.
Diagnostics and publication counts should still be visible when enabled.
Live browser interaction is not automated by this rollout; verification uses the
authenticated API and the existing frontend adapter/route utilities.
