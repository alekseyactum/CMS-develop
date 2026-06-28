# CMS Release Infrastructure Architecture - 2026-06-28

This document captures the first release-contour infrastructure plan for the Actum CMS project.

It is a planning document only. It does not approve or perform any GCP resource creation. Any real work
with Cloud Run, Cloud SQL, Cloud Build, Secret Manager, Cloud Storage, IAM, DNS, certificates, IAP, or load
balancers is governed by `gcp-infra-playbook` and requires the required preflight before reading or
changing cloud state.

## Release Intent

The `release` contour is the future production contour, kept closed until the public go-live window around
mid-August 2026.

It is not a temporary staging environment. The goal is to start filling and validating the future
production database and content model before the public site opens.

Confirmed:

- GCP project: `composite-ally-360719`.
- Environment name: `release`.
- Region: `europe-central2`.
- Deploy-bearing branch: `release`.
- The public site must not become indexable before a separate go-live decision.
- The current public site remains available in parallel as the rollback/fallback surface during cutover.

## Service Repositories

The deploy-bearing release branches should be created in the canonical service repositories:

- `re-actum/site-front`, branch `release`.
- `re-actum/cms-front`, branch `release`.
- `re-actum/cms-back`, branch `release`.

The `CMS-develop` repository remains the umbrella/context repository and does not deploy runtime services.

Release deployment should be git-based:

```text
GitHub release branch -> Cloud Build release trigger -> Cloud Run release service
```

Manual Cloud Run changes are allowed only as documented operational exceptions with rollback notes. They
must not become the normal deployment path.

## Cloud Run Services

Planned release services:

- `site-front-release`
- `cms-front-release`
- `cms-back-release`

Initial resource posture:

- min instances: `0` while the contour is closed.
- max instances: keep close to develop defaults until traffic planning is clearer:
  - `site-front-release`: max `3`
  - `cms-front-release`: max `2`
  - `cms-back-release`: max `3`
- CPU allocation: request-time CPU is enough for the first closed release contour.

Release service accounts should be separate from develop:

- `site-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com`

Access intent:

- `site-front-release` is closed before go-live and must not rely on a secret URL as its only protection.
- `cms-front-release` is closed through IAP and CMS authorization.
- `cms-back-release` is not a public browser API.
- `cms-back-release` may be invoked only by approved service accounts such as `site-front-release-runner`
  and `cms-front-release-runner`, plus explicitly approved operator smoke-check identities if needed.

## Frontend Entry And IAP

For release, direct Cloud Run IAP should not be the default final design.

Recommended release baseline:

- external HTTPS load balancer;
- serverless NEG for Cloud Run backends;
- IAP for `cms-front-release` and pre-go-live release preview access;
- optional Cloud Armor/IP allowlist when stable reviewer IPs are practical;
- managed certificate and explicit hostnames;
- Cloud Run ingress restricted to load balancer paths where the final architecture supports it.

Reason:

- direct Cloud Run IAP on `*.run.app` was acceptable for develop convenience;
- release needs a stable entrypoint, certificate/domain control, clearer access policy, and an easier path
  to go-live without redesigning the perimeter;
- a secret or obscure URL is not an access boundary and is not sufficient to prevent discovery or indexing.

Pragmatic exception:

- if creating the load balancer would block early content work, `cms-front-release` may temporarily use
  direct Cloud Run IAP as a documented internal-editing bridge;
- this must be treated as temporary and reassessed before public go-live.

## Domains

Earlier requirements expected `actum.ua` to become the future primary domain. The current clarification is
that `actum.com.ua` already has Google history and should not be moved lightly.

Confirmed SEO-safe baseline for the first public go-live:

- canonical host: `https://actum.com.ua`;
- add `actum.ua` as a prepared secondary domain, but do not make it canonical until a separate migration
  decision is approved;
- if `actum.ua` is attached before go-live, keep it closed/noindex or redirect it to
  `https://actum.com.ua` according to the current phase;
- do not switch canonicals from `actum.com.ua` to `actum.ua` as a side effect of the CMS release.

Why this matters:

- changing the canonical domain is a domain migration, not a small launch setting;
- `actum.com.ua -> actum.ua` can be done later, but it needs a URL inventory, 301 redirect map, Search
  Console preparation, canonical/hreflang/sitemap changes, and post-migration monitoring;
- doing the CMS launch and the primary-domain migration at the same time increases SEO risk.

`www` decision:

- `https://actum.com.ua` is canonical;
- `https://www.actum.com.ua`, if attached, must redirect to `https://actum.com.ua`;
- the same decision is needed for `actum.ua` if it is attached.

## Pre-Go-Live Preview Host

A separate preview host is useful but should stay minimal.

Recommended:

- create one release preview hostname, for example `release.actum.com.ua`, only if the load-balancer setup
  is already being created;
- protect it with IAP or IP allowlist;
- keep `noindex, nofollow`, blocking robots policy, and no public sitemap;
- do not depend on "unlisted URL" secrecy.

If this feels like unnecessary work for the first infrastructure slice, the contour may start with
IAP-protected Cloud Run/LB URLs and add the preview hostname later, before domain-specific smoke tests.

## Cloud SQL

Confirmed:

- release database boundary: separate Cloud SQL instance.
- database name: `site_release`.
- release DB starts empty.
- schema is created through migrations.
- data is filled through ERP/import and CMS editing, not by copying develop content.
- backups should be enabled with a standard retention of approximately 7 days.

Rationale:

- a separate instance gives a clearer backup/restore boundary, lower accidental cross-environment risk,
  and cleaner performance ownership;
- it is a better match for a production-bound contour than placing `site_release` beside develop data on
  the existing develop instance.

Authentication:

- keep the develop pattern: Cloud SQL IAM authentication through the backend runtime service account.
- do not introduce password-oriented CMS runtime DB credentials.

Migrations:

- release migrations must not run automatically on Cloud Run startup.
- create a release migration job, for example `cms-back-release-migrate`.
- update the migration job image through the release build pipeline, but execute migrations explicitly.

## Storage And Media

Confirmed:

- release media bucket is separate from develop.
- proposed bucket: `site-media-release`.
- release media is filled fresh.
- develop media is not copied by default.

Rules:

- `cms-back-release-runner` can manage release media objects.
- `site-front-release-runner` and `cms-front-release-runner` do not write to the bucket directly.
- `cms-front-release` uploads through `cms-back-release`.
- public media URL strategy must be finalized before go-live.

## Secret Manager And Runtime Config

Project-specific release secret names continue the current CMS naming pattern:

- `site-front-runtime-release`
- `cms-front-runtime-release`
- `cms-back-runtime-release`
- `cms-admin-auth-release`

This is a project-specific exception to the newer playbook example pattern
`<environment>--<service>--<secret-name>` and should be synchronized back to the playbook when release
resources are planned there.

Expected non-secret runtime config:

- `ENVIRONMENT=release`
- `APP_ENV=release` or the service's existing equivalent
- `CMS_BACK_URL` for frontend services
- `CLOUD_SQL_CONNECTION_NAME` for `cms-back-release`
- `DB_NAME=site_release`
- `DB_IAM_USER=cms-back-release-runner`
- `MEDIA_BUCKET=site-media-release`
- indexing/robots mode, defaulting to noindex before go-live

Expected secret-backed config depends on current service implementation, but likely includes:

- CMS admin/session signing material if release auth uses server-side sessions or signed identity state;
- any backend integration tokens needed for release ERP/import flows;
- any media/storage signing secret if a signed URL strategy is chosen later.

No secret values belong in git, markdown, logs, or chat.

Open ownership decision:

- choose who can rotate release secrets. Until delegated, the practical owner is the project owner/operator
  controlling GCP access.

## ERP And Data Intake

Confirmed:

- release code is built from `release` branches.
- release DB starts empty.
- content and data are filled fresh.
- section/page structures come from code and migrations, not from manually copying develop rows.

Open decision:

- define the release ERP/import source and path.

The release contour needs an explicit data path for:

- practices;
- services;
- problems;
- regions;
- offices;
- lawyers;
- reviews;
- lawyer qualifications;
- region qualifications.

The likely options are:

- a release `data-inside-migrator` contour feeding `cms-back-release`;
- a controlled one-time import job into `cms-back-release`;
- a temporary operator-run import path before the steady release integration exists.

This must be decided before release CMS editing starts in earnest, because editors should not polish
content against the wrong source-data boundary.

## CMS Auth And Users

Release must not rely on anonymous develop bypass.

Recommended release baseline:

- IAP protects the external CMS entrypoint.
- CMS backend still enforces CMS users and permissions.
- IAP identity is mapped to an existing CMS user by email.
- `x-cms-actor` remains a local/develop fallback only and is disabled for release browser flows.
- `CMS_DEV_AUTH_ALLOW_ANONYMOUS` or any equivalent bypass is disabled in release.

Current backend roles should be used as implemented:

- `admin`
- `editor`
- `publisher`
- `viewer`

Open decisions:

- first release admin email;
- exact list of CMS release users;
- whether release must ship with a stronger session model before public go-live or whether IAP identity
  plus CMS user mapping is sufficient for the first closed release CMS.

Recommended first admin if no other decision is made:

- `ap@modusmoses.com`

## Indexing And Go-Live Gates

Before public go-live:

- public frontend responses use `X-Robots-Tag: noindex, nofollow`;
- `robots.txt` blocks crawling;
- sitemap is disabled, empty, or not exposed as an indexable public sitemap;
- access is closed by IAP/IP allowlist/private boundary, not by obscurity;
- canonical/hreflang/SEO metadata is still generated and validated internally.

Go-live is a separate action, not a side effect of resource creation.

Minimum go-live gates:

- release services are deployed from `release` branches;
- release DB migrations are applied;
- release ERP/reference data path is proven;
- CMS users and admin access are configured;
- global sections and required page content are filled;
- media upload/render path works;
- all critical public routes render from published snapshots;
- forms/integrations work or are explicitly disabled;
- redirects/canonical policy is approved;
- old site rollback/fallback remains available;
- smoke tests and fresh error-log checks pass;
- indexing policy is deliberately switched only after approval.

## Rollback And Recovery

Old site parallel availability matters because it is the public rollback surface during domain/cutover
failure. If the new release site fails after go-live, the team can revert DNS, redirects, or load balancer
traffic to the old site while fixing the new contour.

Application rollback:

- prefer `git revert` on release branch and redeploy through Cloud Build;
- urgent Cloud Run revision rollback is temporary and must be documented with the previous/target revision
  and follow-up git fix.

Content rollback:

- use CMS snapshot history for page/content rollback.

Database recovery:

- use Cloud SQL backups/restore for infrastructure-level corruption or severe migration mistakes;
- before destructive or risky migrations, take an explicit on-demand backup/export;
- avoid blind down migrations for release.

## First Implementation Sequence

Detailed execution checklist: `docs/release-infrastructure-execution-plan-2026-06-28.md`.

1. Finalize this document and the matching `gcp-infra-playbook` CMS project section.
2. Name and size the separate release Cloud SQL instance.
3. Decide release entrypoint model: LB/IAP now vs documented temporary direct IAP bridge.
4. Confirm release DNS and redirect rules for `https://actum.com.ua`, `www`, and `actum.ua`.
5. Create release branches in `site-front`, `cms-front`, and `cms-back`.
6. Create release service accounts and IAM plan.
7. Create release secrets placeholders and runtime config plan without secret values in docs.
8. Create release Cloud Run services, triggers, and migration job.
9. Apply release migrations explicitly.
10. Establish release ERP/import path.
11. Configure release CMS access and first admin.
12. Fill global sections, media, and page content.
13. Run closed preview and release readiness smoke.
14. Approve public go-live and indexing separately around the target August window.

## Open Decisions

- Name and sizing for the separate release Cloud SQL instance.
- Whether to create `release.actum.com.ua` for closed preview in the first infrastructure slice.
- Release ERP/import path.
- First release admin and full release CMS user list.
- Secret rotation owner.
- Final go-live date/window.
