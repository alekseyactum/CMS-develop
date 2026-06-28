# CMS Release Infrastructure Command Runbook - 2026-06-28

This runbook converts the release execution plan into concrete command-level work.

It is not an approval to run mutation commands. Commands that create or change release resources are R2
actions under `gcp-infra-playbook` and require explicit approval immediately before execution.

References:

- Architecture: `docs/release-infrastructure-architecture-2026-06-28.md`
- Execution plan: `docs/release-infrastructure-execution-plan-2026-06-28.md`
- Inventory: `docs/release-gcp-inventory-2026-06-28.md`
- Governing playbook: `../gcp-infra-playbook/docs/projects/cms.md`

## Already Completed

- [x] Release decisions fixed in CMS docs.
- [x] Release decisions synchronized into `gcp-infra-playbook`.
- [x] GCP preflight passed for account `privatemailofap@gmail.com` and project
  `composite-ally-360719`.
- [x] GCP inventory collected without reading secret values.
- [x] `actum-strapi` baseline read for Cloud SQL sizing.
- [x] Remote `release` branches created in `site-front`, `cms-front`, and `cms-back`.
- [x] `cloudbuild.release.yaml` added and pushed to each release branch.
- [x] Release runtime service accounts created.
- [x] `cms-back-release-runner` granted `roles/cloudsql.client` and `roles/cloudsql.instanceUser`.

## Scope For "Through Point 5"

This runbook interprets "through point 5" as the first five high-level implementation items:

1. close release decisions;
2. run preflight and inventory;
3. prepare release branches and build surface;
4. create release runtime identities;
5. create release Cloud SQL instance/database boundary.

Secrets, storage, Cloud Run services, LB/IAP, migrations, imports, CMS users, and go-live are outside this
specific slice unless separately approved.

## Safety Notes

- Do not copy develop Cloud Run settings blindly.
- Do not reuse old `actum`/`strapi` release resources as CMS release resources.
- Do not reuse old `actum-site-front-release-cloud` as the new `site-front-release-runner`.
- Do not create Cloud Build triggers against current service `cloudbuild.yaml` files before release config
  is corrected. The current files are develop-oriented and would deploy to develop services.
- Do not copy old `actum-strapi` public authorized networks into `site-release` by default.
- Do not put secret values in commands, docs, logs, or chat.

## Phase 1 - Preflight And Inventory

Already executed:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\gcloud-preflight.ps1
```

Result:

- account: `privatemailofap@gmail.com`
- project: `composite-ally-360719`
- token check: passed

Useful read-only inventory commands already used:

```powershell
gcloud sql instances describe actum-strapi --format=json
gcloud sql instances list --format=json
gcloud run services list --platform=managed --region=europe-central2 --format=json
gcloud builds triggers list --format=json
gcloud iam service-accounts list --format=json
gcloud secrets list --format=json
gcloud storage buckets list --format=json
gcloud compute network-endpoint-groups list --format=json
gcloud compute backend-services list --global --format=json
gcloud compute url-maps list --format=json
```

## Phase 2 - Release Branches And Build Surface

Current local service-repo observations:

- `site-front`: local `develop` is behind `origin/develop`; no local `release` branch observed.
- `cms-front`: local `develop` has uncommitted work; no local `release` branch observed.
- `cms-back`: local `develop` is clean; no local `release` branch observed.
- all three repos have `cloudbuild.yaml`.
- current `cloudbuild.yaml` files are develop-oriented and must be adjusted before release triggers are
  created.

Executed state:

- `site-front` remote `release` branch created from `origin/develop`.
- `cms-front` remote `release` branch created from `origin/develop`.
- `cms-back` remote `release` branch created from `origin/develop`.
- `cloudbuild.release.yaml` was added to each release branch.
- pushed release commits:
  - `site-front`: `df49945 ci: add release Cloud Build config`
  - `cms-front`: `ee9a29f ci: add release Cloud Build config`
  - `cms-back`: `e5f5b8d ci: add release Cloud Build config`
- existing develop `cloudbuild.yaml` files were not changed.
- local dirty `cms-front` develop worktree was not checked out or modified.

Recommended branch source:

- create remote `release` branches from current `origin/develop` after fetching and checking remote state;
- do not switch the dirty local `cms-front` working tree until its unrelated work is handled.

Read-only checks:

```powershell
git -C G:\работа\Actum\develop\site-front fetch origin --prune
git -C G:\работа\Actum\develop\cms-front fetch origin --prune
git -C G:\работа\Actum\develop\cms-back fetch origin --prune

git -C G:\работа\Actum\develop\site-front ls-remote --heads origin release
git -C G:\работа\Actum\develop\cms-front ls-remote --heads origin release
git -C G:\работа\Actum\develop\cms-back ls-remote --heads origin release
```

Mutation commands to create remote release branches if they do not exist:

```powershell
git -C G:\работа\Actum\develop\site-front push origin origin/develop:refs/heads/release
git -C G:\работа\Actum\develop\cms-front push origin origin/develop:refs/heads/release
git -C G:\работа\Actum\develop\cms-back push origin origin/develop:refs/heads/release
```

Before Cloud Build triggers:

- update release branch build config so it deploys `*-release` services;
- replace hardcoded develop service accounts with release service accounts;
- replace develop backend URL/DB/media values with release values;
- ensure `cms-back` release config points to `site-release`/`site_release`;
- keep migrations explicit through `cms-back-release-migrate`.

Release build configs are now present. Do not create release triggers until Cloud SQL, secrets, media
bucket, service account act-as permissions, and trigger service-account decisions are confirmed.

Intended trigger names:

- `site-front-release`
- `cms-front-release`
- `cms-back-release`

Trigger creation commands will be finalized only after release build configs are reviewed.

## Phase 3 - Release Runtime Identities

Planned service accounts:

- `site-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com`

Executed state:

- all three release runtime service accounts were created and verified as enabled.
- `cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com` was granted:
  - `roles/cloudsql.client`
  - `roles/cloudsql.instanceUser`
- frontend release runners were not granted broad project roles in this phase.

Mutation commands:

```powershell
gcloud iam service-accounts create site-front-release-runner --display-name="site-front release runner"
gcloud iam service-accounts create cms-front-release-runner --display-name="cms-front release runner"
gcloud iam service-accounts create cms-back-release-runner --display-name="cms-back release runner"
```

Initial project IAM needed for Cloud SQL connector access:

```powershell
gcloud projects add-iam-policy-binding composite-ally-360719 `
  --member="serviceAccount:cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com" `
  --role="roles/cloudsql.client"
```

Additional project IAM needed for Cloud SQL IAM authentication:

```powershell
gcloud projects add-iam-policy-binding composite-ally-360719 `
  --member="serviceAccount:cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com" `
  --role="roles/cloudsql.instanceUser"
```

Do not grant broad project roles to the frontend release runners.

## Phase 4 - Cloud SQL Release Instance

Planned instance:

- instance ID: `site-release`
- database: `site_release`
- region: `europe-central2`
- zone: `europe-central2-b`
- database version: `MYSQL_8_0_43`
- edition: `ENTERPRISE`
- tier: `db-g1-small`
- disk: `10 GB`, `PD_SSD`
- storage auto-resize: enabled
- backups: enabled
- binary logs: enabled
- retained backups: `7`
- transaction log retention: `7` days
- deletion protection: enabled
- flags:
  - `sort_buffer_size=256000000`
  - `innodb_lock_wait_timeout=15000`
  - `character_set_server=utf8mb4`
  - `cloudsql_iam_authentication=on`

Preferred create command:

```powershell
gcloud sql instances create site-release `
  --database-version=MYSQL_8_0_43 `
  --edition=ENTERPRISE `
  --tier=db-g1-small `
  --region=europe-central2 `
  --availability-type=ZONAL `
  --zone=europe-central2-b `
  --storage-type=SSD `
  --storage-size=10GB `
  --storage-auto-increase `
  --backup `
  --backup-start-time=13:00 `
  --retained-backups-count=7 `
  --enable-bin-log `
  --transaction-log-retention-days=7 `
  --database-flags=sort_buffer_size=256000000,innodb_lock_wait_timeout=15000,character_set_server=utf8mb4,cloudsql_iam_authentication=on `
  --network=default `
  --no-assign-ip `
  --deletion-protection
```

Notes:

- `--no-assign-ip` is intentional to avoid copying old public authorized networks from `actum-strapi`.
- If Cloud Run/Cloud SQL connector setup requires public IP in this project, stop and reassess before
  adding it.
- If the CLI rejects a flag combination, stop and adjust the command rather than falling back to a weaker
  network/auth posture.

Create release DB:

```powershell
gcloud sql databases create site_release --instance=site-release --charset=utf8mb4 --collation=utf8mb4_unicode_ci
```

Create IAM DB user for backend service account:

```powershell
gcloud sql users create cms-back-release-runner@composite-ally-360719.iam `
  --instance=site-release `
  --type=cloud_iam_service_account
```

Verification commands:

```powershell
gcloud sql instances describe site-release --format=json
gcloud sql databases list --instance=site-release
gcloud sql users list --instance=site-release
```

Rollback point:

- if the instance was created but no service depends on it yet, deletion is technically possible but is a
  destructive R3 action and must not be done without a separate direct command;
- preferred immediate recovery is to leave the unused instance with deletion protection and document the
  correction needed.

## Not In This Slice

These are intentionally deferred:

- create release Secret Manager resources;
- create `site-media-release`;
- create/deploy release Cloud Run services;
- create LB/IAP perimeter;
- run migrations;
- import data;
- create CMS users;
- open any public access;
- change DNS/canonical/robots for the public site.
