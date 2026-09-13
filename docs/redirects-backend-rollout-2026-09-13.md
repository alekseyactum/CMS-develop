# Redirect registry backend rollout — 2026-09-13

Scope authorized by the owner: apply the backend migration and push/deploy develop and release.
This is not the public domain cutover or import/activation of the real migration map.

## Source and database

- Backend commit: `db0d3a4ce68a4f35aa925e2faa88f11c433c01f4`.
- Remote `develop`, `release`, and `codex/redirect-registry` point to that same commit; no force push.
- Migration: `202609130001`, additive registry/revision/audit/deletion-guard schema.
- MySQL: `8.0.43-google` in both environments.
- Existing migration jobs ran an execution-only scoped operator payload before application deployment.
  Permanent job command/arguments, IAM, secrets and service origins were not manually changed.
- Develop apply: `cms-back-develop-migrate-rq7sf`, successful.
- Release apply: `cms-back-release-migrate-9szxj`, successful.
- Develop: 622 pages, 622 guards. Release: zero pages and guards before and after migration.
- Both registries and audit tables are empty. No real rules activated, no content deleted or copied.
- Synthetic page deletion and pending-target FK checks passed against real MySQL; test rows rolled back.
- Successful pre-existing release backup: `1789218000000`.

## Delivery and verification

- Local build passed. After push, the complete test suite passed again: 811 tests, zero failures/skips.
- Develop build `db25d05b-91a7-41a9-b8ea-88c0fa7afe6b`: successful.
- Develop revision `cms-back-develop-00280-csp`: ready, 100% traffic, expected commit.
- Develop authenticated `/api/health` and `/api/ready`: HTTP 200; database ready.
- Develop resolver: published `/contacts` gives `kind=page`; alternate domain/scheme/trailing slash
  combine into a single redirect decision; unknown address gives `kind=not_found`; foreign host gives 400.
  Successful decisions have API HTTP 200 and `Cache-Control: no-store`.
- Develop post-deployment guard reconciliation: `cms-back-develop-migrate-lnncb`, successful;
  zero missing guards, counts unchanged, transactional FK smoke passed again.
- Release build `2a1618ce-0ef3-430d-b5a7-8e3563527e1d`: successful.
- Release revision `cms-back-release-00069-7nl`: ready, 100% traffic, expected commit.
- Release authenticated `/api/health` and `/api/ready`: HTTP 200; database ready.
- Release resolver: canonical and alternate-domain unknown addresses give `kind=not_found`, as expected
  for its empty page table; a foreign host gives HTTP 400. Decisions have `Cache-Control: no-store`.
- Release post-deployment guard reconciliation: `cms-back-release-migrate-m9cqf`, completed successfully;
  zero missing guards, all counts remain zero, transactional FK smoke passed with rolled-back fixtures.

Live admin smoke under the current Google Cloud operator identity returned HTTP 403
`CMS_USER_NOT_FOUND`. That identity is not registered in CMS. No roles/users were changed and no other
identity was substituted. Admin endpoints have local HTTP/permission tests; the deployed admin workflow
still needs a check through CMS under an existing editor/admin account.

## Remaining frontend work and limits

CMS-front must implement registry/page views, prepare/activate/import confirmation and error handling.
Site-front must call the resolver before loading payload and emit actual HTTP 301/404/410/503 responses.
Backend deployment alone does not redirect the current public site.

Existing `PUBLIC_SITE_ORIGIN` values remain unchanged: develop `https://www.actum.com.ua`, release
`https://actum.com.ua`. The future agreed canonical origin is `https://actum.ua`, but changing it and
DNS/TLS/IAP/indexing requires a separate authorized cutover. Resolver smoke used the current logical
origin, not the develop browser host. Before site-front integration, explicitly settle its test-host policy;
do not pass arbitrary forwarded hosts or silently rewrite the configured origin.

Before bulk real-map import, run representative scale and complete-map HTTP checks with the frontends.

## Rollback

Previous application commit: `0c4936c141880b66b4d6c34041fe1d792d9258dd`.
Previous ready revisions: develop `cms-back-develop-00279-72h`, release `cms-back-release-00068-6tn`.
Use the normal reviewed code-revert/promotion pipeline. Leave the additive registry/guard/audit tables
intact; do not blindly drop them, delete content, reset branch history, or open anonymous access.
