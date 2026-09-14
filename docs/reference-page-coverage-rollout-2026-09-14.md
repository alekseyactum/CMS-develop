# Reference page coverage details: backend rollout, 2026-09-14

## Scope and authorization

Owner explicitly approved promoting the prepared backend commit to develop and release with automatic
deployment. Canonical service repository: `https://github.com/re-actum/cms-back.git`.
Playbook preflight passed for the expected account/project before cloud reads.

- Previous commit on both branches: `db0d3a4ce68a4f35aa925e2faa88f11c433c01f4`.
- Deployed commit on both branches: `b684c2594b32c6fda2bb37408c0ed67b38fe8478`.
- Both pushes were fast-forward; no conflicts, force push or extra merges.
- Feature branch `codex/page-coverage-details` points to the same commit.
- No schema migration, content writes, ERP updates, IAM changes or pipeline edits were performed.
- Existing pipeline updates the migration job image; no migration execution was requested or run.

The change adds opt-in read-only `pageCoverage.details` to practice/region detail cards. It reuses existing
coverage calculations, adds paginated named items and keeps ordinary lists and prior counters unchanged.
Contract: `cms-back/docs/reference-page-coverage-details-2026-09-13.md` at the deployed commit.
CMS frontend rendering remains Yuri's task; this rollout does not add the UI block.

## Deployment evidence

Project `composite-ally-360719`, region `europe-central2`.

| Environment | Build (SUCCESS) | Previous revision | New revision (100% traffic) |
|---|---|---|---|
| develop | `b4f878b0-10c0-486b-9408-de0e1eff0499` | `cms-back-develop-00280-csp` | `cms-back-develop-00281-bl7` |
| release | `7c7b77a0-cf0e-4808-b34f-0c7338674491` | `cms-back-release-00069-7nl` | `cms-back-release-00070-smj` |

Develop build completed at `2026-09-14T03:14:44Z`; release at `2026-09-14T03:19:02Z`.
Both service configurations and authenticated `/api/health` responses identify the expected commit.
Both `/api/health` and `/api/ready` returned 200, with database status `ok`.
No severity ERROR or higher entries were returned for the two new revisions during the post-deploy check.
This is a bounded deployment check, not a long-term availability/performance claim.

## Verification

- Application build and full test suite rerun after each environment push: 827 passed, zero failures/skips.
- Backend worktree clean; `git diff --check` passed.
- Remote develop/release/feature refs verified equal to the deployed commit.
- Develop reference API returned 403 `CMS_USER_NOT_FOUND` for the operator's own identity. No user was
  impersonated, created or granted access. Functional develop admin/UI acceptance remains pending.
- Release accepted the same operator identity. Read-only live practice and region checks succeeded:
  old `own`, `descendants`, `actionScope` values were deeply equal with and without details.
- Practice sample: 9 descendants, limit 2, 2 items, `hasMore=true`.
- Region sample: 10 descendants, limit 2, 2 items, `hasMore=true`; offset 2 returned the next two distinct
  keys with unchanged total. No page creation was performed.
- Invalid detail limit 101 returned 400.

Live samples exercise missing-page states; richer status combinations are covered by local tests, not
claimed as verified against every live record.

## Manual acceptance / frontend handoff

Under an existing authorized CMS editor/admin, open a practice or region detail card and request
`includePageCoverageDetails=true&pageCoverageLocale=uk&pageCoverageDetailsLimit=50&pageCoverageDetailsOffset=0`.
Render own page separately, then full group counters and paginated descendant items. Preserve backend
paths, status/reasons, locale and independent `hasPublishedSnapshot`; do not reconstruct routes or infer
that every missing page is creatable. Fetch the flag only for selected cards, not reference lists.
Verify develop under a registered CMS identity and complete frontend rendering/acceptance separately.

## Risk and rollback

Opt-in details add work to the selected detail request; pagination bounds response/name lookups, not the
existing full coverage aggregation. Monitor card latency for large hierarchies.
Normal rollback is a reviewed revert of `b684c25`, promoted through the existing build pipelines. No DB
rollback is needed. Previous revisions above are emergency traffic rollback points, only with explicit
owner authorization and a follow-up source fix.
