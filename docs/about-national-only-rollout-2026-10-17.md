# About National-Only Rollout

Date: 2026-10-17. The owner explicitly approved backend implementation, push and deployment to
develop and release. The authoritative product scope is national-only About in `uk`, `ru`, `en`.

## Source And Scope

- Specification: `4bcfc8c9`, umbrella branch `codex/tz-2-to-tz-3-handoff`.
- Backend develop: `201901314b07fceb5b874da7c15ad921c60e16df`, branch `codex/about-national-only`.
- Backend release: `14de6cb0763e710b5e8ec87d496d8937a535617a`, branch `codex/about-national-only-release`.
- Both backend commits were pushed to their respective deploy branches. Release received a focused
  cherry-pick, not all develop changes. The sole conflict was lifecycle test placement; existing
  develop-only JSON-LD inspection tests were not imported into release.

Only `/about`, `/ru/about`, `/en/about` are supported. Regional creation, preview, publication and
runtime contexts are rejected. Matrix, navigation summary, tree counts, locale alternatives and
the current sitemap catalog exclude historical regional About identities. Own content is editable
without regional inheritance/locks. Offices and lawyers are selected across Ukraine using the
existing eligibility rules. The ordinary inherited `global_lead_form` and runtime collection
dependencies remain intact. No CMS-front or site-front code was changed or deployed.

## Data Safety

Read-only release inspection found one national UK draft (`e3338050-745a-4162-a46b-af4d15729094`),
no regional About pages, and missing RU/EN locale placeholders. It has ten bindings and eight drafts.
The pre-deploy hash of selected binding/ownership/composition/version data is
`06B94A56745DBC950BBAD9F6C0E201B8CCE3EC36205CE98A9AD032D602DF5DE4`.

Develop inspection used execution-only `node -e` overrides on the existing migrate job, with
`START TRANSACTION READ ONLY` and `ROLLBACK`: `cms-back-develop-migrate-hsl9q` and
`cms-back-develop-migrate-jddkk`. No migration code was executed and saved job arguments were not
changed. It found national page `661b8409-7ac3-4c57-805e-3bd5a2473b8e` and historical regional page
`6143651b-4ffb-47fb-93ae-5eebe2de5014` (`/donetsk/about`). The regional page has ten owned versions
and a current published snapshot, despite its page-row status being `draft`.

Historical regional database records and snapshots were not deleted. The regional route now returns
404. National develop snapshot `c23f9700-6c39-4d8d-b1c3-550d7086ce74` still returns 200 with unchanged
payload hash `ECA56EDF87BF1A027509B7502B5BD21B5C6280937C79C398DD7C9243A59DF453`.

Refresh scheduler/command semantics were not changed. Develop workers and commands remain disabled;
release has no regional About records. Review retained regional refresh history before any future
develop worker activation. No schema migration, content publication, rebuild, IAM change, secret
rotation, domain/indexing change or frontend deployment was performed.

## Verification

- Develop full suite: 3344 passed, one optional test skipped, zero failures.
- Release full suite: 3326 passed, one optional test skipped, zero failures.
- Whitespace checks and production builds after each backend push passed.
- Independent review found a remaining regional count in the workbench tree; it was fixed and
  covered by matrix/navigation/tree regression tests before deployment.
- Develop health/readiness returned the expected source/build; database `ok`, national snapshot
  unchanged, historical regional URL 404. Actual operator admin access remains 403
  `CMS_USER_NOT_FOUND`; no other user was impersonated or access changed.
- Release health/readiness returned the expected source/build and database `ok`. Live schema has
  `supportsRegionalRoutes: false`, all three locales, sixteen slots and inherited `global_lead_form`.
  UK/RU/EN matrices each return one national row; RU/EN remain uncreated placeholders. The UK draft's
  binding/version hash matches its pre-deploy value exactly. History/founder editor `canSavePageDraft`
  is true; the inherited form's is false. These reads did not save or publish content.
- Browser acceptance of CMS/site and end-to-end form submission are not claimed by these checks.

## Deployment

Project `composite-ally-360719`, region `europe-central2`. Playbook preflight passed. Existing triggers
retain exact `^develop$` / `^release$` filters; deployments use the existing Git-triggered pipelines.

| Environment | Build | Revision | Status |
| --- | --- | --- | --- |
| develop | `57c99b50-9299-4aea-87eb-bbe9cd0f55ba` | `cms-back-develop-00334-7pv` | Successful, 100% traffic |
| release | `7a038602-82ae-4e4e-a11b-9ddef87a6e28` | `cms-back-release-00124-d54` | Successful, 100% traffic |

Builds finished at 09:26:52 UTC and 09:31:16 UTC respectively. API/migration/publication-effects job
images match within both environments. Saved job commands remain unchanged. Develop refresh
worker/command gates are both `false`; release gates are both `true`, as before this rollout.
Bounded checks of both new revisions returned no ERROR-or-higher log entries.

## Rollback Points

- Develop previous source `6a6b7b9`, revision `cms-back-develop-00333-msv`, build
  `38a09aff-ea9e-4a4a-8888-38c27b55bcc5`.
- Release previous source `a628df6`, revision `cms-back-release-00123-8gc`, build
  `a1ac489a-7ca1-447d-a87b-d3265382010b`.

Prefer an approved focused Git revert through normal deployment. No schema rollback is needed.
Rolling back application code would re-enable the retained develop regional page; evaluate that
explicitly before rollback. Preserve all content and do not alter environment-specific refresh gates.
