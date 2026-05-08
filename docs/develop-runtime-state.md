# CMS Develop Runtime State

This document records the actual minimal develop runtime created for the clean CMS implementation.

Initial date: 2026-05-07.
Latest update: 2026-05-08.

GCP preflight was run from `gcp-infra-playbook` before reading or changing cloud state.

## Scope

Only the `develop` contour was created.

No release services, custom domains, DNS records, indexing enablement, production-like runtime, Cloud
Tasks, Cloud Scheduler, or worker services were created.

## Service Repositories

Canonical service repositories:

- `re-actum/site-front`
- `re-actum/cms-front`
- `re-actum/cms-back`

Each repository has a `develop` branch with minimal deployable code:

- `site-front`: Next.js public frontend skeleton.
- `cms-front`: Next.js admin frontend skeleton.
- `cms-back`: NestJS backend skeleton with `/api/health`, `/api/ready`, and OpenAPI docs.

The first skeleton commits were pushed before cloud deployment:

- `site-front`: `7147d4b Add develop Cloud Run skeleton`
- `cms-front`: `9822dad Add develop Cloud Run skeleton`
- `cms-back`: `d32e1ee Add develop Cloud Run skeleton`

Latest backend foundation commit:

- `cms-back`: `3acb281 Add manual database migrations`

## Cloud Run

Created services in project `composite-ally-360719`, region `europe-central2`:

- `site-front-develop`
- `cms-front-develop`
- `cms-back-develop`

Current service URLs:

- `site-front-develop`: `https://site-front-develop-2ubpwinuqq-lm.a.run.app`
- `cms-front-develop`: `https://cms-front-develop-2ubpwinuqq-lm.a.run.app`
- `cms-back-develop`: `https://cms-back-develop-2ubpwinuqq-lm.a.run.app`

Access state:

- `site-front-develop`: ingress `all`, `allUsers` has `roles/run.invoker`.
- `cms-front-develop`: ingress `internal-and-cloud-load-balancing`, no public invoker.
- `cms-back-develop`: ingress `all`, no unauthenticated access, invoker allowed only for:
  - `site-front-develop-runner@composite-ally-360719.iam.gserviceaccount.com`
  - `cms-front-develop-runner@composite-ally-360719.iam.gserviceaccount.com`

`cms-back-develop` uses ingress `all` intentionally in the first develop contour. Attempts to use
`internal-and-cloud-load-balancing` blocked the simple Cloud Run service-to-service readiness check without
an additional internal networking path. The backend remains closed by Cloud Run IAM.

Backend runtime settings:

- Cloud SQL instance attached: `composite-ally-360719:europe-central2:develop-eu`
- `CLOUD_SQL_CONNECTION_NAME=composite-ally-360719:europe-central2:develop-eu`
- `DB_NAME=site_develop`
- `DB_IAM_USER=cms-back-develop-runner`
- `MEDIA_BUCKET=site-media-develop`

Frontend runtime settings:

- `CMS_BACK_URL=https://cms-back-develop-2ubpwinuqq-lm.a.run.app`

## Service Accounts And IAM

Runtime service accounts:

- `site-front-develop-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-front-develop-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-back-develop-runner@composite-ally-360719.iam.gserviceaccount.com`

Important IAM state:

- `cms-develop-build-runner@composite-ally-360719.iam.gserviceaccount.com` is the user-managed Cloud Build
  service account for CMS develop triggers.
- `cms-develop-build-runner` can deploy Cloud Run and push Artifact Registry images for these services.
- `cms-develop-build-runner` can act as the three runtime service accounts.
- `cms-back-develop-runner` has `roles/cloudsql.client`.
- `cms-back-develop-runner` has `roles/cloudsql.instanceUser`.
- `cms-back-develop-runner` has bucket object admin on `gs://site-media-develop`.

## Cloud SQL

Instance:

- `develop-eu`
- MySQL 8.0
- region `europe-central2`
- `cloudsql_iam_authentication=on`

Created database:

- `site_develop`

Backend database identity:

- Cloud SQL IAM DB user: `cms-back-develop-runner`
- IAM email: `cms-back-develop-runner@composite-ally-360719.iam.gserviceaccount.com`

Important correction:

- A temporary password-oriented user `cms_back_develop_service` was created during setup.
- After the service-account requirement was clarified, that built-in SQL user was deleted.
- The password-oriented Secret Manager secret `cms-db-login-data-develop` was deleted.

DB-level access:

- `cms-back-develop-runner` has DB-level privileges on `site_develop` for normal application DML and
  controlled schema migrations.
- These grants were applied through a temporary built-in SQL user used only for the grant operation.
- The temporary SQL user was deleted after the grants were applied.
- No password-based CMS runtime credential or database secret was introduced.

Schema state:

- Migration tracking table: `schema_migrations`.
- First migration applied: `202605080001 create cms_system_metadata table`.
- First application table: `cms_system_metadata`.

## Secret Manager

Created develop secrets:

- `site-front-runtime-develop`
- `cms-front-runtime-develop`
- `cms-back-runtime-develop`
- `cms-admin-auth-develop`

No secret values are recorded in this repository.

There is intentionally no `cms-db-login-data-develop` secret because CMS database authentication is
service-account based.

## Media Storage

Created bucket:

- `gs://site-media-develop`

Current policy:

- Uniform bucket-level access enabled.
- Bucket is private.
- `cms-back-develop-runner` can manage objects.
- Public media URL strategy is pending and must be implemented separately before published media is served
  from stable public URLs.

## Build And Deploy

Final manual Cloud Build deploys with the committed `cloudbuild.yaml` shape succeeded:

- `site-front-develop`: build `83ca1ded-9ec4-4a3d-8a87-3a9a367c7492`
- `cms-front-develop`: build `6c6e85f0-22aa-4e35-9c25-1fdc44208715`
- `cms-back-develop`: build `839b28a1-da41-410e-af7b-97a6690e8ae1`

Cloud Build v2 repository mappings were created through connection `strapitest-github`:

- `projects/composite-ally-360719/locations/europe-central2/connections/strapitest-github/repositories/site-front`
- `projects/composite-ally-360719/locations/europe-central2/connections/strapitest-github/repositories/cms-front`
- `projects/composite-ally-360719/locations/europe-central2/connections/strapitest-github/repositories/cms-back`

Created develop triggers:

- `cms-site-front-develop`
  - id: `ba99a59c-7258-4b63-be39-db4b630d59b4`
  - repo: `re-actum/site-front`
  - branch pattern: `develop$`
  - build config: `cloudbuild.yaml`
- `cms-front-develop`
  - id: `097c4ead-3b3f-4bb1-a41f-61666a8922b8`
  - repo: `re-actum/cms-front`
  - branch pattern: `develop$`
  - build config: `cloudbuild.yaml`
- `cms-back-develop`
  - id: `757154f2-e42e-48cc-8bab-2de92021dfbe`
  - repo: `re-actum/cms-back`
  - branch pattern: `develop$`
  - build config: `cloudbuild.yaml`

Trigger service account:

- `projects/composite-ally-360719/serviceAccounts/cms-develop-build-runner@composite-ally-360719.iam.gserviceaccount.com`

Important correction:

- Regional v2 triggers rejected the legacy Cloud Build service account as `build.service_account`.
- A user-managed service account `cms-develop-build-runner` was created and assigned to the three CMS
  develop triggers.
- With a user-managed build service account, each `cloudbuild.yaml` uses `options.logging:
  CLOUD_LOGGING_ONLY`.

Trigger verification:

- `cms-back-develop` trigger fired from normal pushes to `re-actum/cms-back:develop`.
- Successful backend trigger build after first backend runtime foundation: `dd4b1a98-4bf6-463f-9368-773b2dae4d65`.
- Successful backend trigger build after manual migrations were added: build `3a410503-9feb-4248-bf44-a6130b899323`,
  revision `cms-back-develop-00007-mnv`, commit `3acb28141631f5da70b4e03580da2c50b24babde`.
- The backend deployment was performed by `cms-develop-build-runner`.

Open item:

- The next normal code push to `site-front` and `cms-front` should be watched once after the logging option
  fix to confirm automatic deployment end to end for those services.

## Cloud Run Jobs

Created develop operational jobs:

- `cms-back-migrate-develop`
  - purpose: explicit manual database migrations for `cms-back`;
  - command: `npm run migrate`;
  - service account: `cms-back-develop-runner@composite-ally-360719.iam.gserviceaccount.com`;
  - Cloud SQL instance attached: `composite-ally-360719:europe-central2:develop-eu`.
- `cms-back-ready-check`
  - purpose: protected smoke check for `cms-back-develop /api/ready`;
  - service account: `site-front-develop-runner@composite-ally-360719.iam.gserviceaccount.com`;
  - uses an identity token from the Cloud Run metadata server and does not store credentials.

These jobs are operational tools, not background workers. They do not run on a schedule.

Migration verification:

- `cms-back-migrate-develop-ln4zs` applied migration `202605080001`.
- `cms-back-migrate-develop-vr8q8` completed with `No pending migrations`, proving repeat execution is
  idempotent for the current migration set.

## Playbook Sync

The governing `gcp-infra-playbook/docs/projects/cms.md` page should also be synchronized with this actual
runtime state. During this change, the local playbook checkout already contained unrelated dirty work, so
this repository records the authoritative CMS-side state and flags playbook sync as a follow-up.

## Verification

Verified externally:

- `site-front-develop /health` returned `200` with `{"service":"site-front","status":"ok"}`.
- `site-front-develop /robots.txt` returned `Disallow: /`.
- Direct external unauthenticated access to `cms-front-develop /health` was blocked.
- Direct external unauthenticated access to `cms-back-develop /api/ready` returned `403`.
- Cloud Run Job `cms-back-ready-check`, running as `site-front-develop-runner`, successfully called
  `cms-back-develop /api/ready`.
- `cms-back-develop /api/ready` returned `200` and verified Cloud SQL IAM access to `site_develop`.
- The readiness response contains service status, build metadata, and dependency status. It intentionally
  does not return `CLOUD_SQL_CONNECTION_NAME`, `DB_NAME`, `DB_IAM_USER`, or `MEDIA_BUCKET`.

Local notes:

- `cms-back` local build passed before deployment.
- `cms-back` local `typecheck` passed.
- `cms-back` local `npm audit --omit=dev` reported `0 vulnerabilities`.
- Local frontend builds were not completed because the workstation ran out of disk space during local
  dependency installation. GCP Cloud Build for both frontend services succeeded.
