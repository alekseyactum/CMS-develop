# CMS Release Infrastructure Execution Plan - 2026-06-28

This document turns the release infrastructure architecture into an ordered implementation plan.

It is a planning checklist only. It does not approve or perform GCP changes. Any real work with Cloud Run,
Cloud SQL, Cloud Build, Secret Manager, Cloud Storage, IAM, DNS, certificates, IAP, or load balancers is
governed by `gcp-infra-playbook` and requires the required preflight before cloud state is read or
changed.

Primary architecture reference:

- `docs/release-infrastructure-architecture-2026-06-28.md`

GCP inventory reference:

- `docs/release-gcp-inventory-2026-06-28.md`

Governing playbook reference:

- `../gcp-infra-playbook/docs/projects/cms.md`

## Execution Goal

Create the `release` contour as the future production runtime while keeping it closed before the public
go-live window around mid-August 2026.

The first implementation must support:

- release Cloud Run services for `site-front`, `cms-front`, and `cms-back`;
- separate release Cloud SQL instance and empty `site_release` database;
- separate release media bucket;
- release secrets and runtime configuration without storing secret values in git or docs;
- git-based release deployment from `release` branches;
- closed CMS access through IAP and CMS permissions;
- closed/noindex public site preview before go-live;
- canonical first public host `https://actum.com.ua`;
- old public site remaining available as rollback/fallback during cutover.

## Phase 0 - Documentation And Approval Boundary

Status: completed for the initial Cloud SQL slice.

- [x] Create CMS release architecture document.
- [x] Synchronize release summary into `gcp-infra-playbook`.
- [x] Confirm this execution plan before real GCP work starts.
- [x] Confirm that the next step is cloud inventory/preflight, not resource creation.

Open operational decisions before resource creation:

- [x] Cloud SQL release instance name: `site-release`.
- [x] Cloud SQL initial sizing direction: mirror current `actum-strapi` after GCP inventory.
- [x] `release.actum.com.ua` is not required in the first infrastructure slice.
- [x] Release ERP/import path direction: controlled operator-run import into `cms-back-release`/`site_release`
  first; recurring `data-inside-migrator-release` can be added later if needed.
- [x] First release admin: `ap@modusmoses.com`.
- [x] Initial CMS/IAP access list:
  - `privatemailofap@gmail.com`
  - `yuriy.bishko@gmail.com`
  - `po@actum.com.ua`
  - `ap@modusmoses.com`
  - `jamaslov@gmail.com`
- [x] Interim secret rotation owner: `ap@modusmoses.com`.
- [x] Target public go-live window: approximately `2026-08-15`.

Operational decisions still needed during implementation:

- [x] Exact Cloud SQL baseline read from `actum-strapi`.
- [x] Final Cloud SQL create command approval.
- [ ] CMS role assignment for each initial user.

## Phase 1 - Preflight And Current-State Inventory

Goal: understand existing project state before creating anything.

- [x] Run the playbook GCP preflight from `gcp-infra-playbook`.
- [x] Record active gcloud project and authenticated account.
- [x] Inventory existing Cloud Run services relevant to CMS/develop.
- [x] Inventory existing service accounts relevant to CMS/develop.
- [x] Inventory existing Cloud SQL instances/databases relevant to CMS/develop.
- [x] Inventory existing Secret Manager names relevant to CMS/develop.
- [x] Inventory existing Cloud Storage buckets relevant to CMS/develop.
- [x] Inventory existing Cloud Build triggers relevant to CMS service repos.
- [x] Inventory existing load balancers, serverless NEGs, certificates, IAP settings, and DNS decisions if
  already present.
- [x] Save only non-secret findings into markdown.

Stop if:

- active project is not `composite-ally-360719`;
- authenticated account lacks required visibility;
- existing resources conflict with planned release names;
- playbook and CMS docs disagree.

## Phase 2 - Git And Build Surface

Goal: make release deployable from source control before runtime resources depend on it.

- [x] Confirm canonical service repositories:
  - `re-actum/site-front`
  - `re-actum/cms-front`
  - `re-actum/cms-back`
- [x] Create or verify `release` branches in each service repo.
- [ ] Decide whether branch protection is required before first release deploy.
- [x] Confirm Cloud Build config files for release builds.
- [x] Add `cloudbuild.release.yaml` to each service repo release branch.
- [x] Create or update release Cloud Build triggers:
  - `site-front-release`
  - `cms-front-release`
  - `cms-back-release`
- [x] Ensure triggers deploy from `release` branches only.
- [x] Ensure release build configs target release services instead of develop services.

Stop if:

- release branch does not contain the required runtime code;
- release trigger would deploy from the wrong branch;
- build config requires secrets that are not yet modeled.

Executed on `2026-07-14`:

- Created dedicated build identity `cms-release-build-runner`.
- Granted project roles `roles/cloudbuild.builds.builder`, `roles/artifactregistry.writer`, and
  `roles/logging.logWriter`.
- Granted `roles/run.developer` only on release Cloud Run resources:
  `site-front-release`, `cms-front-release`, `cms-back-release`, and `cms-back-release-migrate`.
- Granted `roles/iam.serviceAccountUser` only on release runtime service accounts:
  `site-front-release-runner`, `cms-front-release-runner`, and `cms-back-release-runner`.
- Created release triggers in `europe-central2`:
  - `site-front-release`, id `39cf2871-90be-466c-b9ed-25ab72d2a40c`;
  - `cms-front-release`, id `d689ee57-2a44-4194-83e0-dd99328b59a1`;
  - `cms-back-release`, id `237cd212-f0f3-44af-a681-0099b8a1c13d`.
- Test empty commits pushed to release branches triggered successful builds:
  - `site-front-release`: build `0066b087-68fc-4933-bf49-e6eee05e3913`, commit `cce327f`;
  - `cms-front-release`: build `1afaebd5-e613-4682-97bd-0fccaad0ae38`, commit `83af86a`;
  - `cms-back-release`: build `5a96d08e-6cd2-4f52-a90b-2cd0b3e2ffbd`, commit `ece032e`.
- Current ready revisions after trigger deploy:
  - `site-front-release-00003-cn7`;
  - `cms-front-release-00004-q8n`;
  - `cms-back-release-00004-4k6`.
- IAP remained enabled for both frontend services, unauthenticated frontend `/health` still redirects to
  Google OAuth, and fresh `ERROR` logs were empty after trigger deploy.

## Phase 3 - IAM And Service Accounts

Goal: isolate release runtime identities from develop.

Planned service accounts:

- `site-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com`

Checklist:

- [x] Create release runtime service accounts.
- [x] Grant each service account only required runtime permissions for this phase.
- [x] Grant `cms-back-release-runner` Cloud SQL access for the release database path:
  `roles/cloudsql.client` and `roles/cloudsql.instanceUser`.
- [x] Grant `cms-back-release-runner` write/manage access to release media bucket only.
- [x] Grant frontend runners access only to required runtime secrets/config.
- [x] Grant frontend runners `roles/run.invoker` only on `cms-back-release` for release server-to-server calls.
- [x] Ensure humans are not used as runtime identities.
- [x] Document non-secret IAM grants in playbook or CMS docs.

Stop if:

- release runner needs broad project-level roles;
- develop service accounts are being reused for release runtime;
- an IAM grant exposes release secrets or data to unintended services.

## Phase 4 - Cloud SQL Release Database

Goal: create a clean production-bound database boundary.

Confirmed:

- separate release Cloud SQL instance;
- instance ID: `site-release`;
- database: `site_release`;
- empty start;
- migrations create schema;
- data comes through ERP/import and CMS editing;
- approximately 7-day backup retention;
- Cloud SQL IAM authentication, not password runtime credentials.
- initial sizing mirrors current `actum-strapi`:
  - `MYSQL_8_0_43`
  - `ENTERPRISE`
  - `db-g1-small`
  - `ZONAL`
  - `europe-central2-b`
  - `10 GB` `PD_SSD`
  - storage auto-resize enabled
  - backups/binlog enabled, 7 retained backups / 7 days transaction logs
  - deletion protection enabled
- CMS release additionally enables `cloudsql_iam_authentication=on`.
- CMS release does not copy old `actum-strapi` public authorized networks by default.

Checklist:

- [x] Choose Cloud SQL instance name: `site-release`.
- [x] Read current `actum-strapi` settings after preflight.
- [x] Choose exact initial tier/storage/settings from the `actum-strapi` baseline.
- [x] Approve final Cloud SQL create command.
- [x] Create Cloud SQL instance in `europe-central2`.
- [x] Enable automated backups with about 7 days retention.
- [x] Create database `site_release`.
- [x] Create/authorize IAM database user for `cms-back-release-runner`.
- [x] Prepare release migration job, for example `cms-back-release-migrate`.
- [x] Ensure migrations are executed explicitly, not on normal Cloud Run startup.
- [ ] Before destructive or risky migrations, define backup/export or forward-fix path.

Executed on `2026-07-05`:

- `site-release` created as `MYSQL_8_0_43`, `ENTERPRISE`, `db-g1-small`, `ZONAL`,
  `europe-central2-b`.
- Initially created with private IP only: `10.89.62.17`.
- Deletion protection is enabled.
- Automated backups and binary logs are enabled with 7 days transaction log retention.
- `site_release` database was created with `utf8mb4` / `utf8mb4_unicode_ci`.
- Cloud SQL IAM DB user was created for
  `cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com`.

Post-create connectivity change on `2026-07-05`:

- Public IP was enabled for local Cloud SQL Auth Proxy access: `34.116.243.97`.
- Private IP remains enabled: `10.89.62.17`.
- Authorized networks remain empty.
- Cloud SQL connector enforcement is `REQUIRED`.
- SSL mode is `ENCRYPTED_ONLY`.
- This does not make MySQL password authentication technically impossible; Cloud SQL MySQL still has the
  built-in `root` user. The release security boundary is therefore:
  - no authorized public networks;
  - Cloud SQL Auth Proxy / Cloud SQL connector required;
  - IAM permissions only for approved principals;
  - DB privileges granted only to approved IAM database users;
  - no root password distribution through git, docs, logs, or chat.

Implementation note:

- Current `gcloud` uses `--retained-transaction-log-days=7`, not
  `--transaction-log-retention-days=7`.
- Current `gcloud sql instances create` accepts either `--region` or `--zone`; the executed command used
  `--zone=europe-central2-b` so the region is inferred.
- Current Cloud SQL IAM service account users must be created with the full service account email.
- On `2026-07-05`, MySQL DB privileges were granted to the IAM DB user with a one-time Cloud SQL SQL
  import, avoiding root password distribution:
  - `GRANT ALL PRIVILEGES ON site_release.* TO 'cms-back-release-runner'@'%'`
  - temporary GCS object and temporary Cloud SQL service agent bucket read grant were removed after import.

Stop if:

- DB credentials would be stored as plain secrets when IAM auth is available;
- migrations are configured to run implicitly on every service startup;
- develop data would be copied by default.

## Phase 5 - Secrets And Runtime Config

Goal: create release configuration boundaries without leaking values.

Planned project-specific secret names:

- `site-front-runtime-release`
- `cms-front-runtime-release`
- `cms-back-runtime-release`
- `cms-admin-auth-release`

Checklist:

- [x] Create secret placeholders or secret resources as needed.
- [ ] Add secret values only through GCP Secret Manager, never in git/docs/chat/logs.
- [x] Assign secret access only to the service accounts that need each secret.
- [x] Confirm runtime non-secret config:
  - `ENVIRONMENT=release`
  - `APP_ENV=release` or service equivalent
  - `CMS_BACK_URL`
  - `CLOUD_SQL_CONNECTION_NAME`
  - `DB_NAME=site_release`
  - `DB_IAM_USER=cms-back-release-runner`
  - `MEDIA_BUCKET=site-media-release`
  - noindex/robots mode before go-live
- [x] Confirm secret rotation owner.

Executed on `2026-07-05`:

- Created release Secret Manager containers with automatic replication and no recorded secret values:
  - `site-front-runtime-release`
  - `cms-front-runtime-release`
  - `cms-back-runtime-release`
  - `cms-admin-auth-release`
- Granted `roles/secretmanager.secretAccessor` only to the matching runtime service accounts:
  - `site-front-runtime-release` -> `site-front-release-runner`
  - `cms-front-runtime-release` -> `cms-front-release-runner`
  - `cms-back-runtime-release` -> `cms-back-release-runner`
  - `cms-admin-auth-release` -> `cms-back-release-runner`

Stop if:

- a secret value appears in markdown, command history snippets, logs, or chat;
- a frontend receives backend-only integration secrets;
- release service points to develop secrets.

## Phase 6 - Storage And Media

Goal: isolate release media from develop.

Planned bucket:

- `site-media-release`

Checklist:

- [x] Create release media bucket with region/location policy matching the project decision.
- [x] Grant write/manage access to `cms-back-release-runner`.
- [x] Avoid direct frontend write permissions.
- [ ] Confirm public media URL strategy before go-live.
- [ ] Confirm whether media delivery needs signed URLs, public object serving, or LB/CDN path later.
- [x] Keep release media fresh; do not copy develop media by default.

Executed on `2026-07-05`:

- Created `gs://site-media-release`.
- Location: `EUROPE-CENTRAL2`.
- Storage class: `STANDARD`.
- Uniform bucket-level access: enabled.
- Public access prevention: enforced.
- Soft delete retention: 7 days.
- Granted `roles/storage.objectAdmin` only to
  `cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com`.
- No develop media was copied.

Stop if:

- frontend service accounts need direct bucket write access;
- bucket naming conflicts with existing resources;
- public object strategy is enabled accidentally before approval.

## Phase 7 - Cloud Run Services And Migration Job

Goal: deploy the release runtime with closed access.

Planned services:

- `site-front-release`
- `cms-front-release`
- `cms-back-release`

Planned job:

- `cms-back-release-migrate`

Checklist:

- [x] Create/deploy `cms-back-release` with release runner and release DB/media config.
- [x] Create/deploy `cms-front-release` with release runner and backend URL.
- [x] Create/deploy `site-front-release` with release runner and backend URL.
- [x] Set min instances to `0` while the contour is closed.
- [x] Keep initial max instances conservative:
  - `site-front-release`: `3`
  - `cms-front-release`: `2`
  - `cms-back-release`: `3`
- [x] Restrict `cms-back-release` from public browser access.
- [x] Allow only approved service-to-service invocation paths.
- [x] Deploy/update `cms-back-release-migrate`.
- [x] Run migrations explicitly after confirming target DB.

Executed on `2026-07-05`:

- Updated `cms-back` release branch from current `origin/develop` and kept `cloudbuild.release.yaml`.
- Pushed `cms-back` release commits:
  - `8fa772e` merge current develop into release;
  - `732014c` fix release migration job Cloud SQL flag.
- Cloud Build `73926ddb-5e43-4218-8983-487fc673395d` built and deployed the first
  `cms-back-release` revision, then failed while creating the migration job because Cloud Run Jobs require
  `--set-cloudsql-instances`, not `--add-cloudsql-instances`.
- Cloud Build `4ef7402b-9819-4002-ba0c-a0fe044e74eb` succeeded.
- `cms-back-release` is Ready at `https://cms-back-release-2ubpwinuqq-lm.a.run.app`.
- `cms-back-release` uses:
  - service account `cms-back-release-runner`;
  - Cloud SQL instance `composite-ally-360719:europe-central2:site-release`;
  - `DB_NAME=site_release`;
  - `DB_IAM_USER=cms-back-release-runner`;
  - `MEDIA_BUCKET=site-media-release`;
  - min instances `0`, max instances `3`;
  - unauthenticated access disabled.
- `cms-back-release-migrate` job is Ready.
- Migration execution `cms-back-release-migrate-lps9f` completed successfully and applied migrations
  through `202607020001`.
- Updated frontend release branches from current `origin/develop`:
  - `site-front` release commit `61160f2`;
  - `cms-front` release merge commit `add9906`;
  - `cms-front` release fix commit `30c6bb6` makes production start honor Cloud Run `PORT`.
- Granted `roles/run.invoker` on `cms-back-release` to:
  - `cms-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`;
  - `site-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`.
- Cloud Build `834909b0-1226-4bee-8430-cde2cc81e574` built and pushed the first
  `cms-front-release` image, then failed deploy because the container started Next.js on port `3000`
  while Cloud Run expected `PORT=8080`.
- Cloud Build `e8a9a344-58d8-4c7b-a5b6-30bd36697251` successfully deployed `cms-front-release`.
- `cms-front-release` is Ready at `https://cms-front-release-2ubpwinuqq-lm.a.run.app`.
- `cms-front-release` uses:
  - service account `cms-front-release-runner`;
  - `CMS_BACK_URL=https://cms-back-release-2ubpwinuqq-lm.a.run.app`;
  - min instances `0`, max instances `2`;
  - unauthenticated access disabled.
- Cloud Build `7464d74c-6581-4360-af9c-ed24cb9e0d40` successfully deployed `site-front-release`.
- `site-front-release` is Ready at `https://site-front-release-2ubpwinuqq-lm.a.run.app`.
- `site-front-release` uses:
  - service account `site-front-release-runner`;
  - `CMS_BACK_URL=https://cms-back-release-2ubpwinuqq-lm.a.run.app`;
  - `INDEXING_MODE=noindex`;
  - min instances `0`, max instances `3`;
  - unauthenticated access disabled.

Stop if:

- `cms-back-release` becomes broadly public;
- frontend services point to develop backend;
- migration job points to develop DB;
- service deploy uses a non-release branch unexpectedly.

## Phase 8 - Load Balancer, IAP, Domains, And Closed Preview

Goal: create the release entrypoint without exposing the future public site early.

Recommended baseline:

- external HTTPS load balancer;
- serverless NEGs for Cloud Run services;
- IAP for CMS and closed release preview access;
- managed certificates and explicit hostnames;
- optional Cloud Armor/IP allowlist if reviewer IPs are stable.

Domain policy:

- first public canonical host: `https://actum.com.ua`;
- `www.actum.com.ua`, if attached, redirects to `https://actum.com.ua`;
- `actum.ua` is prepared as secondary/future migration domain, not first canonical;
- `release.actum.com.ua` is optional for closed preview and is not required in the first infrastructure
  slice.

Checklist:

- [x] Decide whether LB/IAP is created in the first slice or whether direct Cloud Run IAP is used only as
  a temporary bridge.
- [ ] Create serverless NEG/backends for required release services.
- [ ] Configure HTTPS LB and managed certificate(s).
- [x] Configure IAP access for `cms-front-release`.
- [x] Configure IAP or IP allowlist for pre-go-live public site preview.
- [x] Ensure `*.run.app` direct access does not bypass the intended boundary where final architecture
  supports ingress restriction.
- [x] Configure noindex response headers before go-live.
- [x] Configure `robots.txt` blocking policy before go-live.
- [x] Keep sitemap disabled, empty, or non-public before go-live.
- [ ] Confirm redirect behavior for `www` and any attached `actum.ua` host.

Stop if:

- the site is reachable publicly without IAP/IP boundary before go-live;
- noindex is absent while the preview is reachable;
- `actum.ua` becomes canonical accidentally;
- direct Cloud Run URL bypasses the perimeter unexpectedly.

Executed on `2026-07-11`:

- Chose direct Cloud Run IAP as the first temporary closed reviewer bridge for the release frontend
  services.
- This does not replace the recommended final release entrypoint: HTTPS LB + serverless NEGs + IAP remains
  deferred until the domain/DNS decision is ready.
- Existing project LB inventory showed a shared HTTPS LB already serving `actum.com.ua`, `www`, `strapi`,
  `erp`, and `tag` hosts on IP `34.160.235.199`; no release-specific LB objects were created.
- Cloud DNS inventory failed for the active account with missing DNS permissions, so DNS/domain work is
  deferred until permissions or external DNS ownership are clarified.
- Enabled direct Cloud Run IAP on:
  - `cms-front-release`;
  - `site-front-release`.
- `run.googleapis.com/iap-enabled=true` is set on both release frontend services.
- Cloud Run `roles/run.invoker` for both release frontend services is granted only to the Google-managed
  IAP service agent:
  `service-865011807785@gcp-sa-iap.iam.gserviceaccount.com`.
- IAP `roles/iap.httpsResourceAccessor` is granted on both release frontend services to:
  - `privatemailofap@gmail.com`;
  - `yuriy.bishko@gmail.com`;
  - `po@actum.com.ua`;
  - `ap@modusmoses.com`;
  - `jamaslov@gmail.com`.
- Unauthenticated HTTP smoke to `/health` on both release frontend URLs returns `302` to Google OAuth,
  confirming IAP intercepts browser access instead of serving content directly.

Executed on `2026-07-12`:

- Added `site-front-release` proxy behavior on branch `release` in `re-actum/site-front` commit `918a3fa`.
- The proxy sets `X-Robots-Tag: noindex, nofollow` whenever `INDEXING_MODE=noindex`.
- Existing release deploy config already sets `INDEXING_MODE=noindex` for `site-front-release`.
- Existing `robots.txt` blocks all crawling, and `sitemap.xml` returns an empty sitemap list.
- Unit test `tests/unit/proxy-indexing.test.js` confirms the header is set only in noindex mode.
- Cloud Build `5b45bcce-1a94-4ade-82b0-2e52302d005f` deployed `site-front-release`.
- New ready revision: `site-front-release-00002-8qm`.
- IAP remained enabled after deploy, and Cloud Run invoker remained limited to the IAP service agent.
- CLI app-level header smoke is blocked by IAP for the current user-token flow; this is acceptable while
  the site stays closed, but the final LB/public entrypoint must repeat header/robots/sitemap smoke before
  public opening.

## Phase 9 - Data, Import, And CMS Initialization

Goal: make release content editable against the correct data boundary.

Checklist:

- [ ] Decide release ERP/import path:
  - first path: controlled operator-run import into `cms-back-release`/`site_release`;
  - later option: release `data-inside-migrator` contour if recurring imports need their own runtime.
- [ ] Run schema migrations on `site_release`.
- [ ] Import or create reference data:
  - practices;
  - services;
  - problems;
  - regions;
  - offices;
  - lawyers;
  - reviews;
  - lawyer qualifications;
  - region qualifications.
- [ ] Create first release admin user.
- [ ] Create/authorize initial CMS users.
- [ ] Configure IAP access for approved emails.
- [ ] Disable anonymous/develop auth bypass for release.
- [ ] Fill global sections.
- [ ] Fill required page content.
- [ ] Upload release media fresh.
- [ ] Publish first snapshots for smoke routes.

Stop if:

- editors are polishing content against wrong or temporary source data without clear ownership;
- release CMS auth depends on anonymous bypass;
- users have IAP access but no CMS role mapping.

## Phase 10 - Closed Verification

Goal: prove that the release contour works while still closed.

Smoke checks:

- [x] `cms-back-release` health endpoint works.
- [x] `cms-back-release` readiness confirms DB connectivity.
- [x] `cms-front-release` health endpoint works through authenticated Cloud Run access.
- [x] `site-front-release` health endpoint works through authenticated Cloud Run access.
- [x] direct unauthenticated requests to `cms-front-release` return `403`.
- [x] direct unauthenticated requests to `site-front-release` return `403`.
- [x] `cms-front-release` can call `cms-back-release` through the release service-to-service path.
- [x] `site-front-release` can call `cms-back-release` through the release service-to-service path.
- [x] IAP/closed reviewer boundary is configured for the approved initial emails.
- [ ] public routes render from published snapshots.
- [ ] global sections render on public pages.
- [ ] media upload/render path works.
- [ ] reference data pages render correct imported data.
- [ ] publish path updates current snapshots.
- [ ] rollback/snapshot recovery path works for a test page.
- [ ] backend is not callable by public browsers outside approved paths.
- [ ] logs contain no secrets or raw credentials.
- [x] fresh error-log check is clean after backend/frontend smoke.
- [x] noindex/robots/sitemap behavior is correct for the current closed release boundary; repeat through
  the final public/LB entrypoint before opening.

Stop if:

- any critical route renders develop data;
- CMS auth or IAP behaves inconsistently for approved users;
- indexing controls are missing;
- logs expose sensitive values.

Smoke result on `2026-07-05`:

- Authenticated `GET /api/health` returned `200`.
- Authenticated `GET /api/ready` returned `200`.
- `/api/ready` reported database status `ok` with Cloud SQL IAM access to `site_release`.
- Authenticated `GET cms-front-release /health` returned `200`.
- Authenticated `GET cms-front-release /api/admin/pages` returned `200` with an empty release DB page list.
- Authenticated `GET site-front-release /health` returned `200`.
- Authenticated `POST site-front-release /api/preview/pages/smoke-missing-page` returned app-layer `404`
  for a missing page, confirming the frontend -> backend invocation path works.
- Unauthenticated `GET /health` returned `403` on both frontend services.
- After direct Cloud Run IAP was enabled on `2026-07-11`, unauthenticated `GET /health` returns `302` to
  Google OAuth on both frontend services.
- `cms-front-release` and `site-front-release` both have explicit IAP OAuth settings with the dedicated
  release OAuth client `865011807785-dc2h038ejlv6hjlpaodmaliprs2rdvrp.apps.googleusercontent.com`; the
  secret was applied from a temporary local JSON and deleted, not stored in git/docs/chat.
- On `2026-07-12`, `site-front-release` revision `site-front-release-00002-8qm` deployed a runtime
  `X-Robots-Tag: noindex, nofollow` proxy for `INDEXING_MODE=noindex`; unauthenticated `/health` still
  returns `302` to Google OAuth, and fresh `ERROR` logs were empty after deploy.

## Phase 11 - Public Go-Live Preparation

Goal: prepare the controlled public opening without combining it with an accidental domain migration.

Checklist:

- [ ] Confirm public go-live date/window.
- [ ] Confirm old site rollback/fallback mechanism.
- [ ] Confirm DNS or LB traffic switch plan.
- [ ] Confirm canonical host remains `https://actum.com.ua`.
- [ ] Confirm redirect behavior for `www.actum.com.ua`.
- [ ] Confirm `actum.ua` behavior for this phase.
- [ ] Confirm Search Console and sitemap plan.
- [ ] Confirm robots/noindex removal plan.
- [ ] Confirm forms/integrations are working or explicitly disabled.
- [ ] Run final smoke before opening.
- [ ] Open public access only after explicit approval.
- [ ] Remove noindex only after explicit approval.
- [ ] Monitor logs, indexing signals, and critical routes after launch.

Stop if:

- public opening and `actum.ua` canonical migration are being bundled unintentionally;
- old site rollback path is unavailable;
- critical content is missing;
- no one owns post-launch monitoring.

## Rollback Notes

Code rollback:

- prefer `git revert` on the `release` branch and redeploy through Cloud Build;
- urgent Cloud Run revision rollback is temporary and must be documented with current revision, target
  revision, reason, and follow-up git fix.

Content rollback:

- use CMS snapshot history to restore page/content state.

Database recovery:

- use Cloud SQL backups/restore for severe corruption or bad migration outcomes;
- take an explicit on-demand backup/export before risky release migrations;
- avoid blind down migrations for release.

Public rollback:

- keep the old public site available during the cutover;
- if release go-live fails, revert DNS, redirects, or load-balancer traffic to the old site while fixing
  the release contour.

## Immediate Next Step

The next practical step is the closed access and content-preparation slice:

1. create/map CMS users and roles for the approved release reviewers;
2. run controlled import/bootstrap into `site_release`;
3. fill and publish the first release snapshots for smoke routes;
4. repeat noindex/robots/sitemap smoke through the final public/LB entrypoint before any opening;
5. decide the final LB/serverless NEG/IAP/domain perimeter separately from the temporary direct Cloud Run
   IAP bridge.
