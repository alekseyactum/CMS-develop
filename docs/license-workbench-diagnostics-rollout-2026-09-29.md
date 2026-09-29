# License workbench diagnostics rollout — 2026-09-29

## Scope and source

Owner approved CMS-back develop and release rollout through the existing push-triggered
pipelines. No frontend, content, page publication/rebuild, migration execution, redirect,
IAM, environment, secret or pipeline changes are included.

- Repository: `re-actum/cms-back`.
- Source commit: `fdf2ba43ea104d4120596d89062ddb9f65de66a5`.
- Feature branch: `codex/license-workbench-diagnostics`.
- Previous develop/release commit: `020a86c448897d6f5f21ad4bb93c322447a7f009`.

The matrix now uses the same exact-draft validation resolver as the section editor.
When stored validation is absent, computed content errors are no longer interpreted as
zero errors. Existing aggregation blocks publication and reports the affected sections;
License navigation uses the same row diagnostics. Draft saving and preview are unchanged.

Implementation details and manual regression steps are in cms-back
`docs/license-workbench-diagnostics-fix-2026-09-29.md`.

## Verification

Before commit and again after push on the exact source commit:

- `npm run typecheck`: passed.
- `npm run build`: passed.
- `npm test`: 1,123 tests / 124 suites passed; zero failures/skips.
- `git diff --check`: passed; backend worktree clean.

Ten new regressions cover nested License errors, editor/matrix parity, row refresh,
navigation, bulk publication readiness, corrected drafts, persisted-result precedence,
missing drafts, generic section fallback and read-only behavior.

## Rollout evidence

Develop was pushed first. Initial build `e62ba305-edd0-4716-bc6d-b6ecf2cf47a5`
failed during FETCHSOURCE with `FETCH_SOURCE_FAILED` and GitHub `Repository not found`.
No build/deploy steps ran. The connection reported installation stage COMPLETE; local
git could access the repository. No permission/configuration change was attempted.

One retry of the existing develop trigger at the same SHA, build
`04ea176a-a2a3-4a94-b4f2-edf6a6da5a60`, succeeded without configuration changes.
The initial fetch failure did not recur; its underlying cause was not established.

After develop verification, the same SHA was fast-forward pushed to release and its
existing trigger completed successfully.

| Environment | Successful build | Ready revision / traffic | Build finished (UTC) |
| --- | --- | --- | --- |
| develop | `04ea176a-a2a3-4a94-b4f2-edf6a6da5a60` | `cms-back-develop-00299-j5j` / 100% | 2026-09-29 08:21:39 |
| release | `35288fcc-beaa-4c78-be31-0db418ef96b9` | `cms-back-release-00088-8xp` / 100% | 2026-09-29 08:25:50 |

Both environments returned HTTP 200 from `/api/health` and `/api/ready`, with database
status ok and the expected source SHA/build ID. Severity >= ERROR checks for each new
revision over a bounded 15-minute window returned no entries; this is a point-in-time check.

Develop License matrix access returned 403 `CMS_USER_NOT_FOUND` for the actual operator;
no role or identity change was made. Release matrix returned 200, but the License page
has not been created there: one placeholder row, eight empty slots, `PAGE_NOT_CREATED`,
`canPublish: false`. This matches the pre-deployment baseline. No test content was created.
The specific incomplete-card scenario is verified by automated regression tests, not
claimed as a live release-content test.

The existing pipelines updated migration-job image/config but did not execute migrations.

## Baseline and rollback

- Previous develop ready revision: `cms-back-develop-00298-8d5`.
- Previous release ready revision: `cms-back-release-00087-znd`.

Use a reviewed git revert through the existing pipelines for a normal rollback.
Emergency traffic rollback requires explicit approval. No data restoration is needed.

## Manual acceptance

On an existing License draft, leave a nested support-card field incomplete, save, then
refresh the matrix without running explicit validation. The cell must report errors
and publication must be unavailable. Complete the field, save a new draft and refresh:
those errors must clear, subject to any other publication blockers. Draft saving and
preview remain available. Do not create production test content merely for deployment smoke.
