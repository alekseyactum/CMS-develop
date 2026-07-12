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
- [x] Release Cloud SQL instance `site-release` created.
- [x] Release database `site_release` created.
- [x] Cloud SQL IAM DB user for `cms-back-release-runner` created.
- [x] Release Secret Manager containers created without secret versions/values.
- [x] Release media bucket `site-media-release` created.
- [x] Release media bucket write/manage access granted only to `cms-back-release-runner`.
- [x] MySQL privileges granted to `cms-back-release-runner` on `site_release`.
- [x] `cms-back-release` deployed.
- [x] `cms-back-release-migrate` job created.
- [x] Release migrations executed successfully.
- [x] `cms-back-release` `/api/health` and `/api/ready` smoke passed.

## Scope For "Through Point 5"

This runbook interprets "through point 5" as the first five high-level implementation items:

1. close release decisions;
2. run preflight and inventory;
3. prepare release branches and build surface;
4. create release runtime identities;
5. create release Cloud SQL instance/database boundary.

Secrets, storage, Cloud Run services, LB/IAP, migrations, imports, CMS users, and go-live are outside this
specific slice unless separately approved.

Status as of `2026-07-05`: item 5 is complete. The next slices are release secrets, release media storage,
release Cloud Run services, explicit migrations, controlled import, CMS users, and closed preview access.

Status later on `2026-07-05`: release secrets and release media storage are also created, but secret values,
Cloud Run services, migrations, imports, CMS users, LB/IAP, and go-live are still deferred.

Status after backend deployment on `2026-07-05`: `cms-back-release` and `cms-back-release-migrate` are
created, release migrations are applied, and backend readiness confirms database connectivity. Frontends,
imports, CMS users, LB/IAP, and go-live are still deferred.

Status after frontend deployment on `2026-07-05`: `cms-front-release` and `site-front-release` are created,
closed to unauthenticated access, and can call `cms-back-release` through release service accounts. Imports,
CMS users, LB/IAP, and go-live are still deferred.

## Safety Notes

- Do not copy develop Cloud Run settings blindly.
- Do not reuse old `actum`/`strapi` release resources as CMS release resources.
- Do not reuse old `actum-site-front-release-cloud` as the new `site-front-release-runner`.
- Do not create Cloud Build triggers against current service `cloudbuild.yaml` files before release config
  is corrected. The current files are develop-oriented and would deploy to develop services.
- Do not copy old `actum-strapi` public authorized networks into `site-release` by default.
- If public IP is enabled for local Cloud SQL Auth Proxy access, keep authorized networks empty and require
  Cloud SQL connectors.
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

Executed create command on `2026-07-05`:

```powershell
gcloud sql instances create site-release `
  --database-version=MYSQL_8_0_43 `
  --edition=ENTERPRISE `
  --tier=db-g1-small `
  --availability-type=ZONAL `
  --zone=europe-central2-b `
  --storage-type=SSD `
  --storage-size=10GB `
  --storage-auto-increase `
  --backup `
  --backup-start-time=13:00 `
  --retained-backups-count=7 `
  --enable-bin-log `
  --retained-transaction-log-days=7 `
  --database-flags=sort_buffer_size=256000000,innodb_lock_wait_timeout=15000,character_set_server=utf8mb4,cloudsql_iam_authentication=on `
  --network=default `
  --no-assign-ip `
  --deletion-protection `
  --timeout=unlimited `
  --quiet
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
gcloud sql users create cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com `
  --instance=site-release `
  --type=cloud_iam_service_account `
  --quiet
```

Implementation notes from execution:

- `--transaction-log-retention-days=7` is no longer accepted by the current SDK; use
  `--retained-transaction-log-days=7`.
- The current SDK rejects `--region=europe-central2` together with `--zone=europe-central2-b`; use
  `--zone=europe-central2-b` to keep the planned zone.
- Cloud SQL IAM service account users must be created with the full service account email. The resulting
  listed DB user name is `cms-back-release-runner` with type `CLOUD_IAM_SERVICE_ACCOUNT`.

Post-create connectivity change executed on `2026-07-05`:

```powershell
gcloud sql instances patch site-release `
  --assign-ip `
  --clear-authorized-networks `
  --connector-enforcement=REQUIRED `
  --ssl-mode=ENCRYPTED_ONLY `
  --quiet
```

Reason:

- allow local Cloud SQL Auth Proxy usage without requiring VPN/bastion;
- do not allow broad direct public network access;
- keep access mediated by Cloud SQL connectors and IAM.

Security notes:

- `connector-enforcement=REQUIRED` requires Cloud SQL Auth Proxy or a Cloud SQL language connector.
- Authorized networks are empty.
- Cloud SQL IAM DB authentication remains enabled.
- Cloud SQL MySQL still keeps the built-in `root` user, so password authentication is not globally
  disabled at the database engine level. Do not distribute root credentials; grant DB privileges only to
  approved IAM database users.

Verification commands:

```powershell
gcloud sql instances describe site-release --format=json
gcloud sql databases list --instance=site-release
gcloud sql users list --instance=site-release
```

Verified result on `2026-07-05`:

- instance: `site-release`
- state: `RUNNABLE`
- region/zone: `europe-central2` / `europe-central2-b`
- private IP: `10.89.62.17`
- public IP: `34.116.243.97` as of the post-create connectivity change
- connector enforcement: `REQUIRED`
- authorized networks: empty
- SSL mode: `ENCRYPTED_ONLY`
- database version: `MYSQL_8_0_43`
- edition/tier: `ENTERPRISE` / `db-g1-small`
- disk: `10 GB` `PD_SSD`, storage auto-resize enabled
- backups/binlog: enabled, start time `13:00`, transaction log retention `7`
- deletion protection: enabled
- flags:
  - `character_set_server=utf8mb4`
  - `cloudsql_iam_authentication=on`
  - `innodb_lock_wait_timeout=15000`
  - `sort_buffer_size=256000000`
- database: `site_release`, `utf8mb4`, `utf8mb4_unicode_ci`
- IAM DB user: `cms-back-release-runner`, type `CLOUD_IAM_SERVICE_ACCOUNT`

Rollback point:

- if the instance was created but no service depends on it yet, deletion is technically possible but is a
  destructive R3 action and must not be done without a separate direct command;
- preferred immediate recovery is to leave the unused instance with deletion protection and document the
  correction needed.

## Not In This Slice

## Phase 5 - Release Secrets

Executed on `2026-07-05`:

```powershell
gcloud secrets create site-front-runtime-release --replication-policy=automatic
gcloud secrets create cms-front-runtime-release --replication-policy=automatic
gcloud secrets create cms-back-runtime-release --replication-policy=automatic
gcloud secrets create cms-admin-auth-release --replication-policy=automatic
```

Secret access grants:

```powershell
gcloud secrets add-iam-policy-binding site-front-runtime-release `
  --member=serviceAccount:site-front-release-runner@composite-ally-360719.iam.gserviceaccount.com `
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding cms-front-runtime-release `
  --member=serviceAccount:cms-front-release-runner@composite-ally-360719.iam.gserviceaccount.com `
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding cms-back-runtime-release `
  --member=serviceAccount:cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com `
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding cms-admin-auth-release `
  --member=serviceAccount:cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com `
  --role=roles/secretmanager.secretAccessor
```

Notes:

- Secret containers were created with automatic replication.
- No secret versions or values were added.
- Secret values must be added only through Secret Manager and must not be written to git/docs/chat/logs.

## Phase 6 - Release Media Bucket

Executed on `2026-07-05`:

```powershell
gcloud storage buckets create gs://site-media-release `
  --location=europe-central2 `
  --default-storage-class=STANDARD `
  --uniform-bucket-level-access `
  --public-access-prevention

gcloud storage buckets add-iam-policy-binding gs://site-media-release `
  --member=serviceAccount:cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com `
  --role=roles/storage.objectAdmin
```

Verified result:

- bucket: `gs://site-media-release`
- location: `EUROPE-CENTRAL2`
- storage class: `STANDARD`
- uniform bucket-level access: enabled
- public access prevention: enforced
- soft delete retention: 7 days
- `cms-back-release-runner` has `roles/storage.objectAdmin`
- frontend release runners have no direct bucket write grants
- no develop media was copied

## Phase 7 - Backend Release Deploy And Migrations

MySQL privileges were granted without distributing a root password:

```sql
GRANT ALL PRIVILEGES ON `site_release`.* TO 'cms-back-release-runner'@'%';
```

Execution method:

- uploaded a temporary non-secret SQL file to `gs://site-media-release/_ops/cloud-sql/`;
- temporarily granted the Cloud SQL service agent `roles/storage.objectViewer` on `site-media-release`;
- ran `gcloud sql import sql site-release ... --database=site_release`;
- removed the temporary Cloud SQL service agent bucket grant;
- removed the temporary SQL object.

Important:

- This gives the backend runner broad database-level privileges on `site_release` because the current
  runtime and migration job both use `cms-back-release-runner`.
- A later hardening pass can split runtime DML and migration DDL into separate service accounts/users.

`cms-back` release branch was updated before deployment:

- `8fa772e` merged current `origin/develop` into `release`;
- `732014c` fixed the Cloud Run Jobs Cloud SQL flag in `cloudbuild.release.yaml`.

First build attempt:

- build `73926ddb-5e43-4218-8983-487fc673395d`;
- built and deployed `cms-back-release`;
- failed while creating `cms-back-release-migrate`;
- root cause: Cloud Run Jobs use `--set-cloudsql-instances`, not `--add-cloudsql-instances`.

Successful build:

- build `4ef7402b-9819-4002-ba0c-a0fe044e74eb`;
- image:
  `europe-central2-docker.pkg.dev/composite-ally-360719/cloud-run-source-deploy/cms-back-release/cms-back:4ef7402b-9819-4002-ba0c-a0fe044e74eb`;
- `cms-back-release` deployed and Ready;
- `cms-back-release-migrate` job created and Ready.

Backend release runtime:

- service URL: `https://cms-back-release-2ubpwinuqq-lm.a.run.app`;
- service account: `cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com`;
- Cloud SQL: `composite-ally-360719:europe-central2:site-release`;
- database: `site_release`;
- IAM DB user: `cms-back-release-runner`;
- media bucket: `site-media-release`;
- min instances `0`, max instances `3`;
- unauthenticated access disabled.

Migration execution:

```powershell
gcloud run jobs execute cms-back-release-migrate --region=europe-central2 --wait
```

Result:

- execution: `cms-back-release-migrate-lps9f`;
- completed successfully in about 16 seconds;
- applied migrations through `202607020001`.

Backend smoke:

- authenticated `GET /api/health` returned `200`;
- authenticated `GET /api/ready` returned `200`;
- `/api/ready` reported database status `ok`.

## Frontend Release Runtime - 2026-07-05

Frontend release branches were updated from current `origin/develop` and pushed:

- `site-front`: `61160f2`;
- `cms-front`: `add9906`, then `30c6bb6` for the Cloud Run port fix.

`cms-front` first build attempt:

- build `834909b0-1226-4bee-8430-cde2cc81e574`;
- image build and push succeeded;
- deploy failed because the container started Next.js on port `3000` while Cloud Run expected `PORT=8080`.

`cms-front` successful build:

- build `e8a9a344-58d8-4c7b-a5b6-30bd36697251`;
- service URL: `https://cms-front-release-2ubpwinuqq-lm.a.run.app`;
- ready revision: `cms-front-release-00002-tp6`;
- service account: `cms-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`;
- `CMS_BACK_URL=https://cms-back-release-2ubpwinuqq-lm.a.run.app`;
- min instances `0`, max instances `2`;
- unauthenticated access disabled.

`site-front` successful build:

- build `7464d74c-6581-4360-af9c-ed24cb9e0d40`;
- service URL: `https://site-front-release-2ubpwinuqq-lm.a.run.app`;
- ready revision: `site-front-release-00001-qnl`;
- service account: `site-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`;
- `CMS_BACK_URL=https://cms-back-release-2ubpwinuqq-lm.a.run.app`;
- `INDEXING_MODE=noindex`;
- min instances `0`, max instances `3`;
- unauthenticated access disabled.

Backend invoke IAM:

- `roles/run.invoker` on `cms-back-release` is granted to:
  - `cms-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`;
  - `site-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`.

Frontend smoke:

- authenticated `GET cms-front-release /health`: `200`;
- authenticated `GET cms-front-release /api/admin/pages`: `200`, empty release DB page list;
- authenticated `GET site-front-release /health`: `200`;
- authenticated `POST site-front-release /api/preview/pages/smoke-missing-page`: `404`, confirming the
  request reached `cms-back-release` and failed at the app/data layer for a missing page;
- unauthenticated `GET /health` returns `403` on both frontend services;
- latest ready revisions had no `ERROR` logs after smoke.

## Phase 8 - Temporary Direct Cloud Run IAP - 2026-07-11

Inventory before mutation:

- existing shared HTTPS LB:
  - forwarding IP: `34.160.235.199`;
  - URL maps: `custom-domains-fc9d`, `custom-domains-fc9d-http`;
  - active certificates include `actum.com.ua`, `www.actum.com.ua`, `strapi.actum.com.ua`,
    `erp.actum.com.ua`, and `tag.actum.com.ua`;
  - no release-specific NEGs/backend services/host rules were created in this slice.
- Cloud DNS zone listing failed for the active account with missing DNS permissions.

Decision:

- Use direct Cloud Run IAP as the temporary release reviewer bridge.
- Keep HTTPS LB + serverless NEG + IAP as the recommended final release entrypoint, deferred until the
  domain/DNS plan is ready.

Executed:

```powershell
gcloud run services update cms-front-release --region=europe-central2 --iap
gcloud run services update site-front-release --region=europe-central2 --iap
```

IAP access was granted on both release frontend services to:

- `privatemailofap@gmail.com`
- `yuriy.bishko@gmail.com`
- `po@actum.com.ua`
- `ap@modusmoses.com`
- `jamaslov@gmail.com`

Verified:

- `run.googleapis.com/iap-enabled=true` on both release frontend services.
- Cloud Run `roles/run.invoker` for both release frontend services is granted only to
  `service-865011807785@gcp-sa-iap.iam.gserviceaccount.com`.
- IAP `roles/iap.httpsResourceAccessor` on both release frontend services contains only the approved
  release access list above.
- `cms-front-release` and `site-front-release` have explicit IAP OAuth settings as of `2026-07-12`:
  `clientId=865011807785-dc2h038ejlv6hjlpaodmaliprs2rdvrp.apps.googleusercontent.com`.
  The client secret is not stored in git/docs/chat; only `clientSecretSha256` is visible through IAP
  settings, and the temporary local JSON used to apply the setting was deleted.
- Unauthenticated `GET /health` on both release frontend URLs returns `302` to Google OAuth, not content.

## Phase 8b - Release Indexing Controls - 2026-07-12

Decision:

- Keep `site-front-release` closed by IAP and keep app-level indexing controls enabled before any public
  opening.
- Treat the app-level controls as a second layer behind IAP, not as a replacement for the closed preview
  boundary.

Executed:

- Added `proxy.js` in `re-actum/site-front` branch `release`, commit `918a3fa`.
- The proxy sets `X-Robots-Tag: noindex, nofollow` when `INDEXING_MODE=noindex`.
- Added unit test `tests/unit/proxy-indexing.test.js`.
- Existing `app/robots.js` blocks all crawlers.
- Existing `app/sitemap.js` returns an empty sitemap list.
- Cloud Build `5b45bcce-1a94-4ade-82b0-2e52302d005f` deployed the change to `site-front-release`.

Verified:

- `npm run lint` passed in the `site-front-release` worktree.
- `npm test -- proxy-indexing.test.js` passed.
- `npx prettier --check proxy.js tests/unit/proxy-indexing.test.js` passed.
- Full `npm run format:check` still fails because of pre-existing formatting drift across the release
  worktree; do not autoformat the whole tree as part of this slice.
- New Cloud Run ready revision: `site-front-release-00002-8qm`.
- IAP stayed enabled after deploy.
- Cloud Run invoker for `site-front-release` stayed limited to
  `service-865011807785@gcp-sa-iap.iam.gserviceaccount.com`.
- Unauthenticated `GET /health` still returns `302` to Google OAuth.
- Fresh `ERROR` logs for the new revision were empty after deploy.

Follow-up:

- App-level `X-Robots-Tag` could not be read directly through the current CLI user-token flow because IAP
  correctly intercepts access. Repeat header/robots/sitemap smoke through the final LB/public entrypoint
  before opening the site.

## Still Deferred

These are intentionally deferred:

- add release secret values;
- create LB/IAP perimeter;
- replace temporary direct Cloud Run IAP with final LB/serverless NEG/IAP perimeter;
- import data;
- create CMS users;
- open any public access;
- change DNS/canonical or remove noindex/robots for the public site.
