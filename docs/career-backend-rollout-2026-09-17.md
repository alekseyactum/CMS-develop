# Career backend rollout — 2026-09-17

Owner explicitly approved commit/push, backend deployment and migrations for develop/release.
GCP preflight passed for the expected account/project before cloud reads or changes.

## Source and scope

- Backend repository: `re-actum/cms-back`.
- Commit: `59001f38e1454cf90c6df8b6fcf34bcfe9ce55f3`.
- Feature branch: `codex/career-backend`; `develop` and `release` both fast-forwarded from
  `b88bbd516a5d9c1bb2d69445cdeb31fa3ac301eb`. No merge conflict or history rewrite.
- Requirements commit: `7e939c0` in `CMS-develop:codex/tz-2-to-tz-3-handoff`.
- Normal existing Cloud Build triggers, unchanged pipeline/IAM/DNS/runtime integration configuration.
- Fixed career page schema, ERP vacancies, safe published vacancy refresh, private application/outbox
  backend and shared internal `global_career_form.hrEmail` are included.
- No frontend deployment, career page bootstrap/publication, vacancy import or real application delivery.

## Develop evidence

- Build `721f5148-6efd-4090-8bd6-d0a49409fb91`: SUCCESS.
- Ready revision `cms-back-develop-00287-64t`, 100% traffic.
- Previous revision `cms-back-develop-00286-jgh`.
- Inspect execution `cms-back-develop-migrate-pdf5p`: only `202609170001`, `202609170002` pending;
  no pre-existing career tables.
- Migration execution `cms-back-develop-migrate-72677`: SUCCESS.
- Verify execution `cms-back-develop-migrate-kwcpb`: both IDs applied, no pending migrations,
  all six tables present and `en`, `ru`, `uk` refresh rows initialized at generation zero.
- `/api/health` and `/api/ready`: HTTP 200 with expected SHA; database status `ok`.
- OpenAPI exposes new career routes. Bounded new-revision ERROR-log check returned zero entries.

## Release evidence

- Build `9311751f-8bb6-426d-a19d-f19c89a4e22d`: SUCCESS.
- Ready revision `cms-back-release-00076-l8p`, 100% traffic.
- Previous revision `cms-back-release-00075-k59`.
- Inspect execution `cms-back-release-migrate-2nhqr`: only the same two migrations pending,
  no pre-existing career tables.
- Migration execution `cms-back-release-migrate-kch7c`: SUCCESS; logs confirm both IDs applied.
- Verify execution `cms-back-release-migrate-qnngt`: both IDs applied, no pending migrations,
  six tables and three zero-generation locale rows verified.
- `/api/health` and `/api/ready`: HTTP 200, expected SHA, database status `ok`.
- Authorized `GET /api/admin/career/vacancies?locale=uk&limit=1`: HTTP 200, empty list as expected.
- Authorized `GET /api/admin/career/applications/integration-status`: HTTP 200; all four readiness flags
  (`hrEmailConfigured`, `emailConfigured`, `erpConfigured`, `resumeStorageConfigured`) are false.
- OpenAPI exposes 13 career routes and the `global_career_form` key.
- Bounded new-revision ERROR-log check returned zero entries.

## Migration contract

`202609170001` adds `cms_career_vacancies`, `cms_career_vacancy_translations`,
`cms_career_runtime_refresh` and three locale rows. `202609170002` adds
`cms_career_applications`, `cms_career_application_deliveries`, `cms_career_application_rate_limits`.
Existing page/source data is not rewritten. The HR destination uses existing versioned section tables;
there is no separate HR settings table.

The normal migration runner executes every pending ID. Read-only prechecks therefore verify that no
unrelated migration is pending before each execution. Inspect/verify use temporary execution overrides
on the existing migration jobs, not permanent command/configuration changes. No two executions run
against the same database concurrently. The check script is in the backend repository at
`scripts/career-migration-check.cjs` and is invoked inline in the container working directory.

## Verification limits and next integration stage

Post-push backend build and all 919 tests passed. Release push uses the identical tested SHA.
Current operator Cloud Run access works, but the same identity receives 403 on develop CMS admin career
methods. No alternative user was impersonated and no role was granted. Functional CMS UI acceptance
must be completed under an existing authorized editor identity after frontend implementation.
The same operator identity already has access in release; read-only career API smoke passed there.

No `CAREER_*` configuration existed in either backend service before rollout. This release deliberately
does not create secrets, a resume bucket, scheduler, SMTP or ERP receiver. Intake/delivery remain disabled
until separately configured. HR email must be saved and published in the shared global form; draft edits
are inert, and retries use the recipient captured in the original accepted application.

## Rollback

Normal rollback is a reviewed revert through the same backend pipelines, keeping develop/release aligned.
Prior known-good commit is `b88bbd516a5d9c1bb2d69445cdeb31fa3ac301eb`; prior revisions are recorded above.
Emergency traffic rollback is a separate explicit operator action. Leave additive tables and any accepted
applications intact: no destructive down migration or data deletion is needed for code rollback.
