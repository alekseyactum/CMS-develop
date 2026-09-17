# Optional problem pages: backend rollout — 2026-09-17

The owner approved commit/push/deployment and then explicitly clarified that the scope is CMS backend
only. No database migration or content republishing is part of this rollout.

## Source and verification

- Backend `re-actum/cms-back`: `fa589816ced48ba5208722da936685d4aaa2b730`.
- `develop` and `release` were fast-forwarded atomically from `59001f38e1454cf90c6df8b6fcf34bcfe9ce55f3`.
- Feature branch: `codex/problem-optional-pages`.
- Requirements: CMS commit `2b9a7ec`, branch `codex/tz-2-to-tz-3-handoff`.
- Post-push backend verification: 942 tests passed, zero failures; TypeScript production build passed.
- Required GCP preflight passed. Existing regional Cloud Build triggers are used unchanged.
- No IAM, DNS, secrets, pipeline, schema or stored page content changes were requested or made.

Backend diagnostics no longer require a slug or an individual page for a visible problem. Creating a
problem page still requires a valid source hierarchy and complete slugs. Public reads expose problem
links only for the matching published page, locale and region; otherwise paths are null.

## Deployment evidence

Project `composite-ally-360719`, region `europe-central2`.

| Environment | Successful build | Ready revision, 100% traffic | Previous ready revision |
| --- | --- | --- | --- |
| develop | `8c7c0339-c9e1-45bb-91e5-46a5560688d6` | `cms-back-develop-00288-8z5` | `cms-back-develop-00287-64t` |
| release | `844ca254-e7ab-42d2-90bc-c124401a8811` | `cms-back-release-00077-wh5` | `cms-back-release-00076-l8p` |

Both builds completed successfully. Authenticated health/ready returned HTTP 200 with the expected
`fa58981` SHA and database status `ok` in both environments. The existing pipelines refreshed migration
job images as usual but no migration job was executed.

Bounded ERROR-log checks for both new revisions returned zero entries after smoke. Remote develop and
release refs were rechecked and both point to the expected full backend SHA.

Release read-only `GET /api/admin/reference/meta` confirms that `problems.requiredSourceFields` is
empty while practices/services still require `sourceSlug`. Develop's same admin check returned the
existing operator CMS authorization 403; no role or identity was changed to bypass it. Admin reference
detail/list GETs were intentionally not used: they can create missing translation skeletons.

Public sitemap reads returned 200 in both environments. Develop public page reads returned 200,
including a regional service with four problem IDs and four published links, exercising the new shared
database lookup. A repeated read retained the same snapshot ID/number. Release had no eligible published
service/collection candidates in the sitemap, so this specific runtime SQL smoke was only exercised on
develop. The null-link and publication-transition cases are covered by automated tests, not by mutating
live content for acceptance.

## Frontend scope correction

The assistant mistakenly included site-front before the owner's clarification. Site-front commit
`9809b9a` and history-only merge `8844112b2e72dc3bc7b9d14e32a1336fa97f4101` were already pushed to
`develop`/`release` and `codex/problem-optional-page-links`. No force push was used and existing work was
preserved. The merge reconciled the previous release merge with develop's existing lead-form changes.

Both automatically started site builds were cancelled before deployment:

- Develop: `dc3f1713-fa1d-42a6-8a3b-80efe3abc794` — CANCELLED.
- Release: `8b29ff7c-d676-418b-a972-e2829e034e6a` — CANCELLED.

Site runtime remained on `site-front-develop-00091-t8z` and `site-front-release-00012-z45`, each with
100% traffic. The pushed source changes remain in the remote branches; no unapproved revert or further
site deployment was performed. A future site build from those branches will include them unless they
are separately reverted. This requires an explicit follow-up decision, not an assumed frontend rollout.

The frontend contract still needs acceptance by its owner: null problem `publicPath` means plain text,
not a generated path, `href` fallback or `#`. Old collection snapshots that omitted slugless problems
need a normal future republish to add membership; live link projection does not republish drafts.

## Rollback

Normal rollback is a reviewed backend revert through the existing pipelines. Emergency traffic rollback
requires separate authorization and can use the prior revisions above. No database rollback is needed.
