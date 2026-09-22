# Page redirect summaries: backend rollout — 2026-09-22

## Status and source

Rollout completed. The owner approved committing, pushing and deploying the backend change to
develop and release. GCP preflight passed before cloud work in
`composite-ally-360719/europe-central2`.

Backend source commit: `c085375539cfebb62438c02729d6ddf8fb185f1b`.
Feature branch: `codex/page-redirect-summary` in `re-actum/cms-back`.
Previous common develop/release commit: `eac0ebbabbabee1b536bcdb57cbf8623ca52c852`.

Develop was deployed and verified before the same source SHA was fast-forwarded to release.
Both deployments succeeded through existing repository push triggers; no manual Cloud Run deployment
was performed. Remote feature/develop/release branches all point to the source commit, and the backend
worktree is clean.

| Environment | Build | Ready revision / traffic | Previous ready revision |
| --- | --- | --- | --- |
| develop | `1d94f6c1-0cfc-4d84-878d-f103af80b948` — SUCCESS | `cms-back-develop-00297-zr9` — Ready, 100% | `cms-back-develop-00296-q5c` |
| release | `cd29aa38-f7af-4365-8ae9-3e85668cc03b` — SUCCESS | `cms-back-release-00086-jbs` — Ready, 100% | `cms-back-release-00085-4sl` |

Develop build completed at `2026-09-22T13:36:45.136102Z`.
Release build completed at `2026-09-22T13:41:25.495630Z`.

## Behavior

Persisted page cards receive an additive `redirects` summary: `active`, `pending`, and counts for
related, working 301, prepared, disabled, unavailable and 410 rules. It is page-specific, including
the page's locale and regional variant. A generated row without a persisted page returns `null`,
not the all-zero summary used by an existing page without rules.

Prepared changes await explicit activation; they are not a background job. Active and pending can
coexist. If a working rule points to A and a prepared edit proposes B, A remains active+pending,
while B is pending-only. Disabled rules are not diagnostic errors. Counts do not form an exclusive
partition because prepared settings can coexist with a current active/disabled/unavailable rule.

The backend enriches workbench matrix/row responses, nested intent workbenches, and editorial
publication list/detail/create responses in batches using existing indexed registry associations.
Navigation-only/internal diagnostics reads skip unnecessary enrichment. No whole-registry or
per-card registry fetch is introduced. Detailed registry access and mutations still require
`redirects.manage`; embedded summaries expose counts only.

## Verification

- Before push: production build passed; 1,069 tests passed across 122 suites, with zero failures/skips.
- After push: all 1,069 tests in 122 suites passed again, with zero failures/skips.
- Typecheck passed after the release push.
- Both environments' `/api/health` returned `ok`; `/api/ready` returned `ready` with database `ok`.
  Both verified the exact source commit and each environment's build ID. Ready revisions each
  receive 100% of traffic.
- Both environments' Swagger exposes all eight summary fields.
- Develop admin-functional smoke returned 403 for the actual operator identity. No identity or
  role was changed; a successful live develop admin response is not claimed.
- Release admin-functional smoke returned 200 using the actual operator identity:
  - contacts matrix: one uncreated row with `redirects: null`;
  - editorial blog list: no items, absent collection page with `redirects: null`;
  - persisted UK catalog: four pages; three row-refresh responses were checked (`sitemap_page`,
    `lawyers_page`, `lawyer_page`), each with all eight summary fields and zero counts/false flags;
  - lawyer matrix: 23 rows, comprising one persisted page with a zero summary and 22 uncreated
    rows with `redirects: null`.
- Release redirect registry contained zero records. Positive active/pending and mixed-state
  behavior is covered by automated tests, not claimed as observed in live release data. No test
  rules or page fixtures were created.
- After smoke, bounded 15-minute ERROR queries for both new revisions returned no entries.
  This is a point-in-time check, not ongoing monitoring.

No frontend, schema migration, content rebuild, redirect activation or live data edits are requested
or performed as part of this feature rollout. IAM, environment/secret settings, domains, triggers
and pipeline definitions are unchanged. Existing pipeline steps update the migration-job image;
that is not a migration execution.

## Remaining CMS-front work

Yuriy must consume the summary to render the redirect button and explanatory tooltip. The UI must
allow active+pending, distinguish disabled from unavailable and respect `null` for uncreated pages.
After a redirect mutation it should reload the affected page row/list, including both targets for
a pending retarget. No page content republication is needed to refresh these registry-derived counts.

Acceptance checks after frontend integration: no rules; prepare/activate; active A + pending B;
manual disable; unpublished target; ready 410; independent locale/region. Workbench and editorial
surfaces should agree for the same page ID.

## Rollback

Preferred rollback is a reviewed `git revert c085375539cfebb62438c02729d6ddf8fb185f1b`, followed by
the existing develop verification and release-promotion pipelines. No database/content restoration
is needed. Emergency traffic rollback requires explicit approval and can use the previous known-good
revisions recorded above. Previous successful builds were
`c52e3d03-b4dd-439a-be0a-74f510d5dfce` (develop) and
`7d60119e-3258-4b56-945d-4950dda3e922` (release).

Backend contract: `cms-back/docs/page-redirect-summary-contract-2026-09-22.md`.
Cloud record: `gcp-infra-playbook/docs/projects/cms-page-redirect-summary-rollout-2026-09-22.md`.
