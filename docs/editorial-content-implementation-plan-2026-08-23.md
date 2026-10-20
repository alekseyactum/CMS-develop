# Editorial Content Implementation Plan - 2026-08-23

## Approved CMS Search And Selection Follow Up 2026-10-19

The owner approved the
[CMS publication search and selection specification](cms-publication-search-and-filter-specification-2026-10-19.md).
This is a target contract, not an implementation or deployment record. It supersedes the older
combined administrative search/filter behavior; the dated implementation sections below remain history.

CMS backend scope: independent mode semantics; saved-draft-first title/slug/lawyer-author search;
Case-only search of the deal number from administrative ERP fields on the existing page record, whose input
contract was approved on 20 October (`deals.deal_str -> CreateArticlePayload.dealNumber`);
read-only display in the `publication_meta` editor outside editable content; exact single-lawyer
and full service-tree selection; existing publication-state semantics;
server-side matching/counting before pagination and stable `createdAt desc` ordering. Reviewer and
CMS-actor roles must not be interpreted as authors, and scope/access boundaries remain unchanged.

CMS frontend scope: separate Search and Selection modes; Enter-only search; explicit Apply and immediate
Reset for filters; current-kind/current-locale scope; separate edited/applied state for each mode;
restore mode, conditions, pagination and scroll after opening a material. Pending conditions must not
leak into pagination or mode restoration. Gateways and BFF must preserve the same mode semantics.

Acceptance follows the dedicated specification. Public/site-front search, cross-kind search, automatic
search on typing, combined search-plus-filter queries and editor-layout redesign are not included.
The existing administrative page-size requirement is unchanged by this amendment. No migration,
runtime activation or deployment is authorized by this documentation task.

The owner's 20 October clarification supersedes storage in `case_summary.dealNumber`: ERP is the
source of truth and CMS keeps the last trusted value in `cms_pages.erp_deal_number`, shared through
the confirmed source identity, not in localized section content/history or public snapshots. No new
table is required: one page in the locale group stores the ERP fields and every translation resolves
that same row, including later-created translations. ERP updates preserve ordinary page audit timestamps.
Trusted ERP creation, subsequent projection updates, language-group linkage and controlled legacy
backfill still require the ERP/migrator/CMS integration and aligned integration documentation.
Changing the projection does not create a section version, invalidate SEO approval or trigger page
publication/staleness. Editor reads and number search use the local projection without synchronous
ERP availability. A manually entered `erpCaseExternalId` is not proof of source identity.
Number lookup in the editorial list must not be confused with integration lookup by
`source.system + source.dealId`. CMS Front displays the number read-only in publication metadata
without sending it in Save; absent numbers do not block editing or publication.

## Approved Follow-Up — 2026-10-16

The [current editorial specification](editorial-content-specification-2026-08-23.md) adds Blog FAQ and
Blog-only aside recommendations. The [lawyer page specification](lawyer-page-structure-2026-06-18.md)
also caps its entire publications block at five cards. The backend changes are implemented and deployed
to develop and release; frontend integration remains a separate task. The dated August implementation
status below remains historical. See the [rollout record](blog-faq-recommendations-rollout-2026-10-16.md).

Backend scope:

- add optional page-owned Blog FAQ, validation, stable item identities, preview/exact-publication support,
  one generated TOC entry and the subordinate FAQ graph;
- add saved automatic/manual recommendation settings and resolved Blog cards, exact-locale eligibility,
  thematic ranking, deterministic top three and manual order without automatic supplementation;
- add the narrow published-only recommendation refresh consumer and new-candidate discovery; preserve
  owner drafts, FAQ/body and saved-but-unpublished selection settings, and prevent refresh loops;
- cap lawyer publications at five consistently across preview, page publication and scoped refresh;
- verify legacy snapshots and additive authoring initialization without rewriting or auto-publishing them.

CMS frontend scope: FAQ editor and normal history/save flow; auto/manual Blog selector with order and
backend diagnostics; generated recommendation inspection. Page-owned sections activate with the page.

Site frontend scope: FAQ within the same server-rendered article after its body; recommendations in an
aside using returned cards; no extra lawyer cards or embedded pagination beyond the five-card list.
The existing full collection pagination remains independent.

Acceptance follows the new specification, including empty/disabled states, locale isolation, more than
three/five eligible candidates, published-only refresh, draft preservation, no-op/loop prevention and
desktop/mobile rendering. Existing imported FAQ text is converted only through an explicit content task.
Content conversion and adoption by existing published snapshots remain separate from this backend rollout.

### Backend deployment — 2026-10-16

The backend now contains the FAQ schema, safe
answer contract, TOC/graph integration, recommendation configuration/resolver and narrow stale-refresh
consumer, exact source-scope freshness checks, and five-card lawyer limit. The implementation contract
is `cms-back/docs/blog-faq-recommendations.md`. Commits `27cb406` (develop) and `0444045` (release)
were pushed and deployed through the normal pipelines; both new revisions receive all service traffic.

Legacy articles lacking an immutable card capture are temporarily omitted with a diagnostic (before
the selector limit), while corrupt existing captures remain errors. This permits initial adoption
without bulk-republication or mutually blocked automatic selections. No new DB migration or runtime
flag is introduced. Deployment does not rewrite existing snapshots. New sections enter an article's
published snapshot through normal page publication; frontend integration remains separate.
Release keeps its already-enabled scheduled refresh; develop keeps its worker and commands disabled.
The existing JSON-LD page-type allowlists still exclude Blog in both environments.

Lifecycle boundary: there is currently no native page unpublish/archive command. Recommendation
discovery/refresh accepts removal events, but a future command or authorized maintenance removal must
capture the editorial BEFORE -> null event transactionally. Direct SQL removal is not a scheduled
change-capture mechanism; this implementation does not add a new removal workflow.

Verification: builds passed in both branches. Develop: full suite 3205 passed, zero failures, one
existing optional MySQL diagnostics test skipped; 182 focused tests passed after push. Release: full
suite 3187 passed, zero failures, the same optional test skipped; 176 focused tests passed after push.
Both deployed health/readiness endpoints passed with the expected source/build and database readiness.
Release schema and refresh-summary reads passed, including the three new Blog slots and a healthy
scheduler heartbeat. Develop admin reads returned the existing operator-membership restriction
`CMS_USER_NOT_FOUND`; no access was changed. Dedicated live MySQL query/concurrency/load checks and
frontend/browser acceptance remain outside this rollout.

## Implementation status - 2026-08-23

The first backend convergence slice is implemented on `codex/editorial-content-v1`: finalized metadata,
legacy read compatibility, public privacy normalization, the closed typed block registry, common
Blog/Media/Case locale-family creation, projection fields for cover alt and primary service relation, and
ordered JSON-LD authors. The work remains unmerged and does not include legacy-content migration, public
collection pagination/refresh, the CMS typed editor, or site renderers.

The common backend foundation now also preserves the existing public editorial date when a legacy snapshot
without editor-owned `publishedAt` is republished for technical reasons. Such a republish does not create a
false material change or advance `contentModifiedAt`.

Normative product contract:

- [`editorial-content-specification-2026-08-23.md`](editorial-content-specification-2026-08-23.md)

Baseline gap audit:

- [`editorial-content-gap-audit-2026-08-23.md`](editorial-content-gap-audit-2026-08-23.md)

The June 2026 documents describe the original backend foundation. This plan is the current delivery order
for converging the existing implementation with the finalized product contract.

## Working Rules

- Preserve the existing page/section/snapshot lifecycle as the only source of truth.
- Treat projection tables as rebuildable published read models, never as draft/body ownership.
- Complete one vertical slice before expanding the shared mechanism to all kinds.
- Update backend contracts and documentation together.
- Do not include legacy-content migration in these slices.
- Do not modify or publish `cms-front` code as part of backend work unless separately authorized.

## Phase 0 - Baseline And Contract Gap Audit

Verify the current deployed and repository state before implementation:

- six page types and their schemas;
- section registries and current validators;
- projection tables and publish/rollback hooks;
- editorial admin facade;
- CMS navigation/list/editor implementation;
- site-front detail and collection renderers;
- JSON-LD output and public route handling.

Produce a gap checklist against the normative specification. Existing scaffolding is not proof of complete
functional behavior.

The repository baseline and prioritized findings are recorded in
[`editorial-content-gap-audit-2026-08-23.md`](editorial-content-gap-audit-2026-08-23.md).

Exit criteria:

- every required change is assigned to backend, CMS frontend, or site frontend;
- no implementation slice relies on an outdated June contract.

## Phase 1 - Common Backend Foundation

Complete or correct:

- `publication_meta` common fields and kind-specific branches;
- ordered author/reviewer relations with the five-author limit;
- normalized unlimited service-tree chains with one primary relation;
- the closed V1 block registry and typed per-block validation;
- stable block IDs and heading anchors;
- TOC configuration and diagnostics;
- optional fixed `editorial_cta`;
- agreed blocking-error and warning boundary;
- locale-family creation/copy rules;
- public date semantics;
- public route, canonical, and exact locale-switch contracts.

Database work must be additive and migration-safe. Existing published snapshots must not be silently
rewritten by a schema migration.

Required tests:

- pure validators for every block type;
- contributor limits/order/duplicates;
- service-tree membership, primary relation, and duplicates;
- media-mode conditional validation;
- locale creation and Ukrainian-first publication gate;
- stable anchors and deterministic serialization;
- material-change date behavior.

Exit criteria:

- backend DTOs fully describe the editor without frontend rule inference;
- preview and publish share the same validation semantics;
- existing publication projections can be rebuilt deterministically.

## Phase 2 - Blog Vertical Slice

Backend:

- finalize `blog_page` schema;
- implement corporate Actum author fallback and optional reviewer;
- implement Blog TOC rules;
- build Blog projection/card output;
- build Blog JSON-LD.

CMS frontend handoff:

- Blog list with agreed search/filter/sort/pagination;
- dedicated publication editor;
- author/reviewer and service-tree selectors;
- typed block editor;
- validation, preview, history, and publication actions.

Site frontend handoff:

- render public intro, TOC, V1 blocks, CTA, and runtime relations;
- render BlogPosting JSON-LD returned by backend;
- render Blog card and placeholder cover.

Exit criteria:

- one Ukrainian Blog page can be created, saved, validated, previewed, published, rendered, revised, and
  rolled back;
- one translation can be created and independently published after Ukrainian;
- public and preview results match except for expected lifecycle metadata.

## Phase 3 - Media Extension

Implement both explicit modes:

- `actum_article`;
- `external_reference`.

Required behavior:

- mode is never inferred;
- conditional field validation is backend-owned;
- external original authorship is not assigned to Actum;
- external-reference TOC is forced off;
- original source link is the primary public action;
- empty external-reference builder is valid without warning;
- card attribution and JSON-LD differ correctly by mode.

Exit criteria:

- both modes pass full create-to-publish and rollback smoke tests;
- frontend renders each mode without branching on accidental field presence.

## Phase 4 - Case Extension

Complete:

- Actum Organization authorship when no lawyers are selected, or one explicit primary lawyer and up to four co-authors;
- optional ERP case relation;
- typed `case_summary`;
- optional body/TOC/CTA;
- case card attribution and result label;
- Article plus stable case-matter Thing JSON-LD.

Exit criteria:

- a minimal case with `case_summary` and an empty builder publishes with warnings only where specified;
- a long-form case uses the same builder as Blog and Media;
- lawyer order and case structured data remain stable after rollback.

## Phase 5 - Collections And Automatic Refresh

For each kind:

- finalize `seo + collection_header + editorial_listing`;
- return the agreed card contract;
- implement featured-first deterministic ordering;
- implement 12-item server pagination;
- return pagination metadata and current-page ItemList JSON-LD;
- implement independent collection preview/publication;
- implement technical refresh after detail publish/rollback/archive;
- preserve old live collection and expose stale/error state when refresh fails.

CMS list screens keep their separate 50-item administrative pagination.

Exit criteria:

- drafts and unpublished locale variants never enter public collections;
- featured cards appear only on the first public page and are not duplicated;
- out-of-range pages return 404;
- technical refresh does not alter collection SEO/header or public material dates;
- unpublished collections are never auto-published.

## Phase 6 - Archive And Unpublish

Deliver as a separately reviewable slice:

- permission model;
- archive/unpublish and restore lifecycle;
- public pointer and projection removal;
- automatic collection refresh;
- 410 behavior;
- audit/history preservation;
- hard delete only for eligible never-published drafts.

This phase does not block the initial Blog vertical slice.

## Phase 7 - Hardening And Acceptance

Contract verification:

- OpenAPI/DTO examples for all editable and runtime sections;
- preview versus published payload fixtures;
- JSON-LD fixtures for Blog, both Media modes, Case, and collections;
- exact route and locale-alternate fixtures.

Integration tests:

- publish and rollback projection rebuild;
- automatic collection refresh and failure recovery;
- stale diagnostics;
- pagination and deterministic ordering;
- invalid reference and media rejection;
- authorization and audit events.

Manual end-to-end matrix:

- Ukrainian, Russian, and English lifecycle;
- empty and rich builders;
- all V1 block types;
- warning-only publication;
- blocking validation;
- missing-cover placeholder;
- corporate author fallback;
- selected reviewer;
- multiple service-tree chains;
- both media modes;
- minimal and long-form cases;
- page 1/page 2 collection navigation without JavaScript.

## Explicit Follow-Up Specifications

Do not absorb these into the implementation opportunistically:

- legacy content migration and redirects: the separate
  [2026-09-13 redirect specification](redirects-specification-2026-09-13.md) now defines the redirect
  mechanism, external map-preparation tool, and staged implementation; it does not migrate content;
- public tags, filters, and search;
- new builder block families;
- slug-change workflow;
- mixed editorial collection;
- recommendation algorithms beyond the approved Blog auto/manual rules above.
