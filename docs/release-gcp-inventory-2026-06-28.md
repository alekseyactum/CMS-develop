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

- `site-release` was not present during inventory.

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
- Release CMS service accounts, secrets, Cloud Run services, build triggers, and media bucket still need
  creation when mutation work is approved.
