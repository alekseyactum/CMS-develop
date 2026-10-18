# Case organization authorship — 2026-10-16

Later contract amendment (18 October 2026): Case metadata also accepts an optional legal reviewer,
independent of authorship. This is a later implementation change, not part of the original rollout
record below. See the current editorial specification's Case contributors section and the separate
18 October rollout record at the end of this document.

The owner explicitly requested implementation and immediate push to develop and release.
Scope: allow Actum Organization to author a Case when no lawyer authors are selected.
Article import, page publication and content changes are separate operations.

## Resulting contract

- Creation, section saves, preview, publication and translation permit empty lawyer selections.
  Omit `primaryLawyerAuthorRef` or send an empty string and use `coAuthorLawyerRefs: []`.
  An explicit `null` is not the authored `plain_text` field contract.
- Public detail metadata resolves `authors` to
  `[{ id: "actum", fullName: "Актум", roleLabel: null, publicPath: "/", photoUrl: null }]`.
  `primaryLawyer` remains `null`; no synthetic lawyer is stored.
- Coauthors require an explicit primary lawyer. Creation, save/publication validation,
  translation and presentation reject an inconsistent selection without promoting a coauthor.
- An explicitly selected unavailable lawyer is not replaced by Actum. Existing preview omission
  and structured-data diagnostics remain unchanged. No extra publication block is claimed when
  the relevant JSON-LD type is disabled in the environment.
- The shared Organization identity is used as JSON-LD author, with no fictional Person.
  Reviewer and external-reference Media semantics are unchanged. No reviewer field is added to Case.
- Exact publication captures retain the resolved organization without live rereads on restore/commit.
  Case projection/card lawyer fields remain nullable, with no fake lawyer contribution; topic case
  listings continue to work. Existing published snapshots are not automatically rewritten.

## Source and validation

Repository: `re-actum/cms-back`.

| Environment | Commit | Full suite | Cloud Build | Ready revision |
| --- | --- | --- | --- | --- |
| develop | `1edc90b89a09f7ef312d5a748e6c7d64f559b3d0` | 3225 pass, 1 optional MySQL skip | `5aa8a445-28a5-4625-9d8c-22f1b1c66237` | `cms-back-develop-00328-rgp` |
| release | `0a52b7148d6c10819754c621a710aff79fec1f22` | 3207 pass, 1 optional MySQL skip | `4be6720f-7434-4eeb-a8bf-4259db4c39eb` | `cms-back-release-00118-hsn` |

Both production builds passed. The release cherry-pick has the same stable patch ID as develop,
`b629e8d74c50eb6c166e82f6eb514929e34b7fba`, preserving release-specific deployment configuration.
Independent review found no blocking defects. Tests cover creation, translation, publication
validation, real preview/legacy publication, exact capture/export/restore, invalid captures,
JSON-LD, nullable projections and immutable cards. Post-push focused verification passed 185 tests
on each environment's exact source commit.

## Deployment verification

Mandatory GCP preflight passed for `composite-ally-360719`; region `europe-central2`.
Both existing branch-triggered builds succeeded: develop at `2026-10-16T05:56:15Z`, release at
`2026-10-16T06:00:24Z`. Both ready revisions receive 100% traffic. Health/readiness returned 200,
the expected commit/build metadata and database status `ok`.
Bounded ERROR-or-higher log reads for both new revisions returned zero entries during verification;
this is a point-in-time smoke check, not a load test.

Release `GET /api/admin/page-schemas/case_page` confirms `primaryLawyerAuthorRef` is optional.
Develop admin schema reads still return the existing `CMS_USER_NOT_FOUND` for the actual operator;
no identity substitution or access changes were made. Its schema is covered by the local tests.

Release refresh worker/commands remain enabled, develop remains disabled. Both retain origin
`no_store` and CDN `absent`. JSON-LD allowlists remain unchanged: develop includes Home and the
existing practice/service/problem types; release includes Home only. The new author rule itself
does not depend on enabling Case JSON-LD.

No migration, scheduler execution, content write, IAM or secret change is part of this rollout.
Frontend rendering and a live editor save/publication are not asserted by the backend checks.

## Rollback

Pre-change source and revisions:

- develop: `27cb4066813bcab72ed219aba978ba333430682c`, `cms-back-develop-00327-g6q`;
- release: `0444045c0aef8195382d65721f3708542fe1e48d`, `cms-back-release-00117-f4g`.

Prefer a focused forward fix once company-authored cases or prepared plans exist. Older binaries
require a primary Case lawyer and reject this new selection/capture. A separately approved rollback
must account for those drafts/plans; never invent authors or delete imported data to make it pass.
Before adoption, a reviewed git revert through the normal pipeline restores the prior behavior.
No table rollback or secret rotation is required.

## Optional Case reviewer rollout — 18 October 2026

The owner explicitly approved backend commit, push and deployment to develop and release. The
optional `publication_meta.legalReviewerLawyerRef` is independent of primary/coauthors, accepts an
explicit CMS lawyer ID on creation/metadata Save and is copied as a structural reference to
translations. Empty selection remains valid; authors/editors are not assigned automatically.
The shared preview/publication capture, public `legalReviewer`, projection and conditional JSON-LD
reviewer contract are reused. CMS-back owns storage; the ERP reference migrator does not make this
editorial choice. The article importer's default-reviewer rule is not extended to Cases.

| Environment | Source commit | Successful Cloud Build | Ready revision, 100% traffic |
| --- | --- | --- | --- |
| develop | `0c43133c2fb89752bf4af2db39ebe3e69f984256` | `36297b8f-ac92-4df8-bb83-5cdf8470bcb8` | `cms-back-develop-00340-vsj` |
| release | `7115255d5efaac902476fd3a9f0a3cba26bfdcd1` | `7b783613-e174-4596-a1ed-741c92af3bd9` | `cms-back-release-00130-lw7` |

Mandatory GCP preflight passed. Exact-branch triggers were unchanged; release is patch-equivalent
to develop (`bd7a48e33e75f5f200d4ccd2789dfa6461fc25f5`) and retains its configuration differences.
Builds, test compilation and three module imports passed. Full tests: develop 3,684 passed, release
3,667 passed, zero failures and one existing opt-in MySQL skip each. Post-push focused checks passed
455/455 and 448/448 respectively. Both health/readiness checks returned 200 with exact source/build
and database `ok`; both job images match their service; bounded ERROR queries returned zero entries.
Release Case schema returned 200 with optional `plain_text` reviewer. Develop admin schema remains
unavailable to the actual operator (`CMS_USER_NOT_FOUND`); no impersonation/access change was used.

No database migration, backfill, import, reviewer assignment or editorial Save/Publish was performed.
No frontend, IAM, secret, flag or scheduler change was made. Refresh worker/commands remain false in
develop and true in release; cache modes and JSON-LD allowlists remain unchanged. CMS Front must
show its existing lawyer picker for Case metadata/creation, allow clearing it and submit only the
reference. Browser Save/Preview/Publish acceptance is not claimed by these backend checks.

Pre-change revisions were `cms-back-develop-00339-z27` and `cms-back-release-00129-tpb`. Prefer a
reviewed forward fix after new reviewer-bearing Case drafts/plans exist; keep saved references,
published snapshots and queue history. No schema down-migration is needed.
