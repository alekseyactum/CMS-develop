# License hero accent title rollout — 2026-09-30

## Scope and source

Owner explicitly approved CMS-back deployment to develop and release through the
existing git-triggered pipelines. No frontend, content, page publication/rebuild,
migration execution, IAM, secret/environment, redirect or pipeline changes.

- Repository: `re-actum/cms-back`.
- Source commit: `8d2d9ffa628bfbd6ab23ba643014097eca6e3dfd`.
- Feature branch: `codex/license-hero-accent-title`.
- Previous common develop/release commit: `fdf2ba43ea104d4120596d89062ddb9f65de66a5`.

`license_hero` now exposes optional plain-text `accentTitle`, max 200 characters,
through the schema, editor, preview and published payload. Missing/empty values do
not block publication. A supplied value must be a string, not null or HTML. The
required `title` is unchanged. New drafts start with an empty accent; old drafts and
snapshots do not require migration or automatic text rewriting.

Frontend renders `title` followed by `accentTitle` within one H1; the accent's pink
style belongs to frontend. The accent is a separate text part, not a substring query.
Example: title `Розвивайте адвокатську практику разом з`, accentTitle `ACTUM`.

## Verification

Before commit and again after push on the exact source SHA:

- Typecheck and production build passed.
- Full test suite: 1,128 tests / 124 suites passed, zero failures/skips.
- `git diff --check` passed; backend worktree clean.

Five added regressions plus extended schema/lifecycle tests cover optional/legacy
values, limits/type/plain-text diagnostics, save/editor round-trip, preview/publication
and persisted snapshots. Sandbox initially prevented rewriting existing build artifacts;
the permitted local retry passed without source or environment changes.

## Deployment evidence

Develop build `e05e3c69-255d-4caf-8f2a-6bc43c4f87fe` succeeded at
`2026-09-30T09:16:33.982600Z`. Revision `cms-back-develop-00300-d7s` is Ready at 100%
traffic. Health/readiness returned 200, database ok, exact expected commit/build IDs.
The actual operator's schema read returned 403 `CMS_USER_NOT_FOUND`; no identity or
role changes were made. After these checks, release received the same source SHA.

Release build `26acd943-4368-4d29-a056-d042bb781406` succeeded at
`2026-09-30T09:20:30.956933Z`. Revision `cms-back-release-00089-5x6` is Ready at 100%
traffic. Health/readiness returned 200, database ok, expected commit/build IDs.

Release GET `/api/admin/page-schemas/lawyer_license_page` returned 200 and confirmed
`license_hero.accentTitle` as optional/plain_text, with `title` still required and
locales `[uk]`. Only read-only endpoints were used; no editor/bootstrap or content
writes were performed. Actual preview/publish round-trip is covered by local tests.

Bounded 15-minute severity >= ERROR log queries for both new revisions returned no
entries. This is a point-in-time check, not continuous monitoring. Existing pipelines
updated migration-job image/config but did not execute migration jobs.

## Rollback and handoff

Previous ready revisions:

- develop: `cms-back-develop-00299-j5j`.
- release: `cms-back-release-00088-8xp`.

Normal rollback: reviewed git revert through existing pipelines. Emergency traffic
rollback requires explicit approval. No database/content restoration is necessary.

Yuriy adds the CMS field and website presentation. After frontend integration, save
the title prefix and accent separately, check preview and publish through the normal
page workflow. Do not leave ACTUM in both fields. Existing pages without an accent
must retain their current heading. No production test content was created for smoke.

Backend contract: `docs/license-page-backend-contract-2026-09-27.md`, addition dated
2026-09-30. Deployment does not itself fill or republish content.
