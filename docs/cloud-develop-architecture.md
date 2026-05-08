# CMS Develop Cloud Architecture

This document fixes the agreed develop cloud architecture for the clean CMS implementation.

It started as a design decision record. The first minimal develop runtime was later created after
`gcp-infra-playbook` preflight and explicit confirmation.

Actual resource status is tracked in [`develop-runtime-state.md`](develop-runtime-state.md).

## Scope

Only the `develop` contour is in scope.

Future `release` services, database, secrets, triggers, domains, indexing policy, and rollback procedures
must be designed and approved separately.

## Governing Source

Google Cloud, IAM, Secret Manager, Cloud Run, Cloud SQL, Cloud Storage, Cloud Build, deployment discipline,
and rollback are governed by:

- local path: `G:\работа\Actum\develop\gcp-infra-playbook`
- project page: `gcp-infra-playbook/docs/projects/cms.md`

If this document conflicts with the playbook, the playbook wins until the conflict is explicitly resolved.

## GCP Contour

- GCP project: `composite-ally-360719`
- region: `europe-central2`
- Cloud SQL instance: existing `develop-eu`
- database to create: `site_develop`

The database name uses an underscore intentionally. Avoid `site-develop` because the dash makes SQL,
ORM configuration, scripts, and manual commands more fragile.

## GitHub And Deployment Shape

The current `CMS-develop` repository stays as an umbrella/context repository.

Canonical service repositories:

- `re-actum/site-front`
- `re-actum/cms-front`
- `re-actum/cms-back`

Develop branch convention:

- branch `develop` deploys the develop Cloud Run services.
- future branch `release` is reserved for future release Cloud Run services and is not approved by this
  document.

Develop Cloud Build triggers:

- `cms-site-front-develop` from `re-actum/site-front:develop` to `site-front-develop`
- `cms-front-develop` from `re-actum/cms-front:develop` to `cms-front-develop`
- `cms-back-develop` from `re-actum/cms-back:develop` to `cms-back-develop`

## Cloud Run Services

Planned develop services:

- `site-front-develop`
- `cms-front-develop`
- `cms-back-develop`

Runtime stacks:

- `site-front`: Next.js
- `cms-front`: Next.js
- `cms-back`: NestJS

Cloud Run resources:

- `site-front-develop`: min instances `0`, max instances `3`, CPU `1`, memory `1Gi`
- `cms-front-develop`: min instances `0`, max instances `2`, CPU `1`, memory `1Gi`
- `cms-back-develop`: min instances `0`, max instances `3`, CPU `1`, memory `1Gi`

CPU mode:

- CPU only during request.
- No always-allocated CPU for the first develop contour.

## Access Model

Public and admin entrypoints:

- `site-front-develop`: public web entrypoint, unauthenticated access allowed.
- `cms-front-develop`: closed Cloud Run service prepared for a future load-balancer/IAP entrypoint.
- `cms-back-develop`: not public for browser use, authentication required.

Ingress and auth:

- `site-front-develop`: ingress `all`, allow unauthenticated.
- `cms-front-develop`: ingress `internal-and-cloud-load-balancing`, no unauthenticated access.
- `cms-back-develop`: ingress `all`, no unauthenticated access.

The backend URL may technically exist, but direct browser-originated access is not an approved API path.
Allowed backend callers are the frontend runtime service accounts explicitly granted `roles/run.invoker`.

Do not tighten `cms-back-develop` to `internal-and-cloud-load-balancing` in the first develop contour
unless a matching internal service-to-service network path is introduced. Plain Cloud Run to Cloud Run
calls over the service URL need network reachability plus IAM. For this contour, IAM is the backend
boundary.

Admin user membership for the future IAP/load-balancer perimeter is intentionally not listed in this
repository. Access is managed in GCP by the owner.

## Service Accounts

Create separate runtime service accounts:

- `site-front-develop-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-front-develop-runner@composite-ally-360719.iam.gserviceaccount.com`
- `cms-back-develop-runner@composite-ally-360719.iam.gserviceaccount.com`

IAM intent:

- `site-front-develop-runner` can invoke `cms-back-develop`.
- `cms-front-develop-runner` can invoke `cms-back-develop`.
- `cms-back-develop-runner` can access Cloud SQL `develop-eu/site_develop` and the required backend
  secrets.
- `site-front-develop-runner` has no Cloud SQL access.
- `cms-front-develop-runner` has no Cloud SQL access.

## Request Flow

The browser must not call `cms-back-develop` directly.

Approved flow:

```text
browser -> site-front-develop -> cms-back-develop -> site_develop
browser -> cms-front-develop -> cms-back-develop -> site_develop
```

Rejected flow:

```text
browser -> cms-back-develop
```

This keeps the backend and database behind server-side frontends and Cloud Run service identity.

## API Contract

- `cms-back` owns the API contract.
- The API contract should be published as OpenAPI.
- `site-front` and `cms-front` should use generated typed clients.
- Breaking backend API changes must update the OpenAPI contract and frontend clients in the same feature
  cycle.

## Cloud SQL

Database:

- Cloud SQL instance: `develop-eu`
- database: `site_develop`
- database authentication: Cloud SQL IAM DB authentication through the backend service account
- IAM DB user: `cms-back-develop-runner`

Only `cms-back-develop` connects to the database.

Connection:

- Use Cloud SQL connector/runtime integration.
- Do not use a password-oriented database user for the CMS backend.
- Do not create a separate VPC connector for the first develop contour.

Backups:

- Do not define a separate backup/PITR policy for `site_develop`.
- Inherit the actual policy of the existing `develop-eu` instance.
- Before implementation, read and record the current instance configuration after GCP preflight.

Migrations:

- Explicit migrations live in the `cms-back` repository.
- Do not auto-run migrations on Cloud Run startup.
- Develop migrations run manually or explicitly after confirmation.
- The develop contour uses Cloud Run Job `cms-back-migrate-develop` as the controlled migration runner.
- The migration job uses the same service-account IAM database identity as `cms-back-develop`.

## Secret Manager

Secret names:

- `site-front-runtime-develop`
- `cms-front-runtime-develop`
- `cms-back-runtime-develop`
- `cms-admin-auth-develop`

Rules:

- Non-secret settings go to Cloud Run environment variables.
- Secret values go to Secret Manager.
- Database connection identity is service-account based; do not store a CMS database password secret.
- Repositories may contain `.env.example` only, without real values.
- Secrets, tokens, passwords, private keys, and live credential values must not be written to git,
  markdown, logs, or chat.

## Media Storage

Create one develop media bucket:

- `site-media-develop`

If the bucket name is globally unavailable, choose a project-prefixed alternative such as
`actum-site-media-develop`.

Storage model:

- `public/`: public read for published site media after a separate public media serving decision.
- `drafts/`: private draft or service media.

The first created develop bucket should stay private until the public media URL policy is implemented.

Write model:

- `cms-back-develop-runner`: read, write, and delete as needed.
- `site-front-develop-runner`: no write.
- `cms-front-develop-runner`: no write.

The admin frontend uploads through `cms-back`, not directly to the bucket.

Snapshots and render payloads:

- Store snapshots and render payloads in `site_develop`.
- Do not create a separate render-cache bucket for the first develop contour.

## Jobs

First develop contour:

- no separate worker service;
- no Cloud Tasks;
- no Cloud Scheduler.

`cms-back-develop` runs publish and rebuild jobs from admin/internal flows.

The code should still be structured so publish/rebuild handlers can later move into a worker without
rewriting the domain logic.

Operational Cloud Run Jobs are allowed for explicit operator actions such as schema migrations and protected
smoke checks. They must not become scheduled background workers without a separate decision.

## Domains And Indexing

Domains:

- First develop launch uses standard `*.run.app` URLs only.
- No custom domains or DNS changes in this step.

Indexing:

- `site-front-develop` is public but closed to indexing.
- Use `X-Robots-Tag: noindex, nofollow`.
- `robots.txt` should disallow crawling.
- `sitemap.xml` should be disabled or empty.

## CORS

`cms-back-develop` is not a public browser API.

- Do not set broad browser CORS.
- `Access-Control-Allow-Origin: *` is forbidden.
- If a future browser-direct call is required, add a narrow allowlist by separate decision.

## CMS Admin Auth

The intended external entry to `cms-front-develop` is a future load-balancer/IAP perimeter. Until that is
created, `cms-front-develop` remains closed at Cloud Run ingress/auth level.

Inside the CMS:

- CMS users, roles, and permissions live in `site_develop`.
- `cms-back` validates CMS sessions or tokens for admin actions.
- IAP identity may help establish access context, but it does not replace CMS roles.

Open design note:

- the browser must not call `cms-back-develop` directly;
- `cms-front` must act as the server-side admin entrypoint for browser-originated admin requests;
- implementation must still define the exact session flow between `cms-front` and `cms-back`;
- the chosen flow must preserve both boundaries: Cloud Run service identity for service-to-service calls
  and CMS user identity/roles for admin authorization.

## Health And Readiness

Minimum endpoints:

- `/health` for all services.
- `/ready` additionally for `cms-back-develop`.

Backend readiness should verify the critical runtime dependencies, including database connectivity.
Backend readiness must not return infrastructure configuration such as Cloud SQL connection names, database
names, IAM database users, bucket names, or secret references.

After the first database foundation stage, backend readiness verifies Cloud SQL IAM access to `site_develop`
without a password.

## Logging

Develop observability baseline:

- Cloud Logging enabled by default.
- Request logs for all services.
- Structured JSON logs for `cms-back`.
- Propagate `requestId` or `correlationId` from frontends to backend.
- Never log secrets, tokens, passwords, private keys, or raw credentials.
- No custom dashboards or alerts in the first develop step.

## Rollback

Code rollback:

- Revert through git in the affected service repository.
- Push `develop`.
- Let Cloud Build deploy the corrected revision.

Urgent Cloud Run rollback:

- Use only as a temporary measure.
- Run GCP preflight first.
- Record the current revision, target previous known-good revision, reason, and follow-up git fix.

Database rollback:

- Do not run blind down migrations.
- For risky migrations, define backup/restore or forward-fix plan before execution.

Content rollback:

- Use CMS snapshot history.
- Rollback should create a new current snapshot from a historical payload.

## Not Approved By This Document

This document does not approve:

- changing release or production-like runtime;
- creating release Cloud Run services;
- changing DNS or custom domains;
- enabling indexing;
- creating Cloud Tasks, Scheduler, worker services, or extra databases;
- creating or printing secret values.
