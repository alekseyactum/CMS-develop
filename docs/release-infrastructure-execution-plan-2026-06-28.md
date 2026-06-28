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

Status: started.

- [x] Create CMS release architecture document.
- [x] Synchronize release summary into `gcp-infra-playbook`.
- [ ] Confirm this execution plan before real GCP work starts.
- [ ] Confirm that the next step is cloud inventory/preflight, not resource creation.

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
- [ ] Final Cloud SQL create command approval.
- [ ] CMS role assignment for each initial user.

## Phase 1 - Preflight And Current-State Inventory

Goal: understand existing project state before creating anything.

- [ ] Run the playbook GCP preflight from `gcp-infra-playbook`.
- [ ] Record active gcloud project and authenticated account.
- [ ] Inventory existing Cloud Run services relevant to CMS/develop.
- [ ] Inventory existing service accounts relevant to CMS/develop.
- [ ] Inventory existing Cloud SQL instances/databases relevant to CMS/develop.
- [ ] Inventory existing Secret Manager names relevant to CMS/develop.
- [ ] Inventory existing Cloud Storage buckets relevant to CMS/develop.
- [ ] Inventory existing Cloud Build triggers relevant to CMS service repos.
- [ ] Inventory existing load balancers, serverless NEGs, certificates, IAP settings, and DNS decisions if
  already present.
- [ ] Save only non-secret findings into markdown.

Stop if:

- active project is not `composite-ally-360719`;
- authenticated account lacks required visibility;
- existing resources conflict with planned release names;
- playbook and CMS docs disagree.

## Phase 2 - Git And Build Surface

Goal: make release deployable from source control before runtime resources depend on it.

- [ ] Confirm canonical service repositories:
  - `re-actum/site-front`
  - `re-actum/cms-front`
  - `re-actum/cms-back`
- [ ] Create or verify `release` branches in each service repo.
- [ ] Decide whether branch protection is required before first release deploy.
- [ ] Confirm Cloud Build config files for release builds.
- [ ] Create or update release Cloud Build triggers:
  - `site-front-release`
  - `cms-front-release`
  - `cms-back-release`
- [ ] Ensure triggers deploy from `release` branches only.
- [ ] Ensure release builds do not deploy from develop branches.

Stop if:

- release branch does not contain the required runtime code;
- release trigger would deploy from the wrong branch;
- build config requires secrets that are not yet modeled.

## Phase 3 - IAM And Service Accounts

Goal: isolate release runtime identities from develop.

Planned service accounts:

- `site-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com`

Checklist:

- [ ] Create release runtime service accounts.
- [ ] Grant each service account only required runtime permissions.
- [ ] Grant `cms-back-release-runner` Cloud SQL access for the release database path.
- [ ] Grant `cms-back-release-runner` write/manage access to release media bucket only.
- [ ] Grant frontend runners access only to required runtime secrets/config.
- [ ] Ensure humans are not used as runtime identities.
- [ ] Document non-secret IAM grants in playbook or CMS docs.

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
- [ ] Approve final Cloud SQL create command.
- [ ] Create Cloud SQL instance in `europe-central2`.
- [ ] Enable automated backups with about 7 days retention.
- [ ] Create database `site_release`.
- [ ] Create/authorize IAM database user for `cms-back-release-runner`.
- [ ] Prepare release migration job, for example `cms-back-release-migrate`.
- [ ] Ensure migrations are executed explicitly, not on normal Cloud Run startup.
- [ ] Before destructive or risky migrations, define backup/export or forward-fix path.

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

- [ ] Create secret placeholders or secret resources as needed.
- [ ] Add secret values only through GCP Secret Manager, never in git/docs/chat/logs.
- [ ] Assign secret access only to the service accounts that need each secret.
- [ ] Confirm runtime non-secret config:
  - `ENVIRONMENT=release`
  - `APP_ENV=release` or service equivalent
  - `CMS_BACK_URL`
  - `CLOUD_SQL_CONNECTION_NAME`
  - `DB_NAME=site_release`
  - `DB_IAM_USER=cms-back-release-runner`
  - `MEDIA_BUCKET=site-media-release`
  - noindex/robots mode before go-live
- [ ] Confirm secret rotation owner.

Stop if:

- a secret value appears in markdown, command history snippets, logs, or chat;
- a frontend receives backend-only integration secrets;
- release service points to develop secrets.

## Phase 6 - Storage And Media

Goal: isolate release media from develop.

Planned bucket:

- `site-media-release`

Checklist:

- [ ] Create release media bucket with region/location policy matching the project decision.
- [ ] Grant write/manage access to `cms-back-release-runner`.
- [ ] Avoid direct frontend write permissions.
- [ ] Confirm public media URL strategy before go-live.
- [ ] Confirm whether media delivery needs signed URLs, public object serving, or LB/CDN path later.
- [ ] Keep release media fresh; do not copy develop media by default.

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

- [ ] Create/deploy `cms-back-release` with release runner and release DB/media config.
- [ ] Create/deploy `cms-front-release` with release runner and backend URL.
- [ ] Create/deploy `site-front-release` with release runner and backend URL.
- [ ] Set min instances to `0` while the contour is closed.
- [ ] Keep initial max instances conservative:
  - `site-front-release`: `3`
  - `cms-front-release`: `2`
  - `cms-back-release`: `3`
- [ ] Restrict `cms-back-release` from public browser access.
- [ ] Allow only approved service-to-service invocation paths.
- [ ] Deploy/update `cms-back-release-migrate`.
- [ ] Run migrations explicitly after confirming target DB.

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

- [ ] Decide whether LB/IAP is created in the first slice or whether direct Cloud Run IAP is used only as
  a temporary bridge.
- [ ] Create serverless NEG/backends for required release services.
- [ ] Configure HTTPS LB and managed certificate(s).
- [ ] Configure IAP access for `cms-front-release`.
- [ ] Configure IAP or IP allowlist for pre-go-live public site preview.
- [ ] Ensure `*.run.app` direct access does not bypass the intended boundary where final architecture
  supports ingress restriction.
- [ ] Configure noindex response headers before go-live.
- [ ] Configure `robots.txt` blocking policy before go-live.
- [ ] Keep sitemap disabled, empty, or non-public before go-live.
- [ ] Confirm redirect behavior for `www` and any attached `actum.ua` host.

Stop if:

- the site is reachable publicly without IAP/IP boundary before go-live;
- noindex is absent while the preview is reachable;
- `actum.ua` becomes canonical accidentally;
- direct Cloud Run URL bypasses the perimeter unexpectedly.

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

- [ ] `cms-back-release` health endpoint works.
- [ ] `cms-back-release` readiness confirms DB connectivity.
- [ ] `cms-front-release` is reachable only by approved identities.
- [ ] `site-front-release` preview is reachable only through the approved closed boundary.
- [ ] public routes render from published snapshots.
- [ ] global sections render on public pages.
- [ ] media upload/render path works.
- [ ] reference data pages render correct imported data.
- [ ] publish path updates current snapshots.
- [ ] rollback/snapshot recovery path works for a test page.
- [ ] backend is not callable by public browsers outside approved paths.
- [ ] logs contain no secrets or raw credentials.
- [ ] fresh error-log check is clean after smoke.
- [ ] noindex/robots/sitemap behavior is correct before go-live.

Stop if:

- any critical route renders develop data;
- CMS auth or IAP behaves inconsistently for approved users;
- indexing controls are missing;
- logs expose sensitive values.

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

The next practical step is not resource creation. It is:

1. approve this plan as the working checklist;
2. run playbook preflight;
3. inventory current GCP state;
4. create a concrete command-level implementation runbook for Phase 2 through Phase 8;
5. request explicit approval before mutation commands that create release resources.
