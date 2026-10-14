# Lawyer Profile Practice Threshold Rollout

Date: 2026-10-14. Status: deployed to develop and release.

## Scope

The owner approved changing the lawyer profile's `practices[]` list to `score >= 3`, then explicitly
approved push and deployment to both environments. Active/resolved qualification requirements,
practice visibility, deduplication and sorting are unchanged. The directory filter and lawyer selection
on practice/service pages retain their existing thresholds. No frontend change or migration is required.

The product rule is recorded in [the lawyer page contract](lawyer-page-structure-2026-06-18.md).
Its update was pushed to `codex/tz-2-to-tz-3-handoff` in `87e7f4f`.

## Source And Deployment

GCP playbook preflight passed before cloud access. Project: `composite-ally-360719`; region:
`europe-central2`; backend repository: `re-actum/cms-back`.

The work was merged with the latest remote environment branches before promotion, preserving the
already deployed stale-refresh and keyless dispatch changes. The net diff against each previous
environment head is only the resolver predicate, focused tests and backend documentation. Existing
Cloud Build configurations and exact `^develop$` / `^release$` triggers were not changed.

| Environment | Source commit | Successful Cloud Build | Ready revision, 100% traffic |
| --- | --- | --- | --- |
| develop | `8382c367e4f7da86fb7a0cbdea83909f23323b89` | `333d4fff-47d7-4478-8ca2-6f0e604a8745` | `cms-back-develop-00318-scf` |
| release | `d785ac3417f07a6e384b0fda277fc6d3d5fc0870` | `c005fbc1-7176-4759-a964-4b58836e5729` | `cms-back-release-00107-jpl` |

Build completion: develop `2026-10-14T05:55:56.601657Z`; release `2026-10-14T06:00:21.329835Z`.
Both environment branches and their respective `codex/lawyer-profile-practice-threshold` and
`codex/lawyer-profile-practice-threshold-release` working branches point to the recorded SHAs.

## Verification

- Production and test TypeScript compilation passed in both updated checkouts.
- After working-branch push, 109 focused tests passed per environment: runtime resolver, closed profile
  refresh publication, and cold application bootstrap. There were no failures or skips.
- After each environment-branch push, the 102 runtime resolver tests passed again. Tests cover the new
  profile query in `uk`, `ru`, `en`, the inclusive boundary of 3, an empty result without a lower-score
  fallback, and the unchanged directory threshold. The full repository suite was not rerun for this
  focused predicate change.
- Authenticated `/api/health` and `/api/ready` returned 200 in both environments, with exact build/source
  identities and database status `ok`.
- Release read-only lawyer matrices returned successfully for all three locales. A fresh runtime
  inspection of the Ukrainian profile supplied in the request returned four practices with scores
  `[4, 3, 3, 3]`. That sample has no created RU/EN pages, so those locale profile checks remain covered
  by local tests, not live sample inspection.
- Develop admin matrix returned 403 `CMS_USER_NOT_FOUND` for the actual operator. No identity
  substitution or permission change was made; live develop functional acceptance remains limited.
- Bounded ERROR-or-higher queries for both new revisions returned no entries at verification time.
  This is a point-in-time check, not a load test; logging ingestion may be delayed.
- Both migration jobs and both publication-effects jobs use their environment's new image. Saved
  Node commands are unchanged, as are latest execution IDs. Neither kind of job was executed by this
  rollout. Both one-minute publication-effects schedules remain `PAUSED`.

## Content Boundary And Manual Check

No database/content writes, page publications, snapshot rebuilds, schema migrations, frontend deploys,
IAM/secret edits, scheduler activation or manual service/traffic changes were performed.

Deployment changes fresh profile assembly, not previously saved public snapshots. Existing pages need
an explicit rebuild and republication to replace their saved practice list. This code change does not
automatically mark those pages stale. A narrow biography-only refresh intentionally preserves captured
practices and is not a substitute for rebuilding the profile list.

To verify, inspect the current `lawyer_profile` runtime or assemble a fresh preview: score 2 must not
appear, score 3 must remain eligible, and ordering must stay descending by score. After an approved
page rebuild/publication, verify the public page against that refreshed payload.

## Rollback

| Environment | Previous source | Previous ready revision | Previous build |
| --- | --- | --- | --- |
| develop | `515ce16e49d049b2ceb8083050e7f9da822d8a3f` | `cms-back-develop-00317-4fx` | `45aa8ffe-a131-429d-a487-3e4f0d0c3f47` |
| release | `89397ee5d65b5698847818e2cef25bc92e5955d9` | `cms-back-release-00106-fcv` | `210f5582-2c53-4362-8feb-f93a140f2b87` |

Prefer an approved focused revert of `010eb1b` (develop) / `2bcc1d2` (release) through the existing
pipelines, preserving the merged upstream changes. Emergency traffic rollback requires separate
approval. No data/schema rollback is needed. Any later republished content has its own snapshot
lifecycle and is not undone merely by reverting the code.
