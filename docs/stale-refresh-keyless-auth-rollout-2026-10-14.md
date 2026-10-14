# CMS page refresh: keyless dispatch authentication rollout

Date: 14 October 2026. Status: backend deployed to develop and release; refresh processing remains off.
This record supersedes the earlier local-only authentication status, not the historical rollout facts.

## Approved scope

The owner explicitly approved commit, push and deployment to both environments, followed by adding
the two non-secret authentication settings to their ordinary Cloud Build configuration. The existing
Google ID token and service-account identity replace the dedicated static dispatch secret. There is
no static-token fallback. This does not activate the queue or change IAM, secrets, content, frontend,
database schema, writer mode, schedules or cache/CDN configuration.

The governing playbook preflight passed for the expected operator and project before cloud work.
Both trigger filters remain exact: `^develop$` and `^release$`. Deployment used those existing
git-triggered pipelines, not a manual Cloud Run deploy.

## Deployed source and runtime

| Environment | Source commit | Successful Cloud Build | Ready revision, 100% traffic |
| --- | --- | --- | --- |
| develop | `515ce16e49d049b2ceb8083050e7f9da822d8a3f` | `45aa8ffe-a131-429d-a487-3e4f0d0c3f47` | `cms-back-develop-00317-4fx` |
| release | `89397ee5d65b5698847818e2cef25bc92e5955d9` | `210f5582-2c53-4362-8feb-f93a140f2b87` | `cms-back-release-00106-fcv` |

Develop build finished at `2026-10-14T04:53:35.207688Z`; release finished at
`2026-10-14T05:01:34.677706Z`. Release is a focused cherry-pick with the same patch-id, not a merge
of develop. The 16 pre-existing unrelated inter-branch file differences are preserved.

Both feature branches and environment branches were pushed without force. Subsequent documentation
clarifications were pushed only to the existing working branches: develop `dcfe886`, release `07a05a6`.
Those commits change two Markdown files and a comment in `.env.example`, not deployed application
code or configuration. They intentionally do not trigger another deployment.

| Setting | Develop | Release |
| --- | --- | --- |
| `CMS_PAGE_REFRESH_DISPATCH_AUDIENCE` | `https://cms-back-develop-2ubpwinuqq-lm.a.run.app` | `https://cms-back-release-2ubpwinuqq-lm.a.run.app` |
| `CMS_PAGE_REFRESH_DISPATCH_ALLOWED_SERVICE_ACCOUNTS` | `erp-back-release-cloudrunner@composite-ally-360719.iam.gserviceaccount.com` | Same explicitly approved account |

These values are in the API deploy steps of `cloudbuild.yaml` and `cloudbuild.release.yaml`, so a
normal subsequent build retains them. No secret was created or read. Cloud Run IAM remains enforced;
the service-level invoker lists remain unchanged. The common ERP identity already has invoker access
to both services. Different audiences do not constitute strict principal isolation between environments.

## Verification

- Production build and test TypeScript compilation passed in both checkouts.
- Develop: 253 current source spec files, 3,021 passed, one existing opt-in skip, no failures.
- Release: 252 current source spec files, 3,003 passed, one existing opt-in skip. Three localhost HTTP
  tests initially blocked by the execution sandbox passed when rerun outside it without code changes.
- Post-push focused authentication/config/controller/worker/command/cold-bootstrap suite: 50 passed
  in each checkout, zero failures or skips. Tests include real RSA verification, local HTTP flow,
  Google certificate transport timeout/retry/cache behavior and failure classification.
- Authenticated `/api/health` and `/api/ready` returned 200 in both environments, with exact expected
  source/build IDs and database status `ok`.
- OpenAPI exposes both required authentication headers and no retired secret header.
- Both deployed services returned 401 `REFRESH_DISPATCH_UNAUTHORIZED` for missing application
  Authorization, malformed Bearer credentials, and the retired static-secret header alone. A real
  operator token authenticated the Cloud Run transport in `X-Serverless-Authorization`; the operator
  was never represented as the ERP caller. No token or request header values were printed or stored.
- Bounded ERROR-or-higher metadata queries for both new revisions returned zero entries at verification.

### Deliberate live-verification limitation

The actual operator lacks the existing IAM permission needed to mint an ID token on behalf of the
ERP service account. The attempt returned permission denied; no IAM grant, impersonation workaround,
service-account key, temporary service or identity substitution was introduced.

Consequently, a successful allowed-ERP dispatch, a valid unlisted caller and a correctly signed
wrong-audience token are covered by automated tests but **not claimed as verified in live Cloud Run**.
The positive two-header flow remains to be checked from the ERP runtime before activating processing.
This limitation does not prevent deploying dormant code and is not evidence that ERP itself lacks
access: its attached runtime identity obtains its own tokens without operator impersonation.

Before activation, the ERP developer should call the matching CMS URL with one fresh Google ID token
in both headers, no query parameters and no body or `{}`. With gates still off, expected HTTP 200 is
`status: disabled`, `dispatchedBatches: 0`, `processedStages: 0`. Then confirm negative credential
and allowlist scenarios using only authorized test identities. Do not enable gates just for the smoke.

## Unchanged processing and jobs

Read/worker/command and source/cache capture gates remain absent/false. Both pre-existing one-minute
publication schedules remain `PAUSED`; no five-minute ERP caller was implemented here. No queue work,
page publication, migration or content write was performed by the smoke checks.

The normal builds updated the migration and publication-effects job images to their corresponding
builds. Their commands and disabled feature configuration were preserved; no job was executed by
these builds. The latest migration executions observed after rollout predate this deployment:
`cms-back-develop-migrate-hwg4n` and `cms-back-release-migrate-wh5fw`. Latest publication-effects
executions remain `cms-back-develop-publication-effects-wpvl4` and
`cms-back-release-publication-effects-wmpc5`.

## Rollback and next boundary

Immediate pre-rollout revisions: develop `cms-back-develop-00316-dgg` (source `4768251`), release
`cms-back-release-00105-hcm` (source `17ec4f3`). Prefer an approved focused revert/forward fix through
the ordinary pipeline. Emergency traffic rollback requires separate approval. This change requires
no schema rollback; keep existing additive tables and content. Keep workers off and schedules paused.

ERP owns the five-minute caller. Its configuration needs the target CMS base URL and matching token
audience, not a second static secret. Successful ERP runtime acceptance and a separate explicit
activation decision remain required before queue processing is enabled.
