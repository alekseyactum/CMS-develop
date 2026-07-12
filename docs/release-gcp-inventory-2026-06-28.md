# CMS Release GCP Inventory - 2026-06-28

This inventory records non-secret GCP facts read before creating the CMS `release` contour.

No secret values were read. No GCP resources were created or changed while collecting this inventory.

## Preflight

Playbook preflight passed:

- account: `privatemailofap@gmail.com`
- project: `composite-ally-360719`
- Cloud SDK: `561.0.0`
- access token check: passed

## Cloud SQL

Existing Cloud SQL instances observed:

- `actum-replica`
- `actum-strapi`
- `bank`
- `develop-eu`
- `telegram`

Planned CMS release instance:

- `site-release` was not present during the original `2026-06-28` inventory.

`actum-strapi` baseline requested for sizing:

- connection name: `composite-ally-360719:europe-central2:actum-strapi`
- database version: `MYSQL_8_0_43`
- edition: `ENTERPRISE`
- tier: `db-g1-small`
- availability type: `ZONAL`
- region: `europe-central2`
- zone: `europe-central2-b`
- disk: `10 GB`, `PD_SSD`
- storage auto-resize: enabled
- backups: enabled
- retained backups: `7`
- binary logs: enabled
- transaction log retention: `7` days
- deletion protection: enabled
- private network: `default`
- public IPv4: enabled
- SSL mode: `ENCRYPTED_ONLY`
- database flags:
  - `sort_buffer_size=256000000`
  - `innodb_lock_wait_timeout=15000`
  - `character_set_server=utf8mb4`

CMS release should mirror `actum-strapi` for initial size/tier/storage/backup posture, but should not be a
blind copy:

- keep the CMS release decision to use Cloud SQL IAM authentication;
- add `cloudsql_iam_authentication=on` unless implementation proves a different approved auth path;
- avoid copying the old `actum-strapi` authorized public networks by default;
- prefer runtime access through Cloud Run/Cloud SQL connector and approved service accounts.

## Cloud Run

CMS/develop services observed:

- `cms-back-develop`
- `cms-front-develop`
- `site-front-develop`

Planned CMS release services were not present during inventory:

- `cms-back-release`
- `cms-front-release`
- `site-front-release`

Existing older public-site/Strapi release resources are present, including Cloud Run services named
`actum` and `strapi`. They are old contour resources and must not be treated as the new CMS release
services.

## Cloud Build

No Cloud Build triggers matching the planned CMS release services were observed with the CMS/site-front
filter:

- `site-front-release`
- `cms-front-release`
- `cms-back-release`

Existing non-CMS triggers for old `Actum`, `Strapi`, ERP, Telegram, and other projects were observed.

## Service Accounts

CMS/develop service accounts observed:

- `site-front-develop-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-front-develop-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-back-develop-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-develop-build-runner@composite-ally-360719.iam.gserviceaccount.com`

Existing old site release service account observed:

- `actum-site-front-release-cloud@composite-ally-360719.iam.gserviceaccount.com`

Planned CMS release service accounts were not present during inventory:

- `site-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com`

The old `actum-site-front-release-cloud` account must not be reused as the new CMS release service account
without a separate explicit decision.

## Secret Manager

CMS/develop secret metadata observed:

- `site-front-runtime-develop`
- `cms-front-runtime-develop`
- `cms-back-runtime-develop`
- `cms-admin-auth-develop`

Planned CMS release secrets were not present during inventory:

- `site-front-runtime-release`
- `cms-front-runtime-release`
- `cms-back-runtime-release`
- `cms-admin-auth-release`

Only secret metadata was read. Secret values were not read.

## Cloud Storage

Existing CMS/develop media bucket observed:

- `site-media-develop`

Planned CMS release media bucket was not present during inventory:

- `site-media-release`

## Load Balancing And Serverless NEGs

Existing serverless NEGs and load-balancer backend services are already used for old `actum`, `strapi`,
ERP, and server-side tagging domains.

Observed URL map:

- `custom-domains-fc9d`

Current old URL-map behavior includes `actum.com.ua`, `www.actum.com.ua`, `strapi.actum.com.ua`,
`tag.actum.com.ua`, and `erp.actum.com.ua`.

Important note:

- the current URL map redirects `actum.com.ua` to `www.actum.com.ua`;
- the CMS release architecture wants `https://actum.com.ua` as canonical;
- do not change this old public-site URL map as part of early release infrastructure work.

## Immediate Implications

- The release CMS contour is not already created.
- `site-release` can be created without colliding with an existing Cloud SQL instance.
- The exact Cloud SQL baseline is now known: `db-g1-small`, `10 GB`, `PD_SSD`, ZONAL, backups/binlog 7
  days, deletion protection.
- CMS release DB auth should differ from `actum-strapi` by enabling Cloud SQL IAM authentication.
- Release CMS secrets, Cloud Run services, build triggers, and media bucket still need creation when
  mutation work is approved.

## Post-Inventory Changes In This Work Slice

After explicit approval for steps 1-3, the following changes were made:

- remote `release` branches were created in:
  - `re-actum/site-front`
  - `re-actum/cms-front`
  - `re-actum/cms-back`
- `cloudbuild.release.yaml` was added and pushed to each service release branch;
- release runtime service accounts were created:
  - `site-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
  - `cms-front-release-runner@composite-ally-360719.iam.gserviceaccount.com`
  - `cms-back-release-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-back-release-runner` was granted:
  - `roles/cloudsql.client`
  - `roles/cloudsql.instanceUser`

After explicit approval on `2026-07-05`, the release Cloud SQL boundary was created:

- `site-release`
  - `MYSQL_8_0_43`
  - `ENTERPRISE`
  - `db-g1-small`
  - `ZONAL`
  - `europe-central2-b`
  - private IP: `10.89.62.17`
  - public IP: `34.116.243.97`
  - authorized networks: empty
  - Cloud SQL connector enforcement: `REQUIRED`
  - SSL mode: `ENCRYPTED_ONLY`
  - `10 GB` `PD_SSD`
  - storage auto-resize: enabled
  - backups and binary logs: enabled
  - transaction log retention: `7` days
  - deletion protection: enabled
  - flags:
    - `character_set_server=utf8mb4`
    - `cloudsql_iam_authentication=on`
    - `innodb_lock_wait_timeout=15000`
    - `sort_buffer_size=256000000`
- database `site_release`
  - charset: `utf8mb4`
  - collation: `utf8mb4_unicode_ci`
- Cloud SQL IAM DB user:
  - `cms-back-release-runner`
  - type: `CLOUD_IAM_SERVICE_ACCOUNT`

Connectivity note:

- `site-release` was initially created private-only.
- Public IP was enabled later on `2026-07-05` to support local Cloud SQL Auth Proxy access.
- The old `actum-strapi` public authorized networks were not copied.
- Direct broad public network access is not intended; Cloud SQL connectors are required.
- Cloud SQL MySQL still includes the built-in `root` user, so password authentication is not globally
  disabled at the database engine level.

No release secrets, media bucket, Cloud Run service, Cloud Build trigger, load balancer, IAP policy,
migration, import, or CMS user was created in this slice.

## Post-Cloud-SQL Release Resources - 2026-07-05

Release Secret Manager containers were created:

- `site-front-runtime-release`
- `cms-front-runtime-release`
- `cms-back-runtime-release`
- `cms-admin-auth-release`

Secret notes:

- replication: automatic
- no secret values are recorded in this repository
- no secret versions were intentionally added in this slice
- `roles/secretmanager.secretAccessor` grants:
  - `site-front-runtime-release` -> `site-front-release-runner`
  - `cms-front-runtime-release` -> `cms-front-release-runner`
  - `cms-back-runtime-release` -> `cms-back-release-runner`
  - `cms-admin-auth-release` -> `cms-back-release-runner`

Release media bucket was created:

- `gs://site-media-release`
- location: `EUROPE-CENTRAL2`
- storage class: `STANDARD`
- uniform bucket-level access: enabled
- public access prevention: enforced
- soft delete retention: 7 days
- `cms-back-release-runner` has `roles/storage.objectAdmin`
- frontend release runners have no direct bucket write grant
- no develop media was copied

No release Cloud Run service, Cloud Build trigger, load balancer, IAP policy, migration, import, CMS user,
or public access was created in this post-Cloud-SQL slice.

## Backend Release Runtime - 2026-07-05

Database privilege update:

- `cms-back-release-runner` was granted `ALL PRIVILEGES` on `site_release.*`.
- Grant was applied through a one-time Cloud SQL SQL import.
- No root password was stored or recorded in git/docs/chat/logs.
- Temporary GCS object and temporary Cloud SQL service agent bucket read grant were removed after import.

`cms-back` release branch:

- updated from current `origin/develop`;
- pushed release commits:
  - `8fa772e`
  - `732014c`

Cloud Build:

- failed first build: `73926ddb-5e43-4218-8983-487fc673395d`
  - service deploy succeeded;
  - migration job creation failed because Cloud Run Jobs require `--set-cloudsql-instances`.
- successful build: `4ef7402b-9819-4002-ba0c-a0fe044e74eb`
  - image pushed and deployed;
  - migration job created.

Cloud Run backend service:

- `cms-back-release`
- URL: `https://cms-back-release-2ubpwinuqq-lm.a.run.app`
- status: Ready
- service account: `cms-back-release-runner`
- Cloud SQL instance attached: `composite-ally-360719:europe-central2:site-release`
- `DB_NAME=site_release`
- `DB_IAM_USER=cms-back-release-runner`
- `MEDIA_BUCKET=site-media-release`
- unauthenticated access: disabled
- min instances: `0`
- max instances: `3`

Cloud Run migration job:

- `cms-back-release-migrate`
- status: Ready
- execution `cms-back-release-migrate-lps9f` completed successfully
- migrations applied through `202607020001`

Smoke:

- authenticated `GET /api/health`: `200`
- authenticated `GET /api/ready`: `200`
- database dependency status from readiness: `ok`

At this backend runtime point, no release frontend service, Cloud Build trigger, load balancer, IAP policy,
import, CMS user, or public access was created.

## Frontend Release Runtime - 2026-07-05

Release frontend Cloud Run services now exist:

- `cms-front-release`
  - URL: `https://cms-front-release-2ubpwinuqq-lm.a.run.app`
  - status: Ready
  - ready revision: `cms-front-release-00002-tp6`
  - service account: `cms-front-release-runner`
  - `CMS_BACK_URL=https://cms-back-release-2ubpwinuqq-lm.a.run.app`
  - min instances: `0`
  - max instances: `2`
  - unauthenticated access: disabled
- `site-front-release`
  - URL: `https://site-front-release-2ubpwinuqq-lm.a.run.app`
  - status: Ready
  - ready revision: `site-front-release-00001-qnl`
  - service account: `site-front-release-runner`
  - `CMS_BACK_URL=https://cms-back-release-2ubpwinuqq-lm.a.run.app`
  - `INDEXING_MODE=noindex`
  - min instances: `0`
  - max instances: `3`
  - unauthenticated access: disabled

Release backend invocation IAM:

- `cms-front-release-runner` has `roles/run.invoker` on `cms-back-release`.
- `site-front-release-runner` has `roles/run.invoker` on `cms-back-release`.

Cloud Build results:

- `cms-front-release`
  - failed build/deploy: `834909b0-1226-4bee-8430-cde2cc81e574`
  - failure reason: container listened on port `3000` while Cloud Run expected `PORT=8080`
  - successful build/deploy: `e8a9a344-58d8-4c7b-a5b6-30bd36697251`
- `site-front-release`
  - successful build/deploy: `7464d74c-6581-4360-af9c-ed24cb9e0d40`

Smoke:

- authenticated `GET cms-front-release /health`: `200`
- authenticated `GET cms-front-release /api/admin/pages`: `200`
- authenticated `GET site-front-release /health`: `200`
- authenticated `POST site-front-release /api/preview/pages/smoke-missing-page`: `404` from the app layer
  for a missing page
- unauthenticated `GET /health` on both frontend services: `403`
- no `ERROR` logs on latest ready frontend revisions after smoke

Still not created/configured:

- release Cloud Build triggers;
- final load balancer / serverless NEGs / IAP perimeter;
- CMS users and CMS role assignments;
- data import and published content snapshots;
- public domain/DNS/certificate cutover.

## Temporary Direct Cloud Run IAP - 2026-07-11

Read-only inventory before IAP mutation:

- Existing shared HTTPS LB:
  - forwarding IP: `34.160.235.199`
  - forwarding rules: `custom-domains-fc9d-fe`, `custom-domains-fc9d-fe-http`
  - URL maps: `custom-domains-fc9d`, `custom-domains-fc9d-http`
  - target HTTPS proxy: `custom-domains-fc9d-proxy`
  - active managed certificates include:
    - `actum.com.ua`
    - `www.actum.com.ua`
    - `strapi.actum.com.ua`
    - `erp.actum.com.ua`
    - `tag.actum.com.ua`
- Existing serverless NEGs did not include release frontend services.
- Cloud DNS managed zone listing failed for `privatemailofap@gmail.com` because the active account lacks
  DNS permissions in `composite-ally-360719`.

Release frontend direct IAP state after mutation:

- `cms-front-release`
  - `run.googleapis.com/iap-enabled=true`
  - Cloud Run invoker: `service-865011807785@gcp-sa-iap.iam.gserviceaccount.com`
  - IAP access: approved release email list only
  - IAP OAuth settings were configured with the dedicated release OAuth client
    `865011807785-dc2h038ejlv6hjlpaodmaliprs2rdvrp.apps.googleusercontent.com`; only the
    `clientSecretSha256` is visible in IAP settings, and the temporary local client-secret JSON was deleted.
- `site-front-release`
  - `run.googleapis.com/iap-enabled=true`
  - Cloud Run invoker: `service-865011807785@gcp-sa-iap.iam.gserviceaccount.com`
  - IAP access: approved release email list only
  - IAP OAuth settings were configured with the same dedicated release OAuth client
    `865011807785-dc2h038ejlv6hjlpaodmaliprs2rdvrp.apps.googleusercontent.com`; only the
    `clientSecretSha256` is visible in IAP settings, and the temporary local client-secret JSON was deleted.

Approved release IAP email list:

- `privatemailofap@gmail.com`
- `yuriy.bishko@gmail.com`
- `po@actum.com.ua`
- `ap@modusmoses.com`
- `jamaslov@gmail.com`

Smoke:

- unauthenticated `GET https://cms-front-release-2ubpwinuqq-lm.a.run.app/health`: `302` to Google OAuth
- unauthenticated `GET https://site-front-release-2ubpwinuqq-lm.a.run.app/health`: `302` to Google OAuth

The final LB/serverless NEG/IAP/domain perimeter remains deferred.
