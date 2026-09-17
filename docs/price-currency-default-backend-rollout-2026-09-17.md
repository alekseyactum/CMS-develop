# Price currency default: backend rollout — 2026-09-17

## Scope and behavior

Backend only. The owner requested commit, push and build; existing develop/release git-triggered
build-and-deploy pipelines were used after a successful governing GCP preflight. No frontend source,
frontend deployment, IAM, secrets, DNS, pipeline changes, migrations or content republishing were
performed in this rollout.

Backend commit: `0f0030c5e78d4986fc91a1abe07f57fac19886f6`
(`fix: default missing numeric price currency to UAH`). Develop and release were fast-forwarded
atomically from `fa589816ced48ba5208722da936685d4aaa2b730` to this same commit; no merge or force push.
The implementation branch `codex/price-currency-default` was also published.
Specification commit: `01bb371` on `codex/tz-2-to-tz-3-handoff`.

- Numeric prices with missing, null or blank currency use `UAH`.
- Explicit currencies are retained and normalized, e.g. ` usd ` becomes `USD`.
- Invalid explicit currency values remain validation errors; normalization must not hide them.
- Negotiable prices do not gain a currency or a fabricated numeric amount.
- Shared handling covers global and page-owned price content and structured-data output.
- Description-length recommendations remain non-blocking warnings.
- Existing historical versions are not rewritten. Omitting a previously explicit non-UAH currency
  in newly submitted numeric content means UAH, not inheritance from the prior version.

## Deployment evidence

Project: `composite-ally-360719`; region: `europe-central2`.

| Environment | Successful Cloud Build | Ready revision, 100% traffic | Rollback revision |
| --- | --- | --- | --- |
| develop | `2bcd8427-f5f3-45a0-ab1f-da1a706091f5` | `cms-back-develop-00289-ssr` | `cms-back-develop-00288-8z5` |
| release | `94d47f11-cb36-409b-8615-7b66f23f1fc6` | `cms-back-release-00078-xgj` | `cms-back-release-00077-wh5` |

Both `/api/health` and `/api/ready` returned HTTP 200, the expected full commit SHA and database
status `ok`. Both build records report `SUCCESS`.

## Verification

- Post-push full local suite: 970 tests passed, 117 suites, zero failures.
- Post-push `npm run build`: successful.
- Release live smoke: `POST /api/admin/global-sections/global_price/validate?locale=uk`, with inline
  `content` and `recordDiagnostics: false`, returned HTTP 200 and `validation.ok: true`.
- One request checked a numeric price without currency (UAH), explicit USD (retained), and a
  negotiable price (no currency or numeric amount).
- A 210-character description produced only `GLOBAL_PRICE_DESCRIPTION_LONG`; the other two
  descriptions were 80 characters. Zero validation errors, one warning.
- The response had `editor: null` and `validationRunId: null`. The inline-content validation path
  was audited to return before section creation or lifecycle persistence. No live draft was saved.
- Develop functional admin smoke was limited by `403: CMS user was not found` for the current
  operator. Cloud authentication and health/readiness worked. No user/role changes were made.
- Bounded Cloud Logging checks for `severity >= ERROR` on both new revisions returned zero entries
  in the last 30 minutes at verification time. This is a point-in-time smoke, not a soak test.

## Manual acceptance and rollback

Reload the CMS price editor, enter a numeric price without a currency field and click validation.
The ISO currency error should be absent. A long description can still produce a warning without
blocking validation. Saving/publishing is a separate editor action, not part of this rollout.

Preferred rollback: reviewed backend revert through the existing pipelines. Emergency traffic rollback
requires approval and targets the previous revisions above. No database rollback is required.

