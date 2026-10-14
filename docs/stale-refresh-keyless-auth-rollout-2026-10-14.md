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

## Activation readiness checked on 14 October

The owner requested the readiness check and activation plan without waiting for the CMS queue UI.
This follow-up did not authorize activation. Writer mode, service environments, IAM, content and
schedules were not changed. The playbook preflight passed before reading cloud state.

### Actual writer and queue state

| Check | Develop | Release |
| --- | --- | --- |
| Backend writer mode / generation | `legacy` / `0` | `legacy` / `0` |
| Mode transitions | 0 | 0 |
| Accepted publication operations / plans / effects | 0 / 0 / 0 | 0 / 0 / 0 |
| Refresh source events / demands / executions | 0 / 0 / 0 | 0 / 0 / 0 |
| Current published page heads | 255 | 8 |
| Editorial pages missing a locale group, including drafts | 0 | 0 |
| Missing, foreign or non-published current snapshots | 0 | 0 |
| Current editorial head versus list projection mismatch | 1 | 0 |
| Recorded scheduled refresh tick | Never | Never |

Both migration ledgers contain 56 entries. Source/cache capture and read/worker/command flags remain
absent; seeded `automatic_paused=false` does not enable processing. The four configured source delays
are still 30 minutes each. This is a publication-metadata check, not a full content audit or an
additional approval gate for the initial queue.

The develop mismatch is a Ukrainian `case_page`, ID `253a4361-5ec3-4d47-8982-d17093321d3a`, with
current published snapshot `38b0f3fd-a759-4e3a-9908-dd01440d8739` and no editorial list projection.
Its authoring status is `draft`; that alone does not invalidate an existing published head.
The follow-up inspection below established the missing required excerpt. Reconcile this exact
published snapshot before accepting develop cutover. Do not blindly republish the working page,
adopt unrelated drafts or insert a guessed projection. Release has no mismatch in the checked metadata.

The refresh worker requires database writer mode `exact`. Merely enabling its environment flags
while leaving `legacy` is insufficient. Both deployed CMS fronts also currently default to legacy:
`CMS_PUBLICATION_MODE` is absent. Their exact-mode client implementation already exists; ordinary
publication does not need a new frontend implementation from scratch.

### Frontend and cache evidence

All six checked API/CMS/site services had one ready revision receiving 100 percent traffic. Backend
source and revisions are unchanged from the deployment table above. Frontend source was checked at
the exact deployed commits, not at the older local worktree HEADs.

| Service | Deployed source | Ready revision |
| --- | --- | --- |
| `cms-front-develop` | `fbf73b6297f007441c10bac828f61dc54b045c3c` | `cms-front-develop-00230-5bp` |
| `cms-front-release` | `720561aa40cb3e3bd2037c3704057d2ea98145e9` | `cms-front-release-00031-4k9` |
| `site-front-develop` | `bd025aed38b538b106192572190520dea70d7f40` | `site-front-develop-00117-qhz` |
| `site-front-release` | `2ef54216e60629d560412759bd56943e31cfe733` | `site-front-release-00023-qwl` |

The deployed site page, layout and route-resolver fetches use `cache: "no-store"`. React request
memoization is not a persistent page cache. No persistent HTML cache override was found in these
deployed sources. The cloud inventory contains no serverless NEG targeting either new `site-front`
service and no Cloud Run domain mappings. The project's existing CDN-enabled image/static/assets
backends target the older `actum` service, not these two new site services.

The intended current HTML-page configuration is therefore origin `no_store`, CDN `absent`, subject
to the final authorized-browser response-header check. Direct probes reached IAP rather than the
application: anonymous requests returned 302 and the operator ID-token attempt returned 401.
Application HTML `Cache-Control` headers are not claimed as live-verified; no access policy was
changed to obtain them. Check representative pages through the normal authorized browser before
activating this configuration.

This conclusion is specific to HTML page paths. `sitemap.xml` has a 300-second data revalidation
interval; images/static assets have separate caches. The current refresh cache obligation targets
the affected page paths, not sitemap XML or assets. The existing `/api/revalidate` tag endpoint is
not a `cms-cache-delivery-v1` receiver and must not be configured as one. Provisioning a CDN or its
invalidation receiver remains a separate pre-public-launch task.

### Proposed coordinated activation

This plan is not an execution receipt. Run it only after separate approval, develop first, then
release after develop acceptance. Re-read revisions, modes, generations and queues at execution time.

1. Finish the scoped develop projection diagnosis and authorized-browser cache check. Obtain a
   successful allowed-ERP call with gates still off: HTTP 200, `status: disabled`, zero work. The
   CMS queue UI is not required for these preparation steps.
2. Prepare the approved operator invocation of `transitionPublicationWriterMode` with observed
   mode/generation, identity and reason. The checked-in local-only rehearsal script is not a shared-DB
   tool. Never substitute a raw mode-row update. Review the full writer-cutover runbook, including
   connection capacity, every publishing process/job and the compatible rollback target.
3. Establish a short coordinated pause for publication-producing operations and source mutations,
   including relevant ERP imports/maintenance. Keep the ERP caller disabled during configuration;
   drain in-flight operations and prevent old or local instances from writing with stale flags.
4. Through normal approved pipelines, install the backend settings below and server-side
   `CMS_PUBLICATION_MODE=exact` on the CMS front while publication traffic remains paused. Ensure all
   actual writers use the same source-capture policy; do not launch the old publication-effects jobs
   with their dormant configuration. Re-check that old plans/effects have not appeared.
5. Invoke the guarded database transition with the freshly observed generation. `NOWAIT`/CAS refusal
   is a stop-and-inspect condition, not a reason to bypass the fence. Refresh CMS browser sessions so
   they receive the new server-provided mode. Verify exact admission, legacy rejection and guarded Save.
6. Run the approved develop acceptance scenario: an exact publication/replay, a bounded ERP dispatch,
   and one scoped source refresh that leaves unrelated drafts unpublished. Check the durable receipt,
   journal, page output and cache outcome `not_applicable`, not a fictional successful CDN purge.
7. Enable the ERP five-minute recurrence and resume normal source/publication traffic. Verify durable
   progress and reporting with no reliance on HTTP traffic keeping an instance alive. Keep the old
   one-minute schedules paused under the queue conditions below. Repeat the approved sequence on
   release after develop acceptance; do not introduce a separate starter-queue content approval gate.

| Configuration | Intended enabled value |
| --- | --- |
| `CMS_PAGE_REFRESH_READ_ENABLED` | `true` |
| `CMS_PAGE_REFRESH_WORKER_ENABLED` | `true` |
| `CMS_PAGE_REFRESH_COMMANDS_ENABLED` | `true` |
| `CMS_REVIEW_REFRESH_CAPTURE_ENABLED` | `true` |
| `CMS_EDITORIAL_REFRESH_CAPTURE_ENABLED` | `true` |
| `CMS_LAWYER_PROFILE_REFRESH_CAPTURE_ENABLED` | `true` |
| `CMS_PAGE_REFRESH_CACHE_CAPTURE_ENABLED` | `true` |
| `CMS_PUBLISHED_SECTION_REFRESH_CAPTURE_ENABLED` | `true` |
| `CMS_PAGE_REFRESH_ORIGIN_CACHE_MODE` | `no_store`, for the verified private HTML topology |
| `CMS_PAGE_REFRESH_CDN_CACHE_MODE` | `absent`, for the verified private HTML topology |
| CMS-front `CMS_PUBLICATION_MODE` | `exact` |

Preserve the existing per-environment dispatch audience/allowlist. No new static dispatch secret,
service-account key or CDN resource is needed. Persist approved settings in the normal deployment
configuration so the next build cannot silently disable capture or restore legacy frontend mode.

### Old effects queue and rollback conditions

Switching the database to exact can enable the existing in-process `PublicationEffectWorker` even
when the new refresh gates are off and the one-minute schedules are paused. It is not a read-only
test. ERP `/api/internal/page-refresh/dispatch` processes the new refresh queue, not old effects.

With published-section capture enabled, all ordinary exact section publications take the queued
preparation path and reject nonempty old effects. Supported shared types (`global_price`,
`global_achievements`, `global_lead_form`) produce source events. Other types either publish standalone
without effects or reject unsupported consumers; there is no silent fallback to old dependent
effects. Current HTTP page plans, rollback and maintenance also create no old effects. Previously
accepted plans remain immutable; the measured zero plans/effects is a point-in-time observation.

Accordingly, no second recurring runner is needed for newly admitted work in this configuration,
provided all writers agree and the old queue remains empty at cutover. If old work appears, stop and
plan its handling separately; do not drop it or pretend the ERP dispatcher will execute it. The old
one-minute schedules stay paused, not deleted.

For a fault, stop new commands/worker admission and the ERP recurrence as appropriate, preserve
captured events and accepted work, and use a compatible fenced revision. Do not blindly return a
legacy frontend or unfenced backend while the database remains exact. Reversing the database mode
requires its own drained, guarded transition and snapshot/projection reconciliation. Keep additive
schema, immutable snapshots and audit/history records; disabling flags does not undo published data.

### Read-only database inspection receipts

Existing migration jobs were used only as authorized database-access containers, with temporary
per-execution arguments importing `DatabaseModule`. The migration runner, application workers and
DDL/DML were not executed. The SELECT-only inspector followed the Actum SQL diagnostic convention:
one combined final result rather than multiple export grids, with no content bodies or credentials.

| Scope | Successful execution | Completion UTC |
| --- | --- | --- |
| Develop metadata | `cms-back-develop-migrate-zq6h9` | `2026-10-14T05:43:38.666779Z` |
| Release metadata | `cms-back-release-migrate-bg9wv` | `2026-10-14T05:45:38.473616Z` |
| Develop mismatch detail | `cms-back-develop-migrate-8qfvn` | `2026-10-14T05:47:34.429984Z` |

The final local inspector SHA-256 is
`2bcd3a692a84338852cdef3966d5a05c35ebaa013b5b6b5a9e91a9521e6779a3`.
Local syntax and six mocked query-safety checks passed. Post-inspection readback confirmed both saved
jobs still use `node dist/migrations/run-migrations.js`, the expected deployed build images, and no
temporary inspector environment settings. Both old schedules remain paused. No commit, push or
runtime change is part of this readiness follow-up.

## Activation preparation follow-up

This work prepares the operator transition; it is not an activation receipt. New source changes from
another work stream were observed before any further action:

| Environment | Source | Build | Ready backend revision |
| --- | --- | --- | --- |
| develop | `8382c367e4f7da86fb7a0cbdea83909f23323b89` | `333d4fff-47d7-4478-8ca2-6f0e604a8745` | `cms-back-develop-00318-scf` |
| release | `d785ac3417f07a6e384b0fda277fc6d3d5fc0870` | `c005fbc1-7176-4759-a964-4b58836e5729` | `cms-back-release-00107-jpl` |

Both revisions received 100 percent traffic. The intervening develop code change is the practice
competence threshold fix, not a refresh or authentication change. The earlier deployment table remains
the historical receipt for keyless authentication, not the current revision inventory. Refresh gates
and CMS-front publication-mode configuration still remained absent during this follow-up.

### Test case diagnosis and approved disposition

The exact develop page above has public path `/cases/avyavyayvapy`. Its current snapshot was created
on 29 July 2026; the payload has a title but no required `publication_meta.excerpt`. The pure production
extractor returns `EDITORIAL_PROJECTION_REQUIRED_FIELD_MISSING`. There is no current editorial
projection and no immutable editorial snapshot card. All four saved publication-meta versions also
lack a nonempty excerpt. Reconstructing a projection would require invented or newly authored content;
there is no valid existing excerpt to restore automatically.

The inspected payload SHA-256 is
`1e0e2396dc2310cd6c360ab63f4b34a6466b25863b76e3d97829981931678e88`.
Read-only diagnostic executions were `cms-back-develop-migrate-tqrc2` and
`cms-back-develop-migrate-p4dsd`, using the currently observed develop build. They did not run migrations
or alter saved job configuration. Only safe metadata was returned, not page content.

The owner explicitly identified this as a test page and authorized unpublishing this page only in
develop while retaining the page and its history. This paragraph records authorization, not execution;
an execution receipt must be added after the guarded operation and readback. Release content is out
of scope. Do not turn this one-off disposition into a general deletion or automatic content repair.

The guarded SELECT-only precheck `cms-back-develop-migrate-tpt5m` refused pointer-only execution:
one other current published payload refers to the test case. Follow-up read-only execution
`cms-back-develop-migrate-wg7dg` identified the HTML sitemap `/sitemap`, page
`2a27cd9c-0e9b-4e4c-8540-c6f6b305d3f0`, current snapshot
`153355e6-183b-4db8-b627-5ccb18582f4a`. The link is at
`$.sections[1].payload.groups[3].items[0].publicPath`, with the target page ID in the same item.
There are no direct structured-data dependencies, review relations, redirects, editorial projection
or snapshot card for the test case; generic case-collection consumers alone are not blockers.

No DELETE or other data write has run. The target remains published and is still visible through
both the public API and the normal site browser. The case has two historical snapshots, eight saved
snapshot section refs, five bindings, five owned sections and ten owned section versions; all remain
untouched. The local, unpublished one-off helper is limited to removing the pinned current head and
explicitly refuses this sitemap dependency. It is not packaged or a new product API. Its 50 mocked
checks passed. The bounded route scan also matches absolute, fragment and embedded HTML references.

Correct completion now needs approval to remove this exact test-case link from the published sitemap
as well, preserving unrelated saved drafts and the existing history of both pages. Do not silently
republish the whole latest working sitemap or weaken the pointer-only dependency check. No activation
or content change is justified by a successful local test alone.

### Operator helper and ERP boundary

The local backend change adds `scripts/publication-mode-operator.cjs` with SELECT-only default
inspection and an explicit first-transition operation. It uses the existing domain writer fence and
CAS, checks initial metadata under an exclusive NOWAIT lock, and preserves history on any refusal.
The backend image packages the helper but never invokes it automatically. Mocked tests and the
production TypeScript build passed. No writer-mode transition or refresh activation has run.

The available ERP remote branches were checked on 14 October: erpserver develop `a27f032` and main
`e49a1c4`; erp-event-service develop `b4df3cf` and release `da9ce4d`. No page-refresh dispatcher caller
was found there. The existing ERP five-minute schedule contains unrelated mutating jobs and must not
be invoked as a CMS diagnostic. A bounded today's dispatch-log query returned only six earlier
negative-authentication smoke calls (401), not a successful ERP call. This does not prove that an
unshared developer branch lacks the implementation. The owner was asked for the actual implementation
or successful runtime test. Do not substitute operator impersonation or new IAM permissions.

Anonymous HTML probes still reached IAP (302); those headers are not application cache evidence.
The source/topology findings above remain valid, but live HTML cache-header acceptance is still open.

### Approved test-case and sitemap correction — completed 14 October 2026

The owner subsequently confirmed both actions explicitly: unpublish the develop test case and remove
only its link from the current published sitemap. This receipt supersedes the earlier pending-approval
and no-write state above; it does not authorize release changes or refresh activation.

Fresh readback confirmed develop revision `cms-back-develop-00318-scf` at 100 percent traffic, build
`333d4fff-47d7-4478-8ca2-6f0e604a8745`, with publication capture/cache gates absent. The existing
migration job was used solely as an execution container with per-execution Node arguments: no migration
runner, saved job change, new deployment, configuration change or automatic retry. Database identity,
legacy writer generation zero, pinned snapshots/digests and dependency counts were checked before the
write and again under the writer fence, redirect registry and page/head locks.

Read-only joint inspection `cms-back-develop-migrate-9lxcm` succeeded. Execution
`cms-back-develop-migrate-65ppp` committed successfully at `2026-10-14T08:11:26.776716Z`:

- Removed the current-publication pointer for case `253a4361-5ec3-4d47-8982-d17093321d3a`,
  route `/cases/avyavyayvapy`, previously pointing to snapshot `38b0f3fd-a759-4e3a-9908-dd01440d8739`.
- Created sitemap snapshot **3**, `0bf0e313-31ef-417f-912c-c43e26d0b2c7`, from published snapshot
  `153355e6-183b-4db8-b627-5ccb18582f4a`, changing only the one target item in `sitemap_tree`.
  The existing persistence method created fresh snapshot/ref identifiers and activation metadata;
  `sourceSnapshotId` records the old snapshot and `changeReason` is `system_backfill`.
- Preserved every other payload field, including `publishedAt`; preserved both section references
  semantically with fresh reference row IDs. No draft, page status, binding, authored section/version,
  structured-data dependency or stale reason was changed. The old sitemap snapshot digest stayed
  `a2e77db47f7078c240f8dbf26713a95f0eaf2464e8faf33981bc2d8e704fe8f6`.
- Case history counts remained two snapshots, eight snapshot section refs, five bindings, five owned
  sections and ten owned versions. Total current published heads changed from 255 to 254. Both changes
  were one transaction; no unrelated published route was removed.

Post-commit public API verification returned `404 / PUBLIC_PAGE_SNAPSHOT_NOT_FOUND` for the test case,
and sitemap snapshot 3 with neither its page ID nor its route in the payload. The public technical
sitemap route catalog also contained neither identifier. This verifies backend publication state;
it is not a claim that IAP-protected site HTML/cache headers were re-audited in this operation.

Local checks: 50 pointer-inspection/guard tests and 19 joint-operation tests passed. One-off procedure
hashes: base `6607c5709b97db2ca1b3fd59d389abb7217721d8a03e839f7966c86ab19b735a`, joint procedure
`c8c2497b4377a1492ec04e88585cb171555e937b1f27416ef0ccd1d7f9f80d8a`. These are temporary operator
procedures, not packaged product APIs. Unknown commit outcomes require inspection, never blind replay.

Recovery remains possible from the preserved case snapshot and old sitemap snapshot; a restoration
would require fresh approval and checks that neither head has since changed. No push/build was needed
for this scoped data correction. The separately prepared publication-mode helper is still local and
unpublished; queues, writer-mode transition and refresh gates were not enabled.

## Read-only integration and packaged operator rollout — 14 October 2026

The owner approved deploying the operator helper, enabling only refresh reads and finishing readiness
checks. This does not authorize a writer-mode transition, commands/workers/capture or schedules.
Preflight passed again. The earlier test-case correction is a separate data-change receipt above.

| Environment | Source | Successful build | Ready revision, 100% traffic |
| --- | --- | --- | --- |
| develop | `484621c9a14d4fd3cb4a1b25efe53071b29e907b` | `ff555eab-948b-4960-877e-22378032d98f` | `cms-back-develop-00319-8tp` |
| release | `e51bd166492c0a38e55ee19f82f9ec2893ecd6e0` | `2109681e-cc9a-4952-a3fe-6365d8d0dddf` | `cms-back-release-00108-mwz` |

Develop completed at `2026-10-14T08:38:01.787091Z`, release at `2026-10-14T08:44:52.331974Z`, through
the existing exact-branch git triggers. Each branch merged its own current environment head;
pre-existing inter-branch differences were preserved. Focused implementation commits are `6fb203f`
and `8de40f2`. Later working-branch documentation commits do not change these deployed artifacts.

Both API pipelines persist `CMS_PAGE_REFRESH_READ_ENABLED=true`, confirmed as the only enabled refresh
gate. Commands, worker and all capture gates remain absent/off; dispatch audience/allowlist are retained.
Old publication schedules remain `PAUSED`. No migration, mode transition, content write, frontend
deployment, IAM/secret change or cache/CDN configuration change occurred in this rollout.

### Packaged operator and metadata acceptance

The image contains `scripts/publication-mode-operator.cjs`; startup never invokes it. It was executed
without `--execute`, using temporary arguments of the existing migration job, not its migration
command and without changing saved job configuration:

- develop: `cms-back-develop-migrate-hskbt`, completed `2026-10-14T08:41:38.683613Z`;
- release: `cms-back-release-migrate-55khf`, completed `2026-10-14T08:46:18.875893Z`.

Both jobs succeeded and returned `action: none`, `eligible: true`, writer `legacy/0`; zero transitions,
old operations/plans/effects, invalid heads, missing editorial locale groups and editorial projection
mismatches. This closes the develop metadata inconsistency. It is a SELECT-only readiness result,
not proof that ERP, frontend mode and cache acceptance are ready. Bounded error-log queries found
no ERROR-or-higher entries in either new API revision at verification time.

### Tests and live API acceptance

Production/test TypeScript compilation passed in both worktrees. Operator/rollout checks: 45/45 each.
Current-source full suites: develop 3,025 tests (3,021 pass, three sandbox localhost HTTP failures,
one opt-in skip); release 3,007 (3,003 pass, the same three failures, one opt-in skip). The three HTTP
files passed outside the sandbox: 26/26 per worktree without code changes. No stale nested dist suites
were included. Focused read/config/command/worker/bootstrap acceptance passed 54 tests as well.

Health/readiness returned 200 in both environments with exact source/build identity and database `ok`.
Using the real operator's existing release CMS account, queue, summary, journal, settings and dispatch
attention returned 200, `page-refresh-read-v1`, `commandsEnabled=false` and `Cache-Control: no-store,
private`. Queue/journal/attention and pending events were empty, as expected with capture disabled.

The same operator has no develop CMS user: all five protected endpoints return 403
`CMS_USER_NOT_FOUND`. No identity substitution, user creation or permission change was performed.
Develop has live health/config/metadata checks and automated read tests, but a positive authenticated
HTTP read still needs an existing develop CMS user's normal client. Yuri owns its frontend proxy and
screen; backend availability does not claim that this frontend has already been deployed.

### HTML cache evidence remains incomplete

The authorized browser opened the updated develop HTML sitemap. Its available API exposes DOM/assets/
console, not response headers; F12 exposed no DevTools. Independent requests using the existing operator
ID token in the standard authentication headers returned IAP 401 (invalid audience) for both site
environments. Neither is an application cache sample. No cookies were exported, tokens logged, identity
substituted or access settings weakened. The owner's request to self-check was attempted with these
safe alternatives, not replaced by a claim of successful verification.

Previously verified deployed source/topology supports `no_store` / CDN `absent`; live HTML
`Cache-Control`, `Age` and `x-nextjs-cache` remain **unverified**. Admin-API no-store headers are not
site-HTML evidence. No cache mode was enabled on this basis. This limitation does not block read-only
UI integration, but remains part of processing activation acceptance.

Joint activation still needs a real positive ERP call, coordinated existing CMS exact-mode switch,
HTML cache acceptance and the scoped end-to-end refresh scenario. No further migration or backend
feature is needed merely to expose reads. Rollback references: `cms-back-develop-00318-scf` and
`cms-back-release-00107-jpl`; prefer a reviewed pipeline revert/forward fix. No data/schema rollback.
